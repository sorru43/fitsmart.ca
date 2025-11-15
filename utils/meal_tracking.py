#!/usr/bin/env python3
"""
Meal Tracking System for FitSmart
Handles meal counting, delivery tracking, and payment reminders
"""

from datetime import datetime, timedelta, date
from database.models import Subscription, Delivery, SkippedDelivery, Holiday, db
from database.models import SubscriptionStatus, DeliveryStatus
from flask import current_app
import json
import logging

logger = logging.getLogger(__name__)

class MealTracker:
    """Comprehensive meal tracking system"""
    
    @staticmethod
    def calculate_meals_promised(subscription):
        """
        Calculate total meals promised for current subscription period
        
        Args:
            subscription: Subscription object
            
        Returns:
            dict: {
                'meals_per_day': int,
                'delivery_days_per_week': int,
                'total_meals_weekly': int,
                'total_meals_monthly': int,
                'current_period_meals': int
            }
        """
        try:
            # Count meals per day
            meals_per_day = 0
            if subscription.meal_plan.includes_breakfast:
                meals_per_day += 1
            if subscription.meal_plan.includes_lunch:
                meals_per_day += 1
            if subscription.meal_plan.includes_dinner:
                meals_per_day += 1
            if subscription.meal_plan.includes_snacks:
                meals_per_day += 1
            
            # Get delivery days
            delivery_days = subscription.get_delivery_days_list()
            delivery_days_per_week = len(delivery_days)
            
            # Calculate weekly and monthly meals
            total_meals_weekly = meals_per_day * delivery_days_per_week
            total_meals_monthly = total_meals_weekly * 4  # 4 weeks per month
            
            # Calculate current period meals based on frequency
            if subscription.frequency.value == 'weekly':
                current_period_meals = total_meals_weekly
            else:  # monthly
                current_period_meals = total_meals_monthly
            
            return {
                'meals_per_day': meals_per_day,
                'delivery_days_per_week': delivery_days_per_week,
                'total_meals_weekly': total_meals_weekly,
                'total_meals_monthly': total_meals_monthly,
                'current_period_meals': current_period_meals
            }
            
        except Exception as e:
            logger.error(f"Error calculating meals promised for subscription {subscription.id}: {str(e)}")
            return {
                'meals_per_day': 0,
                'delivery_days_per_week': 5,
                'total_meals_weekly': 0,
                'total_meals_monthly': 0,
                'current_period_meals': 0
            }
    
    @staticmethod
    def count_delivered_meals(subscription, start_date=None, end_date=None):
        """
        Count meals actually delivered for a subscription period
        
        Args:
            subscription: Subscription object
            start_date: Start date for counting (default: current_period_start)
            end_date: End date for counting (default: current_period_end)
            
        Returns:
            int: Number of meals delivered
        """
        try:
            if not start_date:
                start_date = subscription.current_period_start
            if not end_date:
                end_date = subscription.current_period_end
            
            if not start_date or not end_date:
                return 0
            
            # Get all deliveries in the period
            deliveries = Delivery.query.filter(
                Delivery.subscription_id == subscription.id,
                Delivery.delivery_date >= start_date.date(),
                Delivery.delivery_date <= end_date.date(),
                Delivery.status == DeliveryStatus.DELIVERED
            ).all()
            
            # Count meals per delivery
            total_meals = 0
            for delivery in deliveries:
                meals_this_delivery = 0
                if subscription.meal_plan.includes_breakfast:
                    meals_this_delivery += 1
                if subscription.meal_plan.includes_lunch:
                    meals_this_delivery += 1
                if subscription.meal_plan.includes_dinner:
                    meals_this_delivery += 1
                if subscription.meal_plan.includes_snacks:
                    meals_this_delivery += 1
                total_meals += meals_this_delivery
            
            return total_meals
            
        except Exception as e:
            logger.error(f"Error counting delivered meals for subscription {subscription.id}: {str(e)}")
            return 0
    
    @staticmethod
    def count_skipped_meals(subscription, start_date=None, end_date=None):
        """
        Count meals skipped in a period
        
        Args:
            subscription: Subscription object
            start_date: Start date for counting
            end_date: End date for counting
            
        Returns:
            int: Number of meals skipped
        """
        try:
            if not start_date:
                start_date = subscription.current_period_start
            if not end_date:
                end_date = subscription.current_period_end
            
            if not start_date or not end_date:
                return 0
            
            # Get skipped deliveries
            skipped_deliveries = SkippedDelivery.query.filter(
                SkippedDelivery.subscription_id == subscription.id,
                SkippedDelivery.delivery_date >= start_date.date(),
                SkippedDelivery.delivery_date <= end_date.date()
            ).all()
            
            # Count meals per skipped delivery
            total_skipped = 0
            for skipped in skipped_deliveries:
                meals_this_delivery = 0
                if subscription.meal_plan.includes_breakfast:
                    meals_this_delivery += 1
                if subscription.meal_plan.includes_lunch:
                    meals_this_delivery += 1
                if subscription.meal_plan.includes_dinner:
                    meals_this_delivery += 1
                if subscription.meal_plan.includes_snacks:
                    meals_this_delivery += 1
                total_skipped += meals_this_delivery
            
            return total_skipped
            
        except Exception as e:
            logger.error(f"Error counting skipped meals for subscription {subscription.id}: {str(e)}")
            return 0
    
    @staticmethod
    def get_meal_status(subscription):
        """
        Get comprehensive meal status for a subscription
        
        Args:
            subscription: Subscription object
            
        Returns:
            dict: Complete meal status information
        """
        try:
            # Calculate promised meals
            meal_calc = MealTracker.calculate_meals_promised(subscription)
            
            # Count delivered and skipped meals
            delivered_meals = MealTracker.count_delivered_meals(subscription)
            skipped_meals = MealTracker.count_skipped_meals(subscription)
            
            # Calculate remaining meals
            remaining_meals = max(0, meal_calc['current_period_meals'] - delivered_meals)
            
            # Check if period is complete
            is_period_complete = remaining_meals <= 0
            
            # Calculate completion percentage
            if meal_calc['current_period_meals'] > 0:
                completion_percentage = (delivered_meals / meal_calc['current_period_meals']) * 100
            else:
                completion_percentage = 0
            
            return {
                'subscription_id': subscription.id,
                'promised_meals': meal_calc['current_period_meals'],
                'delivered_meals': delivered_meals,
                'skipped_meals': skipped_meals,
                'remaining_meals': remaining_meals,
                'completion_percentage': round(completion_percentage, 2),
                'is_period_complete': is_period_complete,
                'needs_renewal': is_period_complete and subscription.status == SubscriptionStatus.ACTIVE,
                'meal_calculation': meal_calc
            }
            
        except Exception as e:
            logger.error(f"Error getting meal status for subscription {subscription.id}: {str(e)}")
            return {
                'subscription_id': subscription.id,
                'promised_meals': 0,
                'delivered_meals': 0,
                'skipped_meals': 0,
                'remaining_meals': 0,
                'completion_percentage': 0,
                'is_period_complete': False,
                'needs_renewal': False,
                'meal_calculation': {}
            }
    
    @staticmethod
    def record_meal_delivery(subscription, delivery_date):
        """
        Record a meal delivery and update subscription status
        
        Args:
            subscription: Subscription object
            delivery_date: Date of delivery
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create or update delivery record
            delivery = Delivery.query.filter_by(
                subscription_id=subscription.id,
                delivery_date=delivery_date
            ).first()
            
            if not delivery:
                delivery = Delivery(
                    subscription_id=subscription.id,
                    delivery_date=delivery_date,
                    status=DeliveryStatus.DELIVERED
                )
                db.session.add(delivery)
            else:
                delivery.status = DeliveryStatus.DELIVERED
            
            # Update meal counts in subscription
            meal_status = MealTracker.get_meal_status(subscription)
            
            # Update subscription with meal tracking data
            if not hasattr(subscription, 'meals_delivered_this_period'):
                # Add meal tracking fields if they don't exist
                subscription.meals_delivered_this_period = meal_status['delivered_meals']
                subscription.meals_remaining_this_period = meal_status['remaining_meals']
                subscription.total_meals_promised_this_period = meal_status['promised_meals']
            else:
                subscription.meals_delivered_this_period = meal_status['delivered_meals']
                subscription.meals_remaining_this_period = meal_status['remaining_meals']
            
            # Check if period is complete and trigger renewal
            if meal_status['is_period_complete']:
                MealTracker.trigger_renewal_reminder(subscription)
            
            db.session.commit()
            logger.info(f"Recorded meal delivery for subscription {subscription.id} on {delivery_date}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error recording meal delivery for subscription {subscription.id}: {str(e)}")
            return False
    
    @staticmethod
    def trigger_renewal_reminder(subscription):
        """
        Trigger payment reminder when subscription period is complete
        
        Args:
            subscription: Subscription object
        """
        try:
            # Check if reminder already sent
            if hasattr(subscription, 'payment_reminder_sent') and subscription.payment_reminder_sent:
                return
            
            # Set next payment date
            if subscription.frequency.value == 'weekly':
                next_payment_date = datetime.now() + timedelta(days=7)
            else:
                next_payment_date = datetime.now() + timedelta(days=30)
            
            # Update subscription
            if hasattr(subscription, 'next_payment_date'):
                subscription.next_payment_date = next_payment_date
                subscription.payment_reminder_sent = True
                subscription.last_payment_reminder_date = datetime.now()
            
            # Send payment reminder email
            try:
                from utils.email_functions import send_payment_reminder_email
                send_payment_reminder_email(subscription)
                logger.info(f"Payment reminder sent for subscription {subscription.id}")
            except Exception as e:
                logger.error(f"Failed to send payment reminder for subscription {subscription.id}: {str(e)}")
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error triggering renewal reminder for subscription {subscription.id}: {str(e)}")
    
    @staticmethod
    def handle_skip_compensation(subscription, skipped_delivery_date):
        """
        Handle compensation for skipped deliveries
        
        Args:
            subscription: Subscription object
            skipped_delivery_date: Date of skipped delivery
            
        Returns:
            dict: Compensation details
        """
        try:
            # Calculate compensation
            compensation = {
                'type': 'extend_subscription',
                'days_extended': 0,
                'description': 'No compensation needed'
            }
            
            if subscription.frequency.value == 'weekly':
                compensation['days_extended'] = 1
                compensation['description'] = 'Subscription extended by 1 day for skipped delivery'
            elif subscription.frequency.value == 'monthly':
                delivery_days_per_month = len(subscription.get_delivery_days_list()) * 4
                if delivery_days_per_month > 0:
                    days_per_delivery = 30 / delivery_days_per_month
                    compensation['days_extended'] = max(1, int(days_per_delivery))
                    compensation['description'] = f'Monthly subscription extended by {compensation["days_extended"]} days for skipped delivery'
            
            # Apply compensation
            if compensation['days_extended'] > 0:
                if subscription.current_period_end:
                    subscription.current_period_end += timedelta(days=compensation['days_extended'])
                
                # Recalculate meal allocation for extended period
                meal_status = MealTracker.get_meal_status(subscription)
                if hasattr(subscription, 'total_meals_promised_this_period'):
                    subscription.total_meals_promised_this_period = meal_status['promised_meals']
                    subscription.meals_remaining_this_period = meal_status['remaining_meals']
            
            db.session.commit()
            return compensation
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error handling skip compensation for subscription {subscription.id}: {str(e)}")
            return {'type': 'error', 'description': str(e)}
    
    @staticmethod
    def check_holiday_protection(subscription, delivery_date):
        """
        Check if meals are protected during holidays
        
        Args:
            subscription: Subscription object
            delivery_date: Date to check
            
        Returns:
            bool: True if meals are protected, False otherwise
        """
        try:
            # Check for active holiday
            current_holiday = Holiday.query.filter(
                Holiday.is_active == True,
                Holiday.start_date <= delivery_date,
                Holiday.end_date >= delivery_date
            ).first()
            
            if current_holiday and current_holiday.protect_meals:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking holiday protection: {str(e)}")
            return False
    
    @staticmethod
    def get_subscriptions_needing_renewal():
        """
        Get all subscriptions that need renewal
        
        Returns:
            list: List of subscription IDs needing renewal
        """
        try:
            subscriptions = Subscription.query.filter_by(
                status=SubscriptionStatus.ACTIVE
            ).all()
            
            needs_renewal = []
            for subscription in subscriptions:
                meal_status = MealTracker.get_meal_status(subscription)
                if meal_status['needs_renewal']:
                    needs_renewal.append(subscription.id)
            
            return needs_renewal
            
        except Exception as e:
            logger.error(f"Error getting subscriptions needing renewal: {str(e)}")
            return []
    
    @staticmethod
    def update_all_subscription_meal_counts():
        """
        Update meal counts for all active subscriptions
        Useful for maintenance and data consistency
        """
        try:
            subscriptions = Subscription.query.filter_by(
                status=SubscriptionStatus.ACTIVE
            ).all()
            
            updated_count = 0
            for subscription in subscriptions:
                meal_status = MealTracker.get_meal_status(subscription)
                
                # Update subscription with current meal data
                if hasattr(subscription, 'meals_delivered_this_period'):
                    subscription.meals_delivered_this_period = meal_status['delivered_meals']
                    subscription.meals_remaining_this_period = meal_status['remaining_meals']
                    subscription.total_meals_promised_this_period = meal_status['promised_meals']
                    updated_count += 1
            
            db.session.commit()
            logger.info(f"Updated meal counts for {updated_count} subscriptions")
            return updated_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating subscription meal counts: {str(e)}")
            return 0
