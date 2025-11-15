#!/usr/bin/env python3
"""
Admin routes for subscription management
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from database.models import db, Subscription, User, Order, SubscriptionStatus, SubscriptionFrequency
from utils.subscription_management import SubscriptionManager, run_subscription_maintenance
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

admin_subscription_bp = Blueprint('admin_subscription', __name__, url_prefix='/admin/subscriptions')

def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_subscription_bp.route('/')
@login_required
@admin_required
def subscription_dashboard():
    """Admin subscription dashboard"""
    try:
        # Get subscription analytics
        analytics = SubscriptionManager.get_revenue_analytics()
        
        # Get status summary
        status_summary = SubscriptionManager.get_subscription_status_summary()
        
        # Get expiring soon
        expiring_soon = SubscriptionManager.get_expiring_soon_subscriptions(days_ahead=7)
        
        # Get recent subscriptions
        recent_subscriptions = Subscription.query.order_by(Subscription.created_at.desc()).limit(10).all()
        
        return render_template('admin/subscription_dashboard.html',
                             analytics=analytics,
                             status_summary=status_summary,
                             expiring_soon=expiring_soon,
                             recent_subscriptions=recent_subscriptions)
                             
    except Exception as e:
        logger.error(f"Error loading subscription dashboard: {str(e)}")
        flash('Error loading subscription dashboard.', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_subscription_bp.route('/list')
@login_required
@admin_required  
def subscription_list():
    """List all subscriptions with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Filter options
        status_filter = request.args.get('status')
        user_filter = request.args.get('user_id', type=int)
        
        query = Subscription.query
        
        if status_filter:
            query = query.filter(Subscription.status == SubscriptionStatus(status_filter))
        
        if user_filter:
            query = query.filter(Subscription.user_id == user_filter)
        
        subscriptions = query.order_by(Subscription.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/subscription_list.html',
                             subscriptions=subscriptions,
                             status_filter=status_filter,
                             user_filter=user_filter)
                             
    except Exception as e:
        logger.error(f"Error loading subscription list: {str(e)}")
        flash('Error loading subscription list.', 'error')
        return redirect(url_for('admin_subscription.subscription_dashboard'))

@admin_subscription_bp.route('/<int:subscription_id>')
@login_required
@admin_required
def subscription_detail(subscription_id):
    """View subscription details"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        
        # Get related orders
        orders = Order.query.filter_by(user_id=subscription.user_id, 
                                     meal_plan_id=subscription.meal_plan_id).order_by(Order.created_at.desc()).all()
        
        # Get user's other subscriptions
        other_subscriptions = Subscription.query.filter(
            Subscription.user_id == subscription.user_id,
            Subscription.id != subscription_id
        ).all()
        
        return render_template('admin/subscription_detail.html',
                             subscription=subscription,
                             orders=orders,
                             other_subscriptions=other_subscriptions)
                             
    except Exception as e:
        logger.error(f"Error loading subscription {subscription_id}: {str(e)}")
        flash('Error loading subscription details.', 'error')
        return redirect(url_for('admin_subscription.subscription_list'))

@admin_subscription_bp.route('/<int:subscription_id>/pause', methods=['POST'])
@login_required
@admin_required
def pause_subscription(subscription_id):
    """Pause a subscription"""
    try:
        reason = request.form.get('reason', 'Admin action')
        success, message = SubscriptionManager.pause_subscription(subscription_id, reason)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        logger.error(f"Error pausing subscription {subscription_id}: {str(e)}")
        flash('Error pausing subscription.', 'error')
    
    return redirect(url_for('admin_subscription.subscription_detail', subscription_id=subscription_id))

@admin_subscription_bp.route('/<int:subscription_id>/resume', methods=['POST'])
@login_required
@admin_required
def resume_subscription(subscription_id):
    """Resume a paused subscription"""
    try:
        success, message = SubscriptionManager.resume_subscription(subscription_id)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        logger.error(f"Error resuming subscription {subscription_id}: {str(e)}")
        flash('Error resuming subscription.', 'error')
    
    return redirect(url_for('admin_subscription.subscription_detail', subscription_id=subscription_id))

@admin_subscription_bp.route('/<int:subscription_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        reason = request.form.get('reason', 'Admin action')
        immediate = request.form.get('immediate', 'false') == 'true'
        
        success, message = SubscriptionManager.cancel_subscription(subscription_id, reason, immediate)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        logger.error(f"Error cancelling subscription {subscription_id}: {str(e)}")
        flash('Error cancelling subscription.', 'error')
    
    return redirect(url_for('admin_subscription.subscription_detail', subscription_id=subscription_id))

@admin_subscription_bp.route('/<int:subscription_id>/renew', methods=['POST'])
@login_required
@admin_required
def renew_subscription(subscription_id):
    """Manually renew a subscription"""
    try:
        payment_id = f"admin_renewal_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        order_id = f"admin_order_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        success, message = SubscriptionManager.renew_subscription(subscription_id, payment_id, order_id)
        
        if success:
            flash(f'Subscription renewed successfully: {message}', 'success')
        else:
            flash(f'Error renewing subscription: {message}', 'error')
            
    except Exception as e:
        logger.error(f"Error renewing subscription {subscription_id}: {str(e)}")
        flash('Error renewing subscription.', 'error')
    
    return redirect(url_for('admin_subscription.subscription_detail', subscription_id=subscription_id))

@admin_subscription_bp.route('/maintenance/run', methods=['POST'])
@login_required
@admin_required
def run_maintenance():
    """Run subscription maintenance tasks"""
    try:
        result = run_subscription_maintenance()
        
        if 'error' in result:
            flash(f'Maintenance error: {result["error"]}', 'error')
        else:
            flash(f'Maintenance completed: {result["expired_count"]} expired, {result["expiring_soon_count"]} expiring soon', 'success')
            
    except Exception as e:
        logger.error(f"Error running subscription maintenance: {str(e)}")
        flash('Error running subscription maintenance.', 'error')
    
    return redirect(url_for('admin_subscription.subscription_dashboard'))

@admin_subscription_bp.route('/analytics/api')
@login_required
@admin_required
def analytics_api():
    """API endpoint for subscription analytics"""
    try:
        analytics = SubscriptionManager.get_revenue_analytics()
        status_summary = SubscriptionManager.get_subscription_status_summary()
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'status_summary': status_summary
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_subscription_bp.route('/export')
@login_required
@admin_required
def export_subscriptions():
    """Export subscription data as CSV"""
    try:
        import csv
        from io import StringIO
        from flask import make_response
        
        # Get all subscriptions
        subscriptions = Subscription.query.all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'User ID', 'User Email', 'Meal Plan', 'Status', 'Frequency', 
                        'Price', 'Start Date', 'Current Period End', 'Created At'])
        
        # Write data
        for sub in subscriptions:
            writer.writerow([
                sub.id,
                sub.user_id,
                sub.user.email if sub.user else 'Unknown',
                sub.meal_plan_id,
                sub.status.value if hasattr(sub.status, 'value') else str(sub.status),
                sub.frequency.value if hasattr(sub.frequency, 'value') else str(sub.frequency),
                float(sub.price),
                sub.start_date.strftime('%Y-%m-%d') if sub.start_date else '',
                sub.current_period_end.strftime('%Y-%m-%d') if sub.current_period_end else '',
                sub.created_at.strftime('%Y-%m-%d %H:%M') if sub.created_at else ''
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=subscriptions_{datetime.now().strftime("%Y%m%d")}.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting subscriptions: {str(e)}")
        flash('Error exporting subscription data.', 'error')
        return redirect(url_for('admin_subscription.subscription_dashboard')) 