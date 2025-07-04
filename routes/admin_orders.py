#!/usr/bin/env python3
"""
Admin orders and subscriptions management routes
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from database.models import Order, Subscription, User, MealPlan, SubscriptionStatus, SubscriptionFrequency
from functools import wraps
from flask import abort
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import json

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

admin_orders_bp = Blueprint('admin_orders', __name__, url_prefix='/admin')

@admin_orders_bp.route('/orders')
@login_required
@admin_required
def orders_dashboard():
    """Admin orders dashboard"""
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        payment_status_filter = request.args.get('payment_status', 'all')
        date_filter = request.args.get('date_range', '30')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Build query
        query = Order.query.join(User).join(MealPlan)
        
        # Apply filters
        if status_filter != 'all':
            query = query.filter(Order.status == status_filter)
        
        if payment_status_filter != 'all':
            query = query.filter(Order.payment_status == payment_status_filter)
        
        if date_filter != 'all':
            days_ago = int(date_filter)
            start_date = datetime.now() - timedelta(days=days_ago)
            query = query.filter(Order.created_at >= start_date)
        
        # Get paginated results
        orders = query.order_by(desc(Order.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics
        total_orders = Order.query.count()
        completed_orders = Order.query.filter_by(payment_status='completed').count()
        pending_orders = Order.query.filter_by(payment_status='pending').count()
        failed_orders = Order.query.filter_by(payment_status='failed').count()
        
        total_revenue = Order.query.filter_by(payment_status='completed').with_entities(
            func.sum(Order.amount)
        ).scalar() or 0
        
        # Recent orders for quick view
        recent_orders = Order.query.join(User).join(MealPlan).order_by(
            desc(Order.created_at)
        ).limit(5).all()
        
        stats = {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'failed_orders': failed_orders,
            'total_revenue': total_revenue,
            'success_rate': round((completed_orders / total_orders * 100) if total_orders > 0 else 0, 1)
        }
        
        return render_template('admin/orders_dashboard.html',
                             orders=orders,
                             recent_orders=recent_orders,
                             stats=stats,
                             status_filter=status_filter,
                             payment_status_filter=payment_status_filter,
                             date_filter=date_filter)
        
    except Exception as e:
        current_app.logger.error(f"Error in orders dashboard: {str(e)}")
        flash('Error loading orders dashboard', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_orders_bp.route('/subscriptions')
@login_required
@admin_required
def subscriptions_dashboard():
    """Admin subscriptions dashboard"""
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        frequency_filter = request.args.get('frequency', 'all')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Build query
        query = Subscription.query.join(User).join(MealPlan)
        
        # Apply filters
        if status_filter != 'all':
            if status_filter == 'ACTIVE':
                query = query.filter(Subscription.status == SubscriptionStatus.ACTIVE)
            elif status_filter == 'PAUSED':
                query = query.filter(Subscription.status == SubscriptionStatus.PAUSED)
            elif status_filter == 'CANCELED':
                query = query.filter(Subscription.status == SubscriptionStatus.CANCELED)
            elif status_filter == 'EXPIRED':
                query = query.filter(Subscription.status == SubscriptionStatus.EXPIRED)
        
        if frequency_filter != 'all':
            if frequency_filter == 'WEEKLY':
                query = query.filter(Subscription.frequency == SubscriptionFrequency.WEEKLY)
            elif frequency_filter == 'MONTHLY':
                query = query.filter(Subscription.frequency == SubscriptionFrequency.MONTHLY)
        
        # Get paginated results
        subscriptions = query.order_by(desc(Subscription.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics
        total_subscriptions = Subscription.query.count()
        active_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).count()
        paused_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.PAUSED).count()
        canceled_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.CANCELED).count()
        
        monthly_revenue = Subscription.query.filter_by(
            status=SubscriptionStatus.ACTIVE,
            frequency=SubscriptionFrequency.MONTHLY
        ).with_entities(func.sum(Subscription.price)).scalar() or 0
        
        weekly_revenue = Subscription.query.filter_by(
            status=SubscriptionStatus.ACTIVE,
            frequency=SubscriptionFrequency.WEEKLY
        ).with_entities(func.sum(Subscription.price)).scalar() or 0
        
        # Recent subscriptions
        recent_subscriptions = Subscription.query.join(User).join(MealPlan).order_by(
            desc(Subscription.created_at)
        ).limit(5).all()
        
        stats = {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'paused_subscriptions': paused_subscriptions,
            'canceled_subscriptions': canceled_subscriptions,
            'monthly_revenue': monthly_revenue,
            'weekly_revenue': weekly_revenue,
            'total_recurring_revenue': monthly_revenue + (weekly_revenue * 4),
            'retention_rate': round((active_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0, 1)
        }
        
        return render_template('admin/subscriptions_dashboard.html',
                             subscriptions=subscriptions,
                             recent_subscriptions=recent_subscriptions,
                             stats=stats,
                             status_filter=status_filter,
                             frequency_filter=frequency_filter)
        
    except Exception as e:
        current_app.logger.error(f"Error in subscriptions dashboard: {str(e)}")
        flash('Error loading subscriptions dashboard', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_orders_bp.route('/order/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    """View detailed order information"""
    try:
        order = Order.query.get_or_404(order_id)
        
        # Get related subscriptions
        related_subscriptions = order.subscriptions
        
        return render_template('admin/order_detail.html',
                             order=order,
                             related_subscriptions=related_subscriptions)
        
    except Exception as e:
        current_app.logger.error(f"Error loading order detail: {str(e)}")
        flash('Error loading order details', 'error')
        return redirect(url_for('admin_orders.orders_dashboard'))

@admin_orders_bp.route('/subscription/<int:subscription_id>')
@login_required
@admin_required
def subscription_detail(subscription_id):
    """View detailed subscription information"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        
        # Get related orders
        related_orders = Order.query.join(Order.subscriptions).filter(
            Subscription.id == subscription_id
        ).order_by(desc(Order.created_at)).all()
        
        return render_template('admin/subscription_detail.html',
                             subscription=subscription,
                             related_orders=related_orders)
        
    except Exception as e:
        current_app.logger.error(f"Error loading subscription detail: {str(e)}")
        flash('Error loading subscription details', 'error')
        return redirect(url_for('admin_orders.subscriptions_dashboard'))

@admin_orders_bp.route('/update_order_status', methods=['POST'])
@login_required
@admin_required
def update_order_status():
    """Update order status"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        new_status = data.get('status')
        payment_status = data.get('payment_status')
        
        order = Order.query.get_or_404(order_id)
        
        if new_status:
            order.status = new_status
        
        if payment_status:
            order.payment_status = payment_status
        
        order.updated_at = datetime.now()
        
        from app import db
        db.session.commit()
        
        current_app.logger.info(f"Order {order_id} status updated by admin {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating order status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error updating order status'
        }), 500

@admin_orders_bp.route('/update_subscription_status', methods=['POST'])
@login_required
@admin_required
def update_subscription_status():
    """Update subscription status"""
    try:
        data = request.get_json()
        subscription_id = data.get('subscription_id')
        new_status = data.get('status')
        
        subscription = Subscription.query.get_or_404(subscription_id)
        
        if new_status == 'ACTIVE':
            subscription.status = SubscriptionStatus.ACTIVE
        elif new_status == 'PAUSED':
            subscription.status = SubscriptionStatus.PAUSED
        elif new_status == 'CANCELED':
            subscription.status = SubscriptionStatus.CANCELED
        elif new_status == 'EXPIRED':
            subscription.status = SubscriptionStatus.EXPIRED
        
        subscription.updated_at = datetime.now()
        
        from app import db
        db.session.commit()
        
        current_app.logger.info(f"Subscription {subscription_id} status updated by admin {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Subscription status updated successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating subscription status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error updating subscription status'
        }), 500 