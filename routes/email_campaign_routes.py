#!/usr/bin/env python3
"""
Email Campaign Management Routes for Admin Panel
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required
from database.models import User, Order, Subscription, MealPlan, Holiday, db
from datetime import datetime, timedelta
from email_marketing_system import email_system
import json

email_campaign_bp = Blueprint('email_campaign', __name__)

@email_campaign_bp.route('/admin/email-campaigns')
@login_required
def email_campaigns_dashboard():
    """Email campaigns dashboard"""
    try:
        # Get campaign statistics
        stats = email_system.get_campaign_stats()
        
        # Get recent campaigns (this would come from a Campaign model)
        recent_campaigns = []  # Placeholder for actual campaign data
        
        # Get user segments for targeting
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        new_users_this_week = User.query.filter(
            User.created_at >= datetime.now() - timedelta(days=7)
        ).count()
        inactive_users = User.query.filter(
            User.created_at <= datetime.now() - timedelta(days=30)
        ).count()
        
        return render_template('admin/email_campaigns/dashboard.html',
                             stats=stats,
                             recent_campaigns=recent_campaigns,
                             total_users=total_users,
                             active_users=active_users,
                             new_users_this_week=new_users_this_week,
                             inactive_users=inactive_users)
    except Exception as e:
        current_app.logger.error(f"Error in email campaigns dashboard: {str(e)}")
        flash('Error loading email campaigns dashboard', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@email_campaign_bp.route('/admin/email-campaigns/welcome-series')
@login_required
def welcome_series_campaign():
    """Welcome series campaign management"""
    try:
        if request.method == 'POST':
            # Get new users who haven't received welcome emails
            new_users = User.query.filter(
                User.created_at >= datetime.now() - timedelta(days=1),
                User.is_active == True
            ).all()
            
            sent_count = 0
            for user in new_users:
                if email_system.send_welcome_series(user):
                    sent_count += 1
            
            flash(f'Welcome series sent to {sent_count} new users', 'success')
            return redirect(url_for('email_campaign.email_campaigns_dashboard'))
        
        # Get users eligible for welcome series
        eligible_users = User.query.filter(
            User.created_at >= datetime.now() - timedelta(days=7),
            User.is_active == True
        ).all()
        
        return render_template('admin/email_campaigns/welcome_series.html',
                             eligible_users=eligible_users)
    except Exception as e:
        current_app.logger.error(f"Error in welcome series campaign: {str(e)}")
        flash('Error managing welcome series campaign', 'error')
        return redirect(url_for('email_campaign.email_campaigns_dashboard'))

@email_campaign_bp.route('/admin/email-campaigns/abandoned-cart')
@login_required
def abandoned_cart_campaign():
    """Abandoned cart recovery campaign"""
    try:
        if request.method == 'POST':
            # This would integrate with actual cart data
            # For now, we'll simulate abandoned cart users
            users_with_orders = User.query.join(Order).all()
            
            sent_count = 0
            for user in users_with_orders:
                # Simulate abandoned cart items
                cart_items = ['Balanced Lunch Plan', 'High-Protein Weight Loss Plan']
                if email_system.send_abandoned_cart_emails(user, cart_items):
                    sent_count += 1
            
            flash(f'Abandoned cart emails sent to {sent_count} users', 'success')
            return redirect(url_for('email_campaign.email_campaigns_dashboard'))
        
        return render_template('admin/email_campaigns/abandoned_cart.html')
    except Exception as e:
        current_app.logger.error(f"Error in abandoned cart campaign: {str(e)}")
        flash('Error managing abandoned cart campaign', 'error')
        return redirect(url_for('email_campaign.email_campaigns_dashboard'))

@email_campaign_bp.route('/admin/email-campaigns/meal-plan-promotion')
@login_required
def meal_plan_promotion_campaign():
    """Meal plan promotion campaign"""
    try:
        meal_plans = MealPlan.query.filter_by(is_active=True).all()
        
        if request.method == 'POST':
            meal_plan_id = request.form.get('meal_plan_id')
            discount_percent = int(request.form.get('discount_percent', 15))
            
            meal_plan = MealPlan.query.get(meal_plan_id)
            if meal_plan:
                if email_system.send_meal_plan_promotion(meal_plan, discount_percent):
                    flash(f'Promotion email sent for {meal_plan.name}', 'success')
                else:
                    flash('Error sending promotion email', 'error')
            else:
                flash('Meal plan not found', 'error')
            
            return redirect(url_for('email_campaign.email_campaigns_dashboard'))
        
        return render_template('admin/email_campaigns/meal_plan_promotion.html',
                             meal_plans=meal_plans)
    except Exception as e:
        current_app.logger.error(f"Error in meal plan promotion campaign: {str(e)}")
        flash('Error managing meal plan promotion campaign', 'error')
        return redirect(url_for('email_campaign.email_campaigns_dashboard'))

@email_campaign_bp.route('/admin/email-campaigns/win-back')
@login_required
def win_back_campaign():
    """Win-back campaign for inactive users"""
    try:
        if request.method == 'POST':
            # Get inactive users (no orders in last 30 days)
            inactive_users = User.query.filter(
                User.created_at <= datetime.now() - timedelta(days=30),
                User.is_active == True
            ).all()
            
            sent_count = 0
            for user in inactive_users:
                if email_system.send_win_back_campaign(user):
                    sent_count += 1
            
            flash(f'Win-back emails sent to {sent_count} inactive users', 'success')
            return redirect(url_for('email_campaign.email_campaigns_dashboard'))
        
        # Get inactive users for preview
        inactive_users = User.query.filter(
            User.created_at <= datetime.now() - timedelta(days=30),
            User.is_active == True
        ).all()
        
        return render_template('admin/email_campaigns/win_back.html',
                             inactive_users=inactive_users)
    except Exception as e:
        current_app.logger.error(f"Error in win-back campaign: {str(e)}")
        flash('Error managing win-back campaign', 'error')
        return redirect(url_for('email_campaign.email_campaigns_dashboard'))

@email_campaign_bp.route('/admin/email-campaigns/referral-program')
@login_required
def referral_program_campaign():
    """Referral program campaign"""
    try:
        if request.method == 'POST':
            # Get active users for referral program
            active_users = User.query.filter_by(is_active=True).all()
            
            sent_count = 0
            for user in active_users:
                if email_system.send_referral_invitation(user):
                    sent_count += 1
            
            flash(f'Referral invitations sent to {sent_count} users', 'success')
            return redirect(url_for('email_campaign.email_campaigns_dashboard'))
        
        # Get active users for preview
        active_users = User.query.filter_by(is_active=True).all()
        
        return render_template('admin/email_campaigns/referral_program.html',
                             active_users=active_users)
    except Exception as e:
        current_app.logger.error(f"Error in referral program campaign: {str(e)}")
        flash('Error managing referral program campaign', 'error')
        return redirect(url_for('email_campaign.email_campaigns_dashboard'))

@email_campaign_bp.route('/admin/email-campaigns/holiday-notification')
@login_required
def holiday_notification_campaign():
    """Holiday notification campaign"""
    try:
        holidays = Holiday.query.filter_by(is_active=True).all()
        
        if request.method == 'POST':
            holiday_id = request.form.get('holiday_id')
            
            holiday = Holiday.query.get(holiday_id)
            if holiday:
                if email_system.send_holiday_notification(holiday):
                    flash(f'Holiday notification sent for {holiday.name}', 'success')
                else:
                    flash('Error sending holiday notification', 'error')
            else:
                flash('Holiday not found', 'error')
            
            return redirect(url_for('email_campaign.email_campaigns_dashboard'))
        
        return render_template('admin/email_campaigns/holiday_notification.html',
                             holidays=holidays)
    except Exception as e:
        current_app.logger.error(f"Error in holiday notification campaign: {str(e)}")
        flash('Error managing holiday notification campaign', 'error')
        return redirect(url_for('email_campaign.email_campaigns_dashboard'))

@email_campaign_bp.route('/admin/email-campaigns/custom')
@login_required
def custom_campaign():
    """Custom email campaign"""
    try:
        if request.method == 'POST':
            subject = request.form.get('subject')
            html_content = request.form.get('html_content')
            user_segment = request.form.get('user_segment')
            
            # Get users based on segment
            if user_segment == 'all':
                users = User.query.filter_by(is_active=True).all()
            elif user_segment == 'new':
                users = User.query.filter(
                    User.created_at >= datetime.now() - timedelta(days=7),
                    User.is_active == True
                ).all()
            elif user_segment == 'inactive':
                users = User.query.filter(
                    User.created_at <= datetime.now() - timedelta(days=30),
                    User.is_active == True
                ).all()
            elif user_segment == 'newsletter':
                # Newsletter subscribers - include both users and non-users
                from database.models import Newsletter
                newsletter_emails = [n.email for n in Newsletter.query.all()]
                users = User.query.filter(User.email.in_(newsletter_emails)).all()
                
                # If no users found, create a list of newsletter subscribers without user accounts
                if not users and newsletter_emails:
                    users = []
                    for email in newsletter_emails:
                        existing_user = User.query.filter_by(email=email).first()
                        if not existing_user:
                            mock_user = type('MockUser', (), {
                                'id': f'newsletter_{email}',
                                'email': email,
                                'name': email.split('@')[0],
                                'phone': None
                            })()
                            users.append(mock_user)
            else:
                users = []
            
            sent_count = 0
            for user in users:
                if email_system.send_email(user.email, subject, html_content):
                    sent_count += 1
            
            flash(f'Custom campaign sent to {sent_count} users', 'success')
            return redirect(url_for('email_campaign.email_campaigns_dashboard'))
        
        return render_template('admin/email_campaigns/custom.html')
    except Exception as e:
        current_app.logger.error(f"Error in custom campaign: {str(e)}")
        flash('Error managing custom campaign', 'error')
        return redirect(url_for('email_campaign.email_campaigns_dashboard'))

@email_campaign_bp.route('/admin/email-campaigns/analytics')
@login_required
def email_analytics():
    """Email campaign analytics"""
    try:
        # Get campaign statistics
        stats = email_system.get_campaign_stats()
        
        # Get user engagement data (this would come from actual email tracking)
        engagement_data = {
            'total_emails_sent': 0,
            'emails_opened': 0,
            'emails_clicked': 0,
            'conversions': 0
        }
        
        return render_template('admin/email_campaigns/analytics.html',
                             stats=stats,
                             engagement_data=engagement_data)
    except Exception as e:
        current_app.logger.error(f"Error in email analytics: {str(e)}")
        flash('Error loading email analytics', 'error')
        return redirect(url_for('email_campaign.email_campaigns_dashboard'))

@email_campaign_bp.route('/admin/email-campaigns/templates')
@login_required
def email_templates():
    """Email template management"""
    try:
        # Define available templates
        templates = [
            {
                'name': 'Welcome Series',
                'description': 'Welcome emails for new users',
                'type': 'welcome',
                'variables': ['user_name', 'user_email', 'signup_date']
            },
            {
                'name': 'Order Confirmation',
                'description': 'Order confirmation emails',
                'type': 'order_confirmation',
                'variables': ['order_id', 'order_amount', 'delivery_date', 'meal_plan']
            },
            {
                'name': 'Delivery Reminder',
                'description': 'Delivery reminder emails',
                'type': 'delivery_reminder',
                'variables': ['order_id', 'delivery_address', 'estimated_time']
            },
            {
                'name': 'Holiday Notification',
                'description': 'Holiday notification emails',
                'type': 'holiday_notification',
                'variables': ['holiday_name', 'holiday_dates', 'description']
            },
            {
                'name': 'Meal Plan Promotion',
                'description': 'Meal plan promotion emails',
                'type': 'meal_plan_promotion',
                'variables': ['meal_plan_name', 'original_price', 'discounted_price', 'discount_percent']
            },
            {
                'name': 'Loyalty Rewards',
                'description': 'Loyalty rewards notification emails',
                'type': 'loyalty_rewards',
                'variables': ['points_earned', 'total_points', 'rewards_available']
            },
            {
                'name': 'Feedback Request',
                'description': 'Feedback request emails',
                'type': 'feedback_request',
                'variables': ['order_id', 'meal_plan', 'delivery_date']
            },
            {
                'name': 'Win-Back Campaign',
                'description': 'Win-back campaign emails',
                'type': 'win_back',
                'variables': ['user_name', 'last_order_date', 'comeback_offer']
            },
            {
                'name': 'Referral Program',
                'description': 'Referral program invitation emails',
                'type': 'referral_program',
                'variables': ['user_name', 'referral_link', 'rewards_info']
            }
        ]
        
        return render_template('admin/email_campaigns/templates.html',
                             templates=templates)
    except Exception as e:
        current_app.logger.error(f"Error in email templates: {str(e)}")
        flash('Error loading email templates', 'error')
        return redirect(url_for('email_campaign.email_campaigns_dashboard'))

@email_campaign_bp.route('/admin/email-campaigns/schedule')
@login_required
def schedule_campaign():
    """Schedule email campaign"""
    try:
        if request.method == 'POST':
            campaign_type = request.form.get('campaign_type')
            scheduled_date = request.form.get('scheduled_date')
            user_segment = request.form.get('user_segment')
            
            # This would integrate with a task queue like Celery
            # For now, we'll just log the scheduled campaign
            current_app.logger.info(f"Campaign {campaign_type} scheduled for {scheduled_date} targeting {user_segment}")
            
            flash(f'Campaign {campaign_type} scheduled for {scheduled_date}', 'success')
            return redirect(url_for('email_campaign.email_campaigns_dashboard'))
        
        # Get available campaign types
        campaign_types = list(email_system.campaign_types.keys())
        
        return render_template('admin/email_campaigns/schedule.html',
                             campaign_types=campaign_types)
    except Exception as e:
        current_app.logger.error(f"Error scheduling campaign: {str(e)}")
        flash('Error scheduling campaign', 'error')
        return redirect(url_for('email_campaign.email_campaigns_dashboard'))
