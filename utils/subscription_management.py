#!/usr/bin/env python3
"""
Subscription Management System
- Track subscription expiry
- Handle renewal notifications
- Manage subscription lifecycle
"""

from datetime import datetime, timedelta
from database.models import db, Subscription, User, Order, SubscriptionStatus, SubscriptionFrequency
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class SubscriptionManager:
    """Manages subscription lifecycle, expiry, and renewals"""
    
    @staticmethod
    def check_expired_subscriptions():
        """Check for expired subscriptions and mark them as expired"""
        try:
            now = datetime.now()
            
            # Find subscriptions that have expired
            expired_subscriptions = Subscription.query.filter(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.current_period_end < now
            ).all()
            
            expired_count = 0
            for subscription in expired_subscriptions:
                logger.info(f"Expiring subscription {subscription.id} for user {subscription.user_id}")
                subscription.status = SubscriptionStatus.EXPIRED
                subscription.end_date = subscription.current_period_end
                expired_count += 1
            
            if expired_count > 0:
                db.session.commit()
                logger.info(f"Marked {expired_count} subscriptions as expired")
            
            return expired_count
            
        except Exception as e:
            logger.error(f"Error checking expired subscriptions: {str(e)}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def get_expiring_soon_subscriptions(days_ahead=3):
        """Get subscriptions expiring within specified days"""
        try:
            future_date = datetime.now() + timedelta(days=days_ahead)
            
            expiring_subscriptions = Subscription.query.filter(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.current_period_end <= future_date,
                Subscription.current_period_end > datetime.now()
            ).all()
            
            return expiring_subscriptions
            
        except Exception as e:
            logger.error(f"Error getting expiring subscriptions: {str(e)}")
            return []
    
    @staticmethod
    def renew_subscription(subscription_id, payment_id=None, order_id=None):
        """Renew a subscription for another period"""
        try:
            subscription = Subscription.query.get(subscription_id)
            if not subscription:
                return False, "Subscription not found"
            
            # Calculate new period dates
            if subscription.frequency == SubscriptionFrequency.WEEKLY:
                new_period_start = subscription.current_period_end
                new_period_end = new_period_start + timedelta(days=7)
            elif subscription.frequency == SubscriptionFrequency.MONTHLY:
                new_period_start = subscription.current_period_end
                new_period_end = new_period_start + timedelta(days=30)
            else:
                return False, "Invalid subscription frequency"
            
            # Update subscription
            subscription.current_period_start = new_period_start
            subscription.current_period_end = new_period_end
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.updated_at = datetime.now()
            
            # Create renewal order if payment details provided
            if payment_id and order_id:
                renewal_order = Order(
                    user_id=subscription.user_id,
                    meal_plan_id=subscription.meal_plan_id,
                    amount=float(subscription.price),
                    status='confirmed',
                    payment_status='captured',
                    payment_id=payment_id,
                    order_id=order_id
                )
                db.session.add(renewal_order)
                db.session.flush()
                
                # Link renewal order to subscription
                subscription.order_id = renewal_order.id
            
            db.session.commit()
            logger.info(f"Renewed subscription {subscription_id} until {new_period_end}")
            
            return True, f"Subscription renewed until {new_period_end.strftime('%Y-%m-%d')}"
            
        except Exception as e:
            logger.error(f"Error renewing subscription {subscription_id}: {str(e)}")
            db.session.rollback()
            return False, f"Error renewing subscription: {str(e)}"
    
    @staticmethod
    def get_user_active_subscriptions(user_id):
        """Get all active subscriptions for a user"""
        try:
            subscriptions = Subscription.query.filter(
                Subscription.user_id == user_id,
                Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.PAUSED])
            ).all()
            
            return subscriptions
            
        except Exception as e:
            logger.error(f"Error getting user subscriptions: {str(e)}")
            return []
    
    @staticmethod
    def get_subscription_status_summary():
        """Get summary of subscription statuses"""
        try:
            from sqlalchemy import func
            
            summary = db.session.query(
                Subscription.status,
                func.count(Subscription.id).label('count')
            ).group_by(Subscription.status).all()
            
            status_dict = {}
            for status, count in summary:
                status_dict[status.value] = count
            
            return status_dict
            
        except Exception as e:
            logger.error(f"Error getting subscription summary: {str(e)}")
            return {}
    
    @staticmethod
    def pause_subscription(subscription_id, reason=None):
        """Pause a subscription"""
        try:
            subscription = Subscription.query.get(subscription_id)
            if not subscription:
                return False, "Subscription not found"
            
            if subscription.status != SubscriptionStatus.ACTIVE:
                return False, "Only active subscriptions can be paused"
            
            subscription.status = SubscriptionStatus.PAUSED
            subscription.pause_collection = True
            subscription.updated_at = datetime.now()
            
            db.session.commit()
            logger.info(f"Paused subscription {subscription_id}. Reason: {reason}")
            
            return True, "Subscription paused successfully"
            
        except Exception as e:
            logger.error(f"Error pausing subscription {subscription_id}: {str(e)}")
            db.session.rollback()
            return False, f"Error pausing subscription: {str(e)}"
    
    @staticmethod
    def resume_subscription(subscription_id):
        """Resume a paused subscription"""
        try:
            subscription = Subscription.query.get(subscription_id)
            if not subscription:
                return False, "Subscription not found"
            
            if subscription.status != SubscriptionStatus.PAUSED:
                return False, "Only paused subscriptions can be resumed"
            
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.pause_collection = False
            subscription.updated_at = datetime.now()
            
            db.session.commit()
            logger.info(f"Resumed subscription {subscription_id}")
            
            return True, "Subscription resumed successfully"
            
        except Exception as e:
            logger.error(f"Error resuming subscription {subscription_id}: {str(e)}")
            db.session.rollback()
            return False, f"Error resuming subscription: {str(e)}"
    
    @staticmethod
    def cancel_subscription(subscription_id, reason=None, immediate=False):
        """Cancel a subscription"""
        try:
            subscription = Subscription.query.get(subscription_id)
            if not subscription:
                return False, "Subscription not found"
            
            if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.PAUSED]:
                return False, "Subscription is already cancelled or expired"
            
            if immediate:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.end_date = datetime.now()
            else:
                subscription.cancel_at_period_end = True
                # Subscription will be cancelled at the end of current period
            
            subscription.updated_at = datetime.now()
            
            db.session.commit()
            logger.info(f"Cancelled subscription {subscription_id}. Immediate: {immediate}, Reason: {reason}")
            
            if immediate:
                return True, "Subscription cancelled immediately"
            else:
                return True, f"Subscription will be cancelled at the end of current period ({subscription.current_period_end.strftime('%Y-%m-%d')})"
            
        except Exception as e:
            logger.error(f"Error cancelling subscription {subscription_id}: {str(e)}")
            db.session.rollback()
            return False, f"Error cancelling subscription: {str(e)}"
    
    @staticmethod
    def get_revenue_analytics(start_date=None, end_date=None):
        """Get subscription revenue analytics"""
        try:
            from sqlalchemy import func, extract
            
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Total active subscriptions
            active_subs = Subscription.query.filter(
                Subscription.status == SubscriptionStatus.ACTIVE
            ).count()
            
            # Monthly recurring revenue (MRR)
            monthly_revenue = db.session.query(
                func.sum(Subscription.price)
            ).filter(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.frequency == SubscriptionFrequency.MONTHLY
            ).scalar() or 0
            
            # Weekly recurring revenue converted to monthly
            weekly_revenue = db.session.query(
                func.sum(Subscription.price)
            ).filter(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.frequency == SubscriptionFrequency.WEEKLY
            ).scalar() or 0
            
            # Convert weekly to monthly (weekly * 4.33)
            weekly_to_monthly = float(weekly_revenue) * 4.33 if weekly_revenue else 0
            total_mrr = float(monthly_revenue) + weekly_to_monthly
            
            # New subscriptions this month
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            new_subs_this_month = Subscription.query.filter(
                extract('month', Subscription.created_at) == current_month,
                extract('year', Subscription.created_at) == current_year
            ).count()
            
            # Cancelled subscriptions this month
            cancelled_subs_this_month = Subscription.query.filter(
                Subscription.status == SubscriptionStatus.CANCELED,
                extract('month', Subscription.updated_at) == current_month,
                extract('year', Subscription.updated_at) == current_year
            ).count()
            
            return {
                'active_subscriptions': active_subs,
                'monthly_recurring_revenue': round(total_mrr, 2),
                'new_subscriptions_this_month': new_subs_this_month,
                'cancelled_subscriptions_this_month': cancelled_subs_this_month,
                'churn_rate': round((cancelled_subs_this_month / max(active_subs, 1)) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue analytics: {str(e)}")
            return {
                'active_subscriptions': 0,
                'monthly_recurring_revenue': 0,
                'new_subscriptions_this_month': 0,
                'cancelled_subscriptions_this_month': 0,
                'churn_rate': 0
            }

def run_subscription_maintenance():
    """Run daily subscription maintenance tasks"""
    try:
        logger.info("Starting subscription maintenance tasks...")
        
        # Check and mark expired subscriptions
        expired_count = SubscriptionManager.check_expired_subscriptions()
        
        # Get subscriptions expiring soon for notifications
        expiring_soon = SubscriptionManager.get_expiring_soon_subscriptions(days_ahead=3)
        
        # Log summary
        logger.info(f"Subscription maintenance completed:")
        logger.info(f"  - Expired: {expired_count}")
        logger.info(f"  - Expiring soon: {len(expiring_soon)}")
        
        return {
            'expired_count': expired_count,
            'expiring_soon_count': len(expiring_soon),
            'expiring_soon': [{'id': s.id, 'user_id': s.user_id, 'end_date': s.current_period_end} for s in expiring_soon]
        }
        
    except Exception as e:
        logger.error(f"Error in subscription maintenance: {str(e)}")
        return {'error': str(e)} 