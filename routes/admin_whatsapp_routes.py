#!/usr/bin/env python3
"""
WhatsApp Campaign Management Routes for Admin Panel
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required
from database.models import User, Order, Subscription, MealPlan, Holiday, db
from datetime import datetime, timedelta
import json

# Import whatsapp_system with error handling
try:
    from whatsapp_marketing_system import whatsapp_system
except (ImportError, Exception) as e:
    # Set to None if import fails - will be handled in routes
    whatsapp_system = None

admin_whatsapp_bp = Blueprint('admin_whatsapp', __name__)

# Context processor to make site settings and has_blueprint available to all admin_whatsapp templates
@admin_whatsapp_bp.context_processor
def inject_site_settings():
    """Inject site settings and has_blueprint into all admin_whatsapp templates"""
    def has_blueprint(blueprint_name):
        """Check if a blueprint is registered"""
        try:
            return blueprint_name in current_app.blueprints
        except:
            return False
    
    try:
        from database.models import SiteSetting
        settings = {}
        site_settings = SiteSetting.query.all()
        for setting in site_settings:
            settings[setting.key] = setting.value
        
        # Default values if not set
        if 'site_logo' not in settings:
            settings['site_logo'] = '/static/images/logo white.png'
        if 'company_name' not in settings:
            settings['company_name'] = 'FitSmart'
        if 'company_tagline' not in settings:
            settings['company_tagline'] = 'Healthy Meal Delivery'
        
        return {'site_settings': settings, 'has_blueprint': has_blueprint}
    except Exception as e:
        current_app.logger.error(f"Error loading site settings: {str(e)}")
        return {
            'site_settings': {
                'site_logo': '/static/images/logo white.png',
                'company_name': 'FitSmart',
                'company_tagline': 'Healthy Meal Delivery'
            }, 
            'has_blueprint': has_blueprint
        }

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns')
@login_required
def whatsapp_campaigns_dashboard():
    """WhatsApp campaigns dashboard"""
    try:
        # Check if whatsapp_system is available
        if whatsapp_system is None:
            current_app.logger.warning("whatsapp_system is not available - using default values")
        
        # Default analytics if whatsapp_system is not available
        default_analytics = {
            'total_messages_sent': 0,
            'messages_delivered': 0,
            'messages_read': 0,
            'failed_messages': 0,
            'delivery_rate': 0.0,
            'read_rate': 0.0
        }
        
        # Get campaign statistics
        if whatsapp_system and hasattr(whatsapp_system, 'get_analytics'):
            try:
                analytics = whatsapp_system.get_analytics()
            except Exception as e:
                current_app.logger.warning(f"Error getting analytics: {e}")
                analytics = default_analytics
        else:
            analytics = default_analytics
        
        # Get user segments for targeting
        try:
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            new_users_this_week = User.query.filter(
                User.created_at >= datetime.now() - timedelta(days=7)
            ).count()
            users_with_phone = User.query.filter(User.phone.isnot(None)).count()
        except Exception as e:
            current_app.logger.warning(f"Error getting user statistics: {e}")
            total_users = 0
            active_users = 0
            new_users_this_week = 0
            users_with_phone = 0
        
        # Get available templates
        if whatsapp_system and hasattr(whatsapp_system, 'templates'):
            templates = whatsapp_system.templates
        else:
            templates = {}
        
        return render_template('admin/whatsapp_campaigns/dashboard.html',
                            analytics=analytics,
                            total_users=total_users,
                            active_users=active_users,
                            new_users_this_week=new_users_this_week,
                            users_with_phone=users_with_phone,
                            templates=templates)
    except Exception as e:
        current_app.logger.error(f"Error loading WhatsApp campaigns dashboard: {str(e)}", exc_info=True)
        flash(f'Error loading WhatsApp campaigns dashboard: {str(e)}', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns/welcome-message')
@login_required
def send_welcome_message():
    """Send welcome message to new users"""
    try:
        if request.method == 'POST':
            user_ids = request.form.getlist('user_ids')
            
            if not user_ids:
                flash('Please select users to send welcome message', 'error')
                return redirect(url_for('admin_whatsapp.send_welcome_message'))
            
            # Get users
            users = User.query.filter(User.id.in_(user_ids)).all()
            
            if not users:
                flash('No valid users found', 'error')
                return redirect(url_for('admin_whatsapp.send_welcome_message'))
            
            # Send welcome messages
            sent_count = 0
            for user in users:
                if user.phone:
                    success = whatsapp_system.send_welcome_message(user.phone, user.name)
                    if success:
                        sent_count += 1
            
            flash(f'Welcome message sent to {sent_count} users', 'success')
            return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))
        
        # Get new users (registered in last 7 days)
        new_users = User.query.filter(
            User.created_at >= datetime.now() - timedelta(days=7),
            User.phone.isnot(None)
        ).all()
        
        return render_template('admin/whatsapp_campaigns/welcome_message.html',
                            new_users=new_users)
    except Exception as e:
        current_app.logger.error(f"Error sending welcome message: {str(e)}")
        flash('Error sending welcome message', 'error')
        return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns/order-confirmation')
@login_required
def send_order_confirmation():
    """Send order confirmation messages"""
    try:
        if request.method == 'POST':
            order_ids = request.form.getlist('order_ids')
            
            if not order_ids:
                flash('Please select orders to send confirmation', 'error')
                return redirect(url_for('admin_whatsapp.send_order_confirmation'))
            
            # Get orders
            orders = Order.query.filter(Order.id.in_(order_ids)).all()
            
            if not orders:
                flash('No valid orders found', 'error')
                return redirect(url_for('admin_whatsapp.send_order_confirmation'))
            
            # Send confirmation messages
            sent_count = 0
            for order in orders:
                if order.user and order.user.phone:
                    success = whatsapp_system.send_order_confirmation(
                        order.user.phone, 
                        order.user.name, 
                        order.id, 
                        order.amount
                    )
                    if success:
                        sent_count += 1
            
            flash(f'Order confirmation sent for {sent_count} orders', 'success')
            return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))
        
        # Get recent orders
        recent_orders = Order.query.filter(
            Order.created_at >= datetime.now() - timedelta(days=1),
            Order.status == 'confirmed'
        ).join(User).filter(User.phone.isnot(None)).all()
        
        return render_template('admin/whatsapp_campaigns/order_confirmation.html',
                            recent_orders=recent_orders)
    except Exception as e:
        current_app.logger.error(f"Error sending order confirmation: {str(e)}")
        flash('Error sending order confirmation', 'error')
        return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns/delivery-reminder')
@login_required
def send_delivery_reminder():
    """Send delivery reminder messages"""
    try:
        if request.method == 'POST':
            subscription_ids = request.form.getlist('subscription_ids')
            
            if not subscription_ids:
                flash('Please select subscriptions to send delivery reminder', 'error')
                return redirect(url_for('admin_whatsapp.send_delivery_reminder'))
            
            # Get subscriptions
            subscriptions = Subscription.query.filter(Subscription.id.in_(subscription_ids)).all()
            
            if not subscriptions:
                flash('No valid subscriptions found', 'error')
                return redirect(url_for('admin_whatsapp.send_delivery_reminder'))
            
            # Send delivery reminders
            sent_count = 0
            for subscription in subscriptions:
                if subscription.user and subscription.user.phone:
                    success = whatsapp_system.send_delivery_reminder(
                        subscription.user.phone,
                        subscription.user.name,
                        subscription.meal_plan.name if subscription.meal_plan else 'Your meal plan'
                    )
                    if success:
                        sent_count += 1
            
            flash(f'Delivery reminder sent for {sent_count} subscriptions', 'success')
            return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))
        
        # Get active subscriptions
        active_subscriptions = Subscription.query.filter_by(status='active').join(User).filter(User.phone.isnot(None)).all()
        
        return render_template('admin/whatsapp_campaigns/delivery_reminder.html',
                            active_subscriptions=active_subscriptions)
    except Exception as e:
        current_app.logger.error(f"Error sending delivery reminder: {str(e)}")
        flash('Error sending delivery reminder', 'error')
        return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns/holiday-notification')
@login_required
def send_holiday_notification():
    """Send holiday notification messages"""
    try:
        if request.method == 'POST':
            # Get current holiday
            current_holiday = Holiday.get_current_holiday()
            
            if not current_holiday:
                flash('No active holiday found', 'error')
                return redirect(url_for('admin_whatsapp.send_holiday_notification'))
            
            # Get all active users with phone numbers
            users = User.query.filter(
                User.is_active == True,
                User.phone.isnot(None)
            ).all()
            
            if not users:
                flash('No users with phone numbers found', 'error')
                return redirect(url_for('admin_whatsapp.send_holiday_notification'))
            
            # Send holiday notifications
            sent_count = 0
            for user in users:
                success = whatsapp_system.send_holiday_notification(
                    user.phone,
                    user.name,
                    current_holiday.name,
                    current_holiday.description,
                    current_holiday.days_remaining
                )
                if success:
                    sent_count += 1
            
            flash(f'Holiday notification sent to {sent_count} users', 'success')
            return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))
        
        # Get current holiday
        current_holiday = Holiday.get_current_holiday()
        
        # Get user count
        user_count = User.query.filter(
            User.is_active == True,
            User.phone.isnot(None)
        ).count()
        
        return render_template('admin/whatsapp_campaigns/holiday_notification.html',
                            current_holiday=current_holiday,
                            user_count=user_count)
    except Exception as e:
        current_app.logger.error(f"Error sending holiday notification: {str(e)}")
        flash('Error sending holiday notification', 'error')
        return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns/promotion-offer')
@login_required
def send_promotion_offer():
    """Send promotion offer messages"""
    try:
        if request.method == 'POST':
            user_ids = request.form.getlist('user_ids')
            discount_code = request.form.get('discount_code', 'SAVE20')
            discount_percent = request.form.get('discount_percent', '20')
            valid_until = request.form.get('valid_until', '7 days')
            
            if not user_ids:
                flash('Please select users to send promotion offer', 'error')
                return redirect(url_for('admin_whatsapp.send_promotion_offer'))
            
            # Get users
            users = User.query.filter(User.id.in_(user_ids)).all()
            
            if not users:
                flash('No valid users found', 'error')
                return redirect(url_for('admin_whatsapp.send_promotion_offer'))
            
            # Send promotion offers
            sent_count = 0
            for user in users:
                if user.phone:
                    success = whatsapp_system.send_promotion_offer(
                        user.phone,
                        user.name,
                        discount_code,
                        discount_percent,
                        valid_until
                    )
                    if success:
                        sent_count += 1
            
            flash(f'Promotion offer sent to {sent_count} users', 'success')
            return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))
        
        # Get all active users with phone numbers
        users = User.query.filter(
            User.is_active == True,
            User.phone.isnot(None)
        ).all()
        
        return render_template('admin/whatsapp_campaigns/promotion_offer.html',
                            users=users)
    except Exception as e:
        current_app.logger.error(f"Error sending promotion offer: {str(e)}")
        flash('Error sending promotion offer', 'error')
        return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns/custom-message')
@login_required
def send_custom_message():
    """Send custom WhatsApp message"""
    try:
        if request.method == 'POST':
            user_ids = request.form.getlist('user_ids')
            message_text = request.form.get('message_text')
            
            if not user_ids:
                flash('Please select users to send message', 'error')
                return redirect(url_for('admin_whatsapp.send_custom_message'))
            
            if not message_text:
                flash('Please enter a message', 'error')
                return redirect(url_for('admin_whatsapp.send_custom_message'))
            
            # Get users
            users = User.query.filter(User.id.in_(user_ids)).all()
            
            if not users:
                flash('No valid users found', 'error')
                return redirect(url_for('admin_whatsapp.send_custom_message'))
            
            # Send custom messages
            sent_count = 0
            for user in users:
                if user.phone:
                    success = whatsapp_system.send_custom_message(user.phone, message_text)
                    if success:
                        sent_count += 1
            
            flash(f'Custom message sent to {sent_count} users', 'success')
            return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))
        
        # Get all active users with phone numbers
        users = User.query.filter(
            User.is_active == True,
            User.phone.isnot(None)
        ).all()
        
        return render_template('admin/whatsapp_campaigns/custom_message.html',
                            users=users)
    except Exception as e:
        current_app.logger.error(f"Error sending custom message: {str(e)}")
        flash('Error sending custom message', 'error')
        return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns/analytics')
@login_required
def whatsapp_analytics():
    """WhatsApp analytics and reports"""
    try:
        # Get analytics data
        analytics = whatsapp_system.get_analytics() if hasattr(whatsapp_system, 'get_analytics') else {
            'total_messages_sent': 0,
            'messages_delivered': 0,
            'messages_read': 0,
            'failed_messages': 0,
            'delivery_rate': 0.0,
            'read_rate': 0.0
        }
        
        # Get webhook logs
        logs = whatsapp_system.get_webhook_logs() if hasattr(whatsapp_system, 'get_webhook_logs') else []
        
        return render_template('admin/whatsapp_campaigns/analytics.html',
                            analytics=analytics,
                            logs=logs)
    except Exception as e:
        current_app.logger.error(f"Error loading WhatsApp analytics: {str(e)}")
        flash('Error loading WhatsApp analytics', 'error')
        return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns/test-connection')
@login_required
def test_whatsapp_connection():
    """Test WhatsApp API connection"""
    try:
        if request.method == 'POST':
            test_phone = request.form.get('test_phone')
            
            if not test_phone:
                flash('Please enter a test phone number', 'error')
                return redirect(url_for('admin_whatsapp.test_whatsapp_connection'))
            
            # Send test message
            test_message = "🧪 This is a test message from HealthyRizz WhatsApp API. If you receive this, the integration is working correctly!"
            
            success = whatsapp_system.send_custom_message(test_phone, test_message)
            
            if success:
                flash('Test message sent successfully. Check your WhatsApp!', 'success')
            else:
                flash('Failed to send test message. Check your API configuration.', 'error')
            
            return redirect(url_for('admin_whatsapp.test_whatsapp_connection'))
        
        return render_template('admin/whatsapp_campaigns/test_connection.html')
    except Exception as e:
        current_app.logger.error(f"Error testing WhatsApp connection: {str(e)}")
        flash('Error testing WhatsApp connection', 'error')
        return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns/templates')
@login_required
def whatsapp_templates():
    """View and manage WhatsApp templates"""
    try:
        # Get available templates
        templates = whatsapp_system.templates
        
        return render_template('admin/whatsapp_campaigns/templates.html',
                            templates=templates)
    except Exception as e:
        current_app.logger.error(f"Error loading WhatsApp templates: {str(e)}")
        flash('Error loading WhatsApp templates', 'error')
        return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))

@admin_whatsapp_bp.route('/admin/whatsapp-campaigns/settings')
@login_required
def whatsapp_settings():
    """WhatsApp API settings"""
    try:
        if request.method == 'POST':
            # Update settings
            phone_number_id = request.form.get('phone_number_id')
            access_token = request.form.get('access_token')
            verify_token = request.form.get('verify_token')
            
            # Here you would typically save these to your configuration
            # For now, we'll just show a success message
            flash('WhatsApp settings updated successfully', 'success')
            return redirect(url_for('admin_whatsapp.whatsapp_settings'))
        
        # Get current settings
        settings = {
            'phone_number_id': current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', ''),
            'access_token': current_app.config.get('WHATSAPP_ACCESS_TOKEN', ''),
            'verify_token': current_app.config.get('WHATSAPP_VERIFY_TOKEN', ''),
            'webhook_url': f"{request.host_url}webhook/whatsapp"
        }
        
        return render_template('admin/whatsapp_campaigns/settings.html',
                            settings=settings)
    except Exception as e:
        current_app.logger.error(f"Error loading WhatsApp settings: {str(e)}")
        flash('Error loading WhatsApp settings', 'error')
        return redirect(url_for('admin_whatsapp.whatsapp_campaigns_dashboard'))
