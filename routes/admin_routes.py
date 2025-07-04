"""
Admin routes for HealthyRizz application
"""
import os
import json
import logging
from datetime import datetime, timedelta, date
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session, Response, abort, send_file
from flask_login import login_required, current_user, login_user
from sqlalchemy import desc, func, or_, true, false
from wtforms import StringField, TextAreaField, SelectField, RadioField, BooleanField, FloatField, DateField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Length, URL, Optional, Regexp, NumberRange, ValidationError
from flask_wtf import FlaskForm
from extensions import mail, db, limiter, csrf
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Frame, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from urllib.parse import urlparse

# Import models at the top level
from database.models import (
    User, DeliveryLocation, MealPlan, TrialRequest, Delivery,
    Subscription, Newsletter, ServiceRequest, BlogPost, FAQ,
    CouponCode, Banner, PushSubscription, Notification, SubscriptionStatus, SubscriptionFrequency, DeliveryStatus,
    State, City, Area, HeroSlide, Video, TeamMember, SiteSetting,
    ContactInquiry, FullWidthSection
)

# Import forms
from forms.auth_forms import LoginForm

# Import utility functions
from utils.email_utils import send_email
from utils.sms_utils import send_sms

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint with explicit name and url_prefix
admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

def get_db():
    """Get the database instance"""
    return db

# Context processor to make site settings available to all admin templates
@admin_bp.context_processor
def inject_site_settings():
    """Inject site settings into all admin templates"""
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
            settings['company_name'] = 'HealthyRizz'
        if 'company_tagline' not in settings:
            settings['company_tagline'] = 'Healthy Meal Delivery'
        
        return {'site_settings': settings}
    except Exception as e:
        current_app.logger.error(f"Error loading site settings: {str(e)}")
        return {'site_settings': {
            'site_logo': '/static/images/logo white.png',
            'company_name': 'HealthyRizz',
            'company_tagline': 'Healthy Meal Delivery'
        }}

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('main.login'))
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('admin.admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Forms
class NotificationForm(FlaskForm):
    """Form for sending notifications"""
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=200)])
    email_subject = StringField('Email Subject', validators=[DataRequired(), Length(max=200)])
    email_content = TextAreaField('Email Content', validators=[DataRequired()])
    recipient_type = RadioField('Recipients', choices=[
        ('all', 'All Users'),
        ('subscribers', 'Active Subscribers Only'),
        ('specific', 'Specific User')
    ], default='all')
    user_id = StringField('User ID', validators=[Optional()])
    notification_type = SelectField('Type', choices=[
        ('general', 'General Announcement'),
        ('promotion', 'Promotion/Special Offer'),
        ('order_update', 'Order Update'),
        ('delivery', 'Delivery Information'),
        ('account', 'Account Update')
    ])
    channels = SelectMultipleField('Channels', choices=[
        ('push', 'Push Notification'),
        ('email', 'Email'),
        ('sms', 'SMS')
    ], default=['push', 'email'])

class CouponForm(FlaskForm):
    """Form for adding a new coupon"""
    code = StringField('Code', validators=[
        DataRequired(),
        Length(min=3, max=20),
        Regexp(r'^[A-Z0-9]+$', message='Coupon code must contain only uppercase letters and numbers')
    ])
    discount_type = SelectField('Discount Type', choices=[
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('shipping', 'Free Shipping')
    ], validators=[DataRequired()])
    discount_value = FloatField('Discount Value', validators=[
        DataRequired(),
        NumberRange(min=0, message='Discount value must be positive')
    ])
    min_order_value = FloatField('Minimum Order Value', validators=[
        Optional(),
        NumberRange(min=0, message='Minimum order value must be positive')
    ])
    valid_from = DateField('Valid From', validators=[DataRequired()])
    valid_to = DateField('Valid To', validators=[DataRequired()])
    max_uses = IntegerField('Maximum Uses', validators=[
        Optional(),
        NumberRange(min=1, message='Maximum uses must be at least 1')
    ])
    is_single_use = BooleanField('Single Use')
    is_active = BooleanField('Active', default=True)

    def validate_discount_value(self, field):
        if self.discount_type.data == 'percentage' and field.data > 100:
            raise ValidationError('Percentage discount cannot exceed 100%')
        if self.discount_type.data == 'fixed' and field.data <= 0:
            raise ValidationError('Fixed discount must be greater than 0')

    def validate_valid_to(self, field):
        if field.data < self.valid_from.data:
            raise ValidationError('Valid to date must be after valid from date')

# Routes
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
@limiter.limit("60 per minute")
def admin_dashboard():
    """Admin dashboard view"""
    try:
        # Get basic statistics
        total_users = User.query.count()
        new_users = User.query.filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Get subscription statistics
        active_subscriptions = Subscription.query.filter_by(status='active').count()
        trial_subscriptions = Subscription.query.filter_by(status='trial').count()
        total_meal_plans = MealPlan.query.count()
        active_meal_plans = MealPlan.query.filter_by(is_active=True).count()
        total_locations = DeliveryLocation.query.count()
        active_locations = DeliveryLocation.query.filter_by(is_active=True).count()

        # Get recent activity
        recent_activity = []
        
        # Add recent subscriptions
        recent_subs = Subscription.query.order_by(Subscription.created_at.desc()).limit(5).all()
        for sub in recent_subs:
            recent_activity.append({
                'type': 'subscription',
                'user': sub.user,
                'details': f"New {sub.status} subscription",
                'created_at': sub.created_at
            })
        
        # Add recent trial requests
        recent_trials = TrialRequest.query.order_by(TrialRequest.created_at.desc()).limit(5).all()
        for trial in recent_trials:
            recent_activity.append({
                'type': 'trial_request',
                'user': None,  # Trial requests don't have user_id
                'details': f"New trial request from {trial.email}",
                'created_at': trial.created_at
            })

        # Sort activities by date
        recent_activity.sort(key=lambda x: x['created_at'], reverse=True)
        recent_activity = recent_activity[:10]  # Keep only the 10 most recent

        return render_template('admin/dashboard.html',
                             total_users=total_users,
                             new_users=new_users,
                             active_subscriptions=active_subscriptions,
                             trial_subscriptions=trial_subscriptions,
                             total_meal_plans=total_meal_plans,
                             active_meal_plans=active_meal_plans,
                             total_locations=total_locations,
                             active_locations=active_locations,
                             recent_activity=recent_activity)
    except Exception as e:
        current_app.logger.error(f"Error loading admin dashboard: {str(e)}")
        flash('An error occurred while loading the dashboard.', 'error')
        return redirect(url_for('main.index'))

@admin_bp.route('/locations', methods=['GET'])
@login_required
@admin_required
def admin_location_tree():
    return render_template('admin/locations.html')

# --- AJAX CRUD for State ---
@admin_bp.route('/locations/state', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_state_crud():
    if request.method == 'GET':
        states = State.query.order_by(State.name).all()
        return jsonify([{'id': s.id, 'name': s.name} for s in states])
    data = request.get_json()
    state = State(name=data['name'])
    db.session.add(state)
    db.session.commit()
    return jsonify({'id': state.id, 'name': state.name})

@admin_bp.route('/locations/state/<int:state_id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required
def admin_state_update_delete(state_id):
    state = State.query.get_or_404(state_id)
    if request.method == 'PUT':
        data = request.get_json()
        state.name = data['name']
        db.session.commit()
        return jsonify({'id': state.id, 'name': state.name})
    db.session.delete(state)
    db.session.commit()
    return jsonify({'result': 'deleted'})

# --- AJAX CRUD for City ---
@admin_bp.route('/locations/city', methods=['POST'])
@login_required
@admin_required
def admin_city_create():
    data = request.get_json()
    city = City(name=data['name'], state_id=data['state_id'])
    db.session.add(city)
    db.session.commit()
    return jsonify({'id': city.id, 'name': city.name, 'state_id': city.state_id})

@admin_bp.route('/locations/city/<int:state_id>', methods=['GET'])
@login_required
@admin_required
def admin_city_list(state_id):
    cities = City.query.filter_by(state_id=state_id).order_by(City.name).all()
    return jsonify([{'id': c.id, 'name': c.name, 'state_id': c.state_id} for c in cities])

@admin_bp.route('/locations/city/<int:city_id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required
def admin_city_update_delete(city_id):
    city = City.query.get_or_404(city_id)
    if request.method == 'PUT':
        data = request.get_json()
        city.name = data['name']
        db.session.commit()
        return jsonify({'id': city.id, 'name': city.name, 'state_id': city.state_id})
    db.session.delete(city)
    db.session.commit()
    return jsonify({'result': 'deleted'})

# --- AJAX CRUD for Area ---
@admin_bp.route('/locations/area', methods=['POST'])
@login_required
@admin_required
def admin_area_create():
    data = request.get_json()
    area = Area(name=data['name'], city_id=data['city_id'])
    db.session.add(area)
    db.session.commit()
    return jsonify({'id': area.id, 'name': area.name, 'city_id': area.city_id})

@admin_bp.route('/locations/area/<int:city_id>', methods=['GET'])
@login_required
@admin_required
def admin_area_list(city_id):
    areas = Area.query.filter_by(city_id=city_id).order_by(Area.name).all()
    return jsonify([{'id': a.id, 'name': a.name, 'city_id': a.city_id} for a in areas])

@admin_bp.route('/locations/area/<int:area_id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required
def admin_area_update_delete(area_id):
    area = Area.query.get_or_404(area_id)
    if request.method == 'PUT':
        data = request.get_json()
        area.name = data['name']
        db.session.commit()
        return jsonify({'id': area.id, 'name': area.name, 'city_id': area.city_id})
    db.session.delete(area)
    db.session.commit()
    return jsonify({'result': 'deleted'})

@admin_bp.route('/users')
@login_required
@admin_required
@limiter.limit("60 per minute")  # Increased from 30 to 60
def admin_users():
    """Admin users management page"""
    try:
        # Get all users
        users = User.query.all()
        
        # Get today's date for comparison
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count new users today
        new_users_today = sum(1 for user in users if user.created_at >= today)
        
        return render_template('admin/users.html', 
                             users=users,
                             new_users_today=new_users_today,
                             today=today)
    except Exception as e:
        current_app.logger.error(f"Error loading users: {str(e)}")
        flash('Error loading users', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def admin_view_user(user_id):
    """View a single user's details"""
    user = User.query.get_or_404(user_id)
    
    # In a real application, you would fetch more details about the user
    # such as their subscriptions, delivery history, etc.
    
    return render_template('admin/user_view.html', user=user)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    """Edit a user's details"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'update_user':
            # Handle user update form submission
            user.username = request.form.get('username', user.username)
            user.email = request.form.get('email', user.email)
            user.phone = request.form.get('phone', user.phone)
            
            # Only update password if provided
            password = request.form.get('password')
            if password and password.strip():
                # In a real app, you would hash the password
                user.password_hash = password  # This would be properly hashed
            
            # Update status fields
            user.is_active = 'is_active' in request.form
            user.email_verified = 'email_verified' in request.form
            
            # Make admin if requested and not already admin
            if not user.is_admin and 'make_admin' in request.form:
                user.is_admin = True
            
            # Update address
            user.address_line1 = request.form.get('address_line1', user.address_line1)
            user.address_line2 = request.form.get('address_line2', user.address_line2)
            user.city = request.form.get('city', user.city)
            user.province = request.form.get('province', user.province)
            user.postal_code = request.form.get('postal_code', user.postal_code)
            user.country = request.form.get('country', user.country)
            
            # Update admin notes
            user.admin_notes = request.form.get('admin_notes', user.admin_notes)
            user.notes_updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('User information updated successfully', 'success')
            return redirect(url_for('admin.admin_view_user', user_id=user.id))
        
        elif action == 'update_notes':
            # Handle notes update form submission
            user.admin_notes = request.form.get('admin_notes', '')
            user.notes_updated_at = datetime.utcnow()
            db.session.commit()
            flash('Admin notes updated successfully', 'success')
            return redirect(url_for('admin.admin_view_user', user_id=user.id))
            
        elif action == 'delete_user':
            # Handle user deletion
            if user.is_admin:
                flash('Cannot delete admin users', 'error')
            else:
                # In a real app, you would handle dependencies
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully', 'success')
                return redirect(url_for('admin.admin_users'))
    
    # For GET requests or if no valid action was submitted, render edit form
    return render_template('admin/user_edit.html', user=user)


@admin_bp.route('/meal-plans')
@login_required
@admin_required
@limiter.limit("60 per minute")  # Increased from 30 to 60
def admin_meal_plans():
    """Admin view for managing meal plans"""
    try:
        # Get filter parameters
        search = request.args.get('search', '')
        status = request.args.get('status', 'all')
        category = request.args.get('category', 'all')
        
        # Base query
        query = MealPlan.query
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    MealPlan.name.ilike(f'%{search}%'),
                    MealPlan.description.ilike(f'%{search}%'),
                    MealPlan.tag.ilike(f'%{search}%')
                )
            )
        
        if status != 'all':
            query = query.filter(MealPlan.is_active == (status == 'active'))
            
        if category != 'all':
            if category == 'vegetarian':
                query = query.filter(MealPlan.is_vegetarian == True)
            elif category == 'vegan':
                query = query.filter(MealPlan.is_vegan == True)
            elif category == 'gluten_free':
                query = query.filter(MealPlan.is_gluten_free == True)
            elif category == 'dairy_free':
                query = query.filter(MealPlan.is_dairy_free == True)
            elif category == 'keto':
                query = query.filter(MealPlan.is_keto == True)
            elif category == 'paleo':
                query = query.filter(MealPlan.is_paleo == True)
            elif category == 'low_carb':
                query = query.filter(MealPlan.is_low_carb == True)
            elif category == 'high_protein':
                query = query.filter(MealPlan.is_high_protein == True)
        
        # Get all meal plans
        plans = query.order_by(MealPlan.name).all()
        
        # Ensure all meal plans have required attributes
        for plan in plans:
            # Set default values for required attributes if they're None
            if plan.price_trial is None:
                plan.price_trial = 999.00
            if plan.available_for_trial is None:
                plan.available_for_trial = False
            if plan.image_url is None:
                plan.image_url = url_for('static', filename='images/default-meal-plan.svg')
            if plan.is_vegetarian is None:
                plan.is_vegetarian = False
            if plan.is_vegan is None:
                plan.is_vegan = False
            if plan.is_gluten_free is None:
                plan.is_gluten_free = False
            if plan.is_dairy_free is None:
                plan.is_dairy_free = False
            if plan.is_keto is None:
                plan.is_keto = False
            if plan.is_paleo is None:
                plan.is_paleo = False
            if plan.is_low_carb is None:
                plan.is_low_carb = False
            if plan.is_high_protein is None:
                plan.is_high_protein = False
            if plan.for_gender is None:
                plan.for_gender = 'both'
            if plan.is_popular is None:
                plan.is_popular = False
            if plan.is_active is None:
                plan.is_active = True
        
        return render_template('admin/meal_plans.html',
                             plans=plans,
                             current_search=search,
                             current_status=status,
                             current_category=category)
                             
    except Exception as e:
        current_app.logger.error(f"Error loading meal plans: {str(e)}")
        flash('An error occurred while loading meal plans. Please try again.', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/add-meal-plan', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_meal_plan():
    """Admin view for adding a new meal plan"""
    if request.method == 'POST':
        try:
            # Log form data for debugging
            current_app.logger.info("Form data received:")
            for key, value in request.form.items():
                current_app.logger.info(f"{key}: {value}")
            
            # Handle None values for numeric fields
            def safe_float(value):
                if value is None or value == '':
                    return 0.0
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            
            def safe_int(value):
                if value is None or value == '':
                    return None
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return None
            
            # Create new meal plan
            meal_plan = MealPlan(
                name=request.form.get('name'),
                description=request.form.get('description'),
                calories=safe_int(request.form.get('calories')),
                protein=safe_float(request.form.get('protein')),
                carbs=safe_float(request.form.get('carbs')),
                fat=safe_float(request.form.get('fat')),
                price_weekly=safe_float(request.form.get('price_weekly')),
                price_monthly=safe_float(request.form.get('price_monthly')),
                price_trial=safe_float(request.form.get('price_trial')),
                is_vegetarian=request.form.get('is_vegetarian') == 'true',
                available_for_trial=request.form.get('available_for_trial') == 'true',
                tag=request.form.get('tag'),
                is_popular=request.form.get('is_popular') == 'true',
                is_active=request.form.get('is_active') == 'true',
                image_url=request.form.get('image_url')
            )
            
            db.session.add(meal_plan)
            db.session.commit()
            
            flash('Meal plan added successfully!', 'success')
            return redirect(url_for('admin.admin_meal_plans'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding meal plan: {str(e)}")
            flash('Error adding meal plan. Please try again.', 'error')
            return redirect(url_for('admin.admin_add_meal_plan'))
    
    return render_template('admin/add_meal_plan.html')

@admin_bp.route('/trial-requests')
@login_required
@admin_required
@limiter.limit("60 per minute")  # Increased from 30 to 60
def admin_trial_requests():
    """Admin trial requests page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of items per page
        
        # Get paginated trial requests
        trial_requests = TrialRequest.query.order_by(
            TrialRequest.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('admin/trial_requests.html', trial_requests=trial_requests)
    except Exception as e:
        current_app.logger.error(f"Error loading trial requests: {str(e)}")
        flash('An error occurred while loading trial requests. Please try again.', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/trial-request/<int:request_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_trial_request_detail(request_id):
    trial_request = TrialRequest.query.get_or_404(request_id)
    form = FlaskForm()  # Create an empty form for CSRF protection
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'approve':
            trial_request.status = 'approved'
            flash('Trial request has been approved.', 'success')
        elif action == 'reject':
            trial_request.status = 'rejected'
            flash('Trial request has been rejected.', 'success')
        elif action == 'complete':
            trial_request.status = 'completed'
            flash('Trial request has been marked as completed.', 'success')
        
        db.session.commit()
        return redirect(url_for('admin.admin_trial_requests'))
    
    return render_template('admin/trial_request_detail.html', trial_request=trial_request, form=form)

@admin_bp.route('/trial-requests/approve/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_approve_trial_request(id):
    """Approve a trial request"""
    try:
        trial_request = TrialRequest.query.get_or_404(id)
        trial_request.status = 'approved'
        db.session.commit()
        flash('Trial request approved successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error approving trial request: {str(e)}")
        flash('Error approving trial request', 'error')
    return redirect(url_for('admin.admin_trial_requests'))

@admin_bp.route('/trial-requests/reject/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_reject_trial_request(id):
    """Reject a trial request"""
    try:
        trial_request = TrialRequest.query.get_or_404(id)
        trial_request.status = 'rejected'
        db.session.commit()
        flash('Trial request rejected successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error rejecting trial request: {str(e)}")
        flash('Error rejecting trial request', 'error')
    return redirect(url_for('admin.admin_trial_requests'))

@admin_bp.route('/trial-requests/complete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_complete_trial_request(id):
    """Mark a trial request as completed"""
    try:
        trial_request = TrialRequest.query.get_or_404(id)
        trial_request.status = 'completed'
        db.session.commit()
        flash('Trial request marked as completed', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error completing trial request: {str(e)}")
        flash('Error completing trial request', 'error')
    return redirect(url_for('admin.admin_trial_requests'))

@admin_bp.route('/trial-requests/update-notes/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_update_trial_request_notes(id):
    """Update admin notes for a trial request"""
    try:
        trial_request = TrialRequest.query.get_or_404(id)
        trial_request.admin_notes = request.form.get('admin_notes', '')
        db.session.commit()
        flash('Notes updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating trial request notes: {str(e)}")
        flash('Error updating notes', 'error')
    return redirect(url_for('admin.admin_trial_requests'))

@admin_bp.route('/orders')
@login_required
@admin_required
def admin_orders():
    """Admin orders management page"""
    from datetime import datetime
    from flask import request, current_app
    from database.models import DeliveryStatus
    
    # Get today's date or selected date from query parameters
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()
    
    # Import the report_utils module
    from utils.report_utils import get_daily_orders, get_skipped_deliveries
    
    # Get orders and skipped deliveries for the selected date
    orders = get_daily_orders(selected_date)
    skipped = get_skipped_deliveries(selected_date)
    
    # Transform orders to match template expectations
    transformed_orders = []
    for order in orders:
        transformed_order = {
            'customer_name': order.get('user_name', 'N/A'),
            'email': order.get('user_email', 'N/A'),
            'phone': order.get('user_phone', 'N/A'),
            'meal_plan_name': order.get('meal_plan_name', 'N/A'),
            'is_vegetarian': order.get('is_vegetarian', False),
            'includes_breakfast': order.get('with_breakfast', False),
            'address': order.get('delivery_address', 'N/A'),
            'city': order.get('delivery_city', 'N/A'),
            'province': order.get('delivery_state', 'N/A'),
            'postal_code': order.get('delivery_postal_code', 'N/A'),
            'subscription_id': order.get('subscription_id', 'N/A'),
            'created_at': order.get('created_at', 'N/A'),
            'delivery_status': order.get('delivery_status', 'pending'),
            'delivery_id': order.get('delivery_id'),
            'is_skipped': order.get('is_skipped', False)
        }
        transformed_orders.append(transformed_order)
    
    # Calculate location counts
    location_counts = {}
    for order in transformed_orders:
        location_key = f"{order['city']}, {order['province']}"
        location_counts[location_key] = location_counts.get(location_key, 0) + 1
    
    # Calculate meal counts
    meal_counts = {}
    for order in transformed_orders:
        meal_key = f"{order['meal_plan_name']} ({'Veg' if order['is_vegetarian'] else 'Non-Veg'}, {'w/Breakfast' if order['includes_breakfast'] else 'No Breakfast'})"
        meal_counts[meal_key] = meal_counts.get(meal_key, 0) + 1
    
    # Get all possible delivery statuses
    delivery_statuses = [status.value for status in DeliveryStatus]
    
    current_app.logger.info(f"Admin viewing orders for date: {selected_date}")
    
    return render_template('admin/orders.html', 
                          selected_date=selected_date,
                          orders=transformed_orders,
                          skipped=skipped,
                          delivery_statuses=delivery_statuses,
                          location_counts=location_counts,
                          meal_counts=meal_counts)

@admin_bp.route('/subscriptions')
@login_required
@admin_required
def admin_subscriptions():
    """Admin subscriptions management page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        status = request.args.get('status', '')
        search = request.args.get('search', '')
        
        # Start with base query
        query = Subscription.query
        
        # Apply status filter if provided
        if status:
            try:
                # Use the status value directly since it's already lowercase
                status_enum = SubscriptionStatus(status)
                query = query.filter(Subscription.status == status_enum)
            except (KeyError, ValueError) as e:
                current_app.logger.warning(f"Invalid subscription status: {status}. Error: {str(e)}")
        
        # Apply search filter if provided
        if search:
            query = query.join(User).filter(
                or_(
                    User.name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )
        
        # Order by newest first and paginate
        subscriptions = query.order_by(Subscription.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/subscriptions.html', 
                             subscriptions=subscriptions,
                             status=status,
                             search=search)
    except Exception as e:
        current_app.logger.error(f"Error loading subscriptions: {str(e)}")
        flash('Error loading subscriptions', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/newsletters')
@login_required
@admin_required
def admin_newsletters():
    """Admin newsletter subscribers management page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        search = request.args.get('search', '')
        date_range = request.args.get('date_range', '')
        
        # Build query
        query = Newsletter.query
        
        # Apply search filter if provided
        if search:
            query = query.filter(Newsletter.email.ilike(f'%{search}%'))
        
        # Apply date range filter
        today = datetime.now().date()
        if date_range == 'today':
            query = query.filter(func.date(Newsletter.created_at) == today)
        elif date_range == 'week':
            week_ago = today - timedelta(days=7)
            query = query.filter(func.date(Newsletter.created_at) >= week_ago)
        elif date_range == 'month':
            month_ago = today - timedelta(days=30)
            query = query.filter(func.date(Newsletter.created_at) >= month_ago)
        
        # Order by newest first
        query = query.order_by(Newsletter.created_at.desc())
        
        # Paginate results
        newsletters = query.paginate(page=page, per_page=per_page)
        
        # Count new subscribers today
        new_today = Newsletter.query.filter(
            func.date(Newsletter.created_at) == today
        ).count()
        
        # Calculate total pages
        total_pages = (newsletters.total + per_page - 1) // per_page
        
        return render_template('admin/newsletters.html',
                             newsletters=newsletters,
                             today=today,
                             new_today=new_today,
                             total_pages=total_pages,
                             current_search=search,
                             current_date_range=date_range)
    except Exception as e:
        current_app.logger.error(f"Error loading newsletters: {str(e)}")
        flash('Error loading newsletters', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/service-requests')
@login_required
@admin_required
def admin_service_requests():
    """Admin service requests management page"""
    return render_template('admin/service_requests.html', pages=1)

@admin_bp.route('/add/location', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_location():
    """Admin add location page"""
    from database.models import DeliveryLocation, db
    from sqlalchemy import text
    from flask import current_app, request, flash, redirect, url_for
    
    if request.method == 'POST':
        city = request.form.get('city')
        province = request.form.get('province')
        is_active = 'is_active' in request.form
        
        # Validate inputs
        if not city or not province:
            flash('City and province are required', 'error')
            return redirect(url_for('admin.admin_add_location'))
        
        # Check if location already exists
        existing_location = DeliveryLocation.query.filter_by(
            city=city,
            province=province
        ).first()
        
        if existing_location:
            flash(f'A location for {city}, {province} already exists', 'error')
            return redirect(url_for('admin.admin_location_tree'))
        
        try:
            # Clear session to ensure clean state
            db.session.expire_all()
            
            # Create new location
            new_location = DeliveryLocation(
                city=city,
                province=province,
                postal_code_prefix='',  # Set to empty string instead of NULL
                is_active=is_active
            )
            
            db.session.add(new_location)
            db.session.commit()
            
            # Log the new location
            current_app.logger.info(f"Added new location: {province} - {city}, active: {is_active}")
            
            flash('Location added successfully', 'success')
            return redirect(url_for('admin.admin_location_tree'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding location: {str(e)}")
            flash(f'Error adding location: {str(e)}', 'error')
            return redirect(url_for('admin.admin_add_location'))
    
    return render_template('admin/add_location.html')

@admin_bp.route('/locations/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_location(id):
    """Admin edit location page"""
    from database.models import DeliveryLocation, db
    from flask import current_app, request, flash, redirect, url_for
    
    # Get the location
    location = DeliveryLocation.query.get_or_404(id)
    
    if request.method == 'POST':
        city = request.form.get('city')
        province = request.form.get('province')
        is_active = 'is_active' in request.form
        
        # Validate inputs
        if not city or not province:
            flash('All fields are required', 'error')
            return redirect(url_for('admin.admin_edit_location', id=id))
        
        # Check if another location with the same city+province exists
        existing_location = DeliveryLocation.query.filter(
            DeliveryLocation.city == city,
            DeliveryLocation.province == province,
            DeliveryLocation.id != id
        ).first()
        
        if existing_location:
            flash(f'A location for {city}, {province} already exists', 'error')
            return redirect(url_for('admin.admin_location_tree'))
        
        try:
            # Update location
            location.city = city
            location.province = province
            location.is_active = is_active
            
            db.session.commit()
            
            flash('Location updated successfully', 'success')
            return redirect(url_for('admin.admin_location_tree'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating location: {str(e)}")
            flash(f'Error updating location: {str(e)}', 'error')
            return redirect(url_for('admin.admin_edit_location', id=id))
    
    return render_template('admin/edit_location.html', location=location)

@admin_bp.route('/notifications')
@login_required
@admin_required
def admin_notifications():
    """Admin notifications management page"""
    form = NotificationForm()
    
    # Get all users with push subscriptions
    users = User.query.join(PushSubscription).all()
    
    # Get subscription stats
    subscription_count = User.query.count()
    email_subscribers_count = User.query.filter(User.email.isnot(None)).count()
    push_subscribers_count = PushSubscription.query.count()
    sms_subscribers_count = User.query.filter(User.phone.isnot(None)).count()
    
    # Get recent notifications
    recent_notifications = Notification.query.order_by(desc(Notification.created_at)).limit(20).all()
    
    return render_template(
        'admin/send_notifications.html',
        form=form,
        users=users,
        subscription_count=subscription_count,
        email_subscribers_count=email_subscribers_count,
        push_subscribers_count=push_subscribers_count,
        sms_subscribers_count=sms_subscribers_count,
        recent_notifications=recent_notifications
    )

@admin_bp.route('/send-notification', methods=['POST'])
@login_required
@admin_required
def send_notification():
    """Handle sending notifications through multiple channels"""
    form = NotificationForm()
    
    if form.validate_on_submit():
        title = form.title.data
        message = form.message.data
        email_subject = form.email_subject.data
        email_content = form.email_content.data
        recipient_type = form.recipient_type.data
        user_id = form.user_id.data if form.recipient_type.data == 'specific' else None
        notification_type = form.notification_type.data
        channels = form.channels.data
        
        # Get users based on recipient type
        if recipient_type == 'specific' and user_id:
            users = User.query.filter_by(id=user_id).all()
        elif recipient_type == 'subscribers':
            users = User.query.join(Subscription).filter(Subscription.status == 'active').all()
        else:
            users = User.query.all()
        
        if not users:
            flash('No users found matching the criteria.', 'warning')
            return redirect(url_for('admin.admin_notifications'))
        
        # Create notification record
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            recipient_count=len(users)
        )
        db.session.add(notification)
        db.session.commit()
        
        # Send notifications through selected channels
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                # Send push notification if selected
                if 'push' in channels:
                    subscription = PushSubscription.query.filter_by(user_id=user.id).first()
                    if subscription:
                        try:
                            send_push_notification(subscription, title, message, notification_type)
                            sent_count += 1
                        except Exception as e:
                            logger.error(f"Failed to send push notification to user {user.id}: {str(e)}")
                            failed_count += 1
                
                # Send email if selected
                if 'email' in channels and user.email:
                    try:
                        send_email(
                            to_email=user.email,
                            from_email=os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@healthyrizz.ca'),
                            subject=email_subject,
                            text_content=email_content,
                            html_content=render_template('email/notification.html',
                                user=user,
                                title=title,
                                message=message,
                                content=email_content
                            )
                        )
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send email to user {user.id}: {str(e)}")
                        failed_count += 1
                
                # Send SMS if selected
                if 'sms' in channels and user.phone:
                    try:
                        send_sms(user.phone, message)
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send SMS to user {user.id}: {str(e)}")
                        failed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process notifications for user {user.id}: {str(e)}")
                failed_count += 1
        
        # Update notification record with results
        notification.sent_count = sent_count
        db.session.commit()
        
        flash(f'Notification sent to {sent_count} users ({failed_count} failed).', 'success')
        return redirect(url_for('admin.admin_notifications'))
    
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Error in {field}: {error}', 'danger')
    
    return redirect(url_for('admin.admin_notifications'))

def send_push_notification(subscription, title, message, notification_type):
    """Helper function to send push notification"""
    import pywebpush
    from flask import request
    
    # Get VAPID keys from environment variables
    vapid_private_key = os.environ.get('VAPID_PRIVATE_KEY')
    vapid_public_key = os.environ.get('VAPID_PUBLIC_KEY')
    
    if not vapid_private_key or not vapid_public_key:
        raise Exception('VAPID keys not configured')
    
    # Set up VAPID claims
    vapid_claims = {
        'sub': f"mailto:{os.environ.get('VAPID_CONTACT_EMAIL', 'admin@healthyrizz.ca')}",
        'aud': request.host_url
    }
    
    # Format subscription for pywebpush
    sub_info = {
        'endpoint': subscription.endpoint,
        'keys': {
            'p256dh': subscription.p256dh,
            'auth': subscription.auth
        }
    }
    
    # Notification data
    notification_data = json.dumps({
        'title': title,
        'message': message,
        'type': notification_type
    })
    
    # Send the notification
    pywebpush.webpush(
        subscription_info=sub_info,
        data=notification_data,
        vapid_private_key=vapid_private_key,
        vapid_claims=vapid_claims
    )
    
    # Update last_used timestamp
    subscription.last_used = datetime.utcnow()
    db.session.commit()

@admin_bp.route('/notifications/history')
@login_required
@admin_required
def notification_history():
    """View notification history"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    notifications = Notification.query.order_by(desc(Notification.created_at)).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/notification_history.html', notifications=notifications)


@admin_bp.route('/locations/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_location(id):
    """Delete a location"""
    from database.models import DeliveryLocation, db
    from flask import current_app, flash, redirect, url_for
    
    location = DeliveryLocation.query.get_or_404(id)
    
    try:
        db.session.delete(location)
        db.session.commit()
        flash('Location deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting location: {str(e)}")
        flash(f'Error deleting location: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin_location_tree'))

# Coupon Management Routes
@admin_bp.route('/coupons')
@login_required
@admin_required
def admin_coupons():
    """Admin coupons management page"""
    from database.models import CouponCode
    try:
        # Get all coupons
        coupons = CouponCode.query.all()
        return render_template('admin/coupons.html', coupons=coupons)
    except Exception as e:
        current_app.logger.error(f"Error loading coupons: {str(e)}")
        flash('Error loading coupons', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/coupons/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_coupon(id):
    """Delete a coupon"""
    try:
        coupon = CouponCode.query.get_or_404(id)
        db.session.delete(coupon)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Coupon deleted successfully'})
    except Exception as e:
        current_app.logger.error(f"Error deleting coupon: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while deleting the coupon'}), 500

@admin_bp.route('/coupons/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_coupon(id):
    """Edit a coupon"""
    try:
        coupon = CouponCode.query.get_or_404(id)
        form = CouponForm(obj=coupon)
        
        if request.method == 'POST':
            if form.validate_on_submit():
                # Check if code is being changed and if it already exists
                if form.code.data != coupon.code:
                    existing_coupon = CouponCode.query.filter_by(code=form.code.data).first()
                    if existing_coupon:
                        flash('A coupon with this code already exists', 'error')
                        return redirect(url_for('admin.admin_edit_coupon', id=id))
                
                # Update coupon
                coupon.code = form.code.data
                coupon.discount_type = form.discount_type.data
                coupon.discount_value = form.discount_value.data
                coupon.min_order_value = form.min_order_value.data or 0
                coupon.valid_from = form.valid_from.data
                coupon.valid_to = form.valid_to.data
                coupon.max_uses = form.max_uses.data
                coupon.is_single_use = form.is_single_use.data
                coupon.is_active = form.is_active.data
                
                db.session.commit()
                flash('Coupon updated successfully', 'success')
                return redirect(url_for('admin.admin_coupons'))
        
        return render_template('admin/edit_coupon.html', form=form, coupon=coupon)
    except Exception as e:
        current_app.logger.error(f"Error editing coupon: {str(e)}")
        flash('Error editing coupon', 'error')
        return redirect(url_for('admin.admin_coupons'))

# FAQ Management Routes
@admin_bp.route('/faqs')
@login_required
@admin_required
def admin_faqs():
    """Admin FAQs management page"""
    from database.models import FAQ
    try:
        # Get all FAQs
        faqs = FAQ.query.all()
        return render_template('admin/faqs.html', faqs=faqs)
    except Exception as e:
        current_app.logger.error(f"Error loading FAQs: {str(e)}")
        flash('Error loading FAQs', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/faqs/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_faq(id):
    """Delete a FAQ"""
    try:
        faq = FAQ.query.get_or_404(id)
        db.session.delete(faq)
        db.session.commit()
        return jsonify({'success': True, 'message': 'FAQ deleted successfully'})
    except Exception as e:
        current_app.logger.error(f"Error deleting FAQ: {str(e)}")
        return jsonify({'success': False, 'message': 'Error deleting FAQ'}), 500

@admin_bp.route('/faqs/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_faq(id):
    """Edit a FAQ"""
    from database.models import FAQ, db
    
    faq = FAQ.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            faq.question = request.form.get('question')
            faq.answer = request.form.get('answer')
            faq.category = request.form.get('category')
            faq.order = int(request.form.get('order', 0))
            faq.is_active = request.form.get('is_active') == 'true'
            
            db.session.commit()
            flash('FAQ updated successfully', 'success')
            return redirect(url_for('admin.admin_faqs'))
        except Exception as e:
            current_app.logger.error(f"Error updating FAQ: {str(e)}")
            flash('Error updating FAQ', 'error')
    
    return render_template('admin/edit_faq.html', faq=faq)

@admin_bp.route('/faqs/toggle/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_toggle_faq(id):
    """Toggle FAQ status"""
    try:
        faq = FAQ.query.get_or_404(id)
        faq.is_active = not faq.is_active
        db.session.commit()
        return jsonify({'success': True, 'message': 'FAQ status updated successfully'})
    except Exception as e:
        current_app.logger.error(f"Error toggling FAQ status: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating FAQ status'}), 500

# Banner Management Routes
@admin_bp.route('/banners')
@login_required
@admin_required
def admin_banners():
    """Admin banners management page"""
    from database.models import Banner
    try:
        # Get all banners
        banners = Banner.query.order_by(Banner.created_at.desc()).all()
        return render_template('admin/banners.html', banners=banners)
    except Exception as e:
        current_app.logger.error(f"Error loading banners: {str(e)}")
        flash('Error loading banners', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/banners/toggle/<int:banner_id>', methods=['POST'])
@login_required
@admin_required
def admin_toggle_banner(banner_id):
    """Toggle banner active status"""
    try:
        banner = Banner.query.get_or_404(banner_id)
        banner.is_active = not banner.is_active
        db.session.commit()
        return jsonify({'success': True, 'message': 'Banner status updated successfully'})
    except Exception as e:
        current_app.logger.error(f"Error toggling banner status: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating banner status'}), 500

@admin_bp.route('/banners/delete/<int:banner_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_banner(banner_id):
    """Delete a banner"""
    try:
        banner = Banner.query.get_or_404(banner_id)
        db.session.delete(banner)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Banner deleted successfully'})
    except Exception as e:
        current_app.logger.error(f"Error deleting banner: {str(e)}")
        return jsonify({'success': False, 'message': 'Error deleting banner'}), 500

# Blog Management Routes
@admin_bp.route('/blog')
@login_required
@admin_required
def admin_blog():
    """Admin blog management page"""
    from database.models import BlogPost
    try:
        # Get all blog posts with author information
        posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        current_app.logger.info(f"Admin blog route - Found {len(posts)} blog posts")
        
        # Get unique categories
        categories = db.session.query(BlogPost.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        # Log post details for debugging
        for post in posts:
            current_app.logger.info(f"Admin blog post: {post.title} (ID: {post.id}, Published: {post.is_published}, Featured: {post.is_featured}, Created: {post.created_at})")
        
        return render_template('admin/blog.html', posts=posts, categories=categories)
    except Exception as e:
        current_app.logger.error(f"Error loading blog posts: {str(e)}")
        flash('Error loading blog posts', 'error')
        return render_template('admin/blog.html', posts=[], categories=[])

@admin_bp.route('/toggle-user-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user_status():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        return jsonify({'success': True, 'message': 'User status updated successfully'})
    except Exception as e:
        app.logger.error(f"Error toggling user status: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating user status'}), 500

@admin_bp.route('/toggle-admin-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_admin_status():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user = User.query.get_or_404(user_id)
        user.is_admin = not user.is_admin
        db.session.commit()
        return jsonify({'success': True, 'message': 'Admin status updated successfully'})
    except Exception as e:
        app.logger.error(f"Error toggling admin status: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating admin status'}), 500

@admin_bp.route('/delete-user', methods=['POST'])
@login_required
@admin_required
def admin_delete_user():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    except Exception as e:
        app.logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'success': False, 'message': 'Error deleting user'}), 500

@admin_bp.route('/toggle-meal-plan-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_meal_plan_status():
    try:
        data = request.get_json()
        meal_plan_id = data.get('meal_plan_id')
        
        if not meal_plan_id:
            return jsonify({'success': False, 'message': 'Meal plan ID is required'}), 400
            
        meal_plan = MealPlan.query.get(meal_plan_id)
        if not meal_plan:
            return jsonify({'success': False, 'message': 'Meal plan not found'}), 404
            
        meal_plan.is_active = not meal_plan.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Meal plan {"activated" if meal_plan.is_active else "deactivated"} successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling meal plan status: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while updating the meal plan status'}), 500

@admin_bp.route('/add-faq', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_faq():
    try:
        if request.method == 'POST':
            faq = FAQ(
                question=request.form.get('question'),
                answer=request.form.get('answer'),
                category=request.form.get('category'),
                order=int(request.form.get('order', 0))
            )
            db.session.add(faq)
            db.session.commit()
            flash('FAQ added successfully', 'success')
            return redirect(url_for('admin.admin_faqs'))
        return render_template('admin/add_faq.html')
    except Exception as e:
        app.logger.error(f"Error adding FAQ: {str(e)}")
        flash('Error adding FAQ', 'error')
        return redirect(url_for('admin.admin_faqs'))

@admin_bp.route('/add-banner', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_banner():
    try:
        if request.method == 'POST':
            # Get form data
            message = request.form.get('message')
            link_text = request.form.get('link_text')
            link_url = request.form.get('link_url')
            background_color = request.form.get('background_color', '#4CAF50')
            text_color = request.form.get('text_color', '#FFFFFF')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            is_active = 'is_active' in request.form

            # Validate required fields
            if not message or not start_date:
                flash('Message and start date are required', 'error')
                return redirect(url_for('admin.admin_add_banner'))

            # Validate dates
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                
                if end_date:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    if end_date < start_date:
                        flash('End date must be after start date', 'error')
                        return redirect(url_for('admin.admin_add_banner'))
                else:
                    end_date = None
            except ValueError:
                flash('Invalid date format', 'error')
                return redirect(url_for('admin.admin_add_banner'))

            # Create new banner
            banner = Banner(
                message=message,
                link_text=link_text if link_text else None,
                link_url=link_url if link_url else None,
                background_color=background_color,
                text_color=text_color,
                is_active=is_active,
                start_date=start_date,
                end_date=end_date
            )

            db.session.add(banner)
            db.session.commit()
            flash('Banner added successfully', 'success')
            return redirect(url_for('admin.admin_banners'))

        return render_template('admin/add_banner.html')
    except Exception as e:
        current_app.logger.error(f"Error adding banner: {str(e)}")
        flash('Error adding banner', 'error')
        return redirect(url_for('admin.admin_banners'))

@admin_bp.route('/add-coupon', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_coupon():
    """Add a new coupon"""
    try:
        form = CouponForm()
        if form.validate_on_submit():
            # Check if coupon code already exists
            existing_coupon = CouponCode.query.filter_by(code=form.code.data).first()
            if existing_coupon:
                flash('A coupon with this code already exists', 'error')
                return redirect(url_for('admin.admin_add_coupon'))
            
            # Create new coupon
            new_coupon = CouponCode(
                code=form.code.data,
                discount_type=form.discount_type.data,
                discount_value=form.discount_value.data,
                min_order_value=form.min_order_value.data or 0,
                valid_from=form.valid_from.data,
                valid_to=form.valid_to.data,
                max_uses=form.max_uses.data,
                is_single_use=form.is_single_use.data,
                is_active=form.is_active.data
            )
            
            db.session.add(new_coupon)
            db.session.commit()
            
            flash('Coupon added successfully', 'success')
            return redirect(url_for('admin.admin_coupons'))
            
        return render_template('admin/add_coupon.html', form=form, now=datetime.now())
    except Exception as e:
        current_app.logger.error(f"Error adding coupon: {str(e)}")
        flash('Error adding coupon', 'error')
        return redirect(url_for('admin.admin_coupons'))

@admin_bp.route('/add-blog-post', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_blog_post():
    """Admin add blog post page"""
    try:
        # Predefined categories
        categories = [
            'Nutrition',
            'Fitness',
            'Wellness',
            'Recipes',
            'Lifestyle',
            'Health Tips',
            'Workout',
            'Diet'
        ]
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('title')
            content = request.form.get('content')
            category = request.form.get('category')
            custom_category = request.form.get('custom_category')
            
            # Use custom category if provided
            if category == 'custom' and custom_category:
                category = custom_category
            
            # Create slug from title
            slug = title.lower().replace(' ', '-')
            
            # Create new blog post
            blog_post = BlogPost(
                title=title,
                content=content,
                slug=slug,
                category=category,
                tags=request.form.get('tags'),
                is_published=request.form.get('is_published') == 'true',
                author_id=current_user.id,
                summary=content[:200] + '...' if len(content) > 200 else content
            )
            
            # Set published_date if post is published
            if blog_post.is_published:
                blog_post.published_date = datetime.now()
            
            # Handle featured image upload
            if 'image' in request.files:
                image = request.files['image']
                if image and image.filename:
                    filename = secure_filename(image.filename)
                    image_path = os.path.join('static', 'uploads', 'blog', filename)
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    image.save(image_path)
                    blog_post.featured_image = f'/static/uploads/blog/{filename}'
            
            db.session.add(blog_post)
            db.session.commit()
            
            flash('Blog post added successfully', 'success')
            return redirect(url_for('admin.admin_blog'))
            
        # GET request - show the form
        return render_template('admin/add_blog_post.html', categories=categories)
        
    except Exception as e:
        current_app.logger.error(f"Error adding blog post: {str(e)}")
        flash('Error adding blog post', 'error')
        return redirect(url_for('admin.admin_blog'))

@admin_bp.route('/delete-blog-post/<int:id>', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def delete_blog_post(id):
    try:
        blog_post = BlogPost.query.get_or_404(id)
        db.session.delete(blog_post)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Blog post deleted successfully'})
    except Exception as e:
        current_app.logger.error(f"Error deleting blog post: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/blog-post/<int:post_id>')
@login_required
@admin_required
def blog_post_detail(post_id):
    """View blog post details"""
    blog_post = BlogPost.query.get_or_404(post_id)
    return render_template('admin/blog_post_detail.html', post=blog_post)

@admin_bp.route('/toggle-blog-post-status/<int:post_id>', methods=['POST'])
@login_required
@admin_required
def toggle_blog_post_status(post_id):
    """Toggle blog post published status"""
    try:
        blog_post = BlogPost.query.get_or_404(post_id)
        blog_post.is_published = not blog_post.is_published
        db.session.commit()
        
        status = 'published' if blog_post.is_published else 'draft'
        flash(f'Blog post {status} successfully', 'success')
        return redirect(url_for('admin.admin_blog'))
    except Exception as e:
        current_app.logger.error(f"Error toggling blog post status: {str(e)}")
        flash('Error updating blog post status', 'error')
        return redirect(url_for('admin.admin_blog'))

@admin_bp.route('/banners/edit/<int:banner_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_banner(banner_id):
    """Edit a banner"""
    from database.models import Banner, db
    
    banner = Banner.query.get_or_404(banner_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            message = request.form.get('message')
            link_text = request.form.get('link_text')
            link_url = request.form.get('link_url')
            background_color = request.form.get('background_color', '#4CAF50')
            text_color = request.form.get('text_color', '#FFFFFF')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            is_active = 'is_active' in request.form

            # Validate required fields
            if not message or not start_date:
                flash('Message and start date are required', 'error')
                return redirect(url_for('admin.admin_edit_banner', banner_id=banner_id))

            # Validate dates
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                
                if end_date:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    if end_date < start_date:
                        flash('End date must be after start date', 'error')
                        return redirect(url_for('admin.admin_edit_banner', banner_id=banner_id))
                else:
                    end_date = None
            except ValueError:
                flash('Invalid date format', 'error')
                return redirect(url_for('admin.admin_edit_banner', banner_id=banner_id))

            # Update banner
            banner.message = message
            banner.link_text = link_text if link_text else None
            banner.link_url = link_url if link_url else None
            banner.background_color = background_color
            banner.text_color = text_color
            banner.is_active = is_active
            banner.start_date = start_date
            banner.end_date = end_date

            db.session.commit()
            flash('Banner updated successfully', 'success')
            return redirect(url_for('admin.admin_banners'))
        except Exception as e:
            current_app.logger.error(f"Error updating banner: {str(e)}")
            flash('Error updating banner', 'error')
    
    return render_template('admin/edit_banner.html', banner=banner)

@admin_bp.route('/newsletters/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_newsletter(id):
    """Delete a newsletter subscriber"""
    try:
        newsletter = Newsletter.query.get_or_404(id)
        db.session.delete(newsletter)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Newsletter subscriber deleted successfully'})
    except Exception as e:
        current_app.logger.error(f"Error deleting newsletter subscriber: {str(e)}")
        return jsonify({'success': False, 'message': 'Error deleting newsletter subscriber'}), 500

@admin_bp.route('/newsletters/export')
@login_required
@admin_required
def admin_export_newsletters():
    """Export newsletter subscribers to CSV"""
    try:
        from io import StringIO
        import csv
        
        # Create a StringIO object to write CSV data
        si = StringIO()
        cw = csv.writer(si)
        
        # Write header
        cw.writerow(['Email', 'Subscribed On', 'Status'])
        
        # Write data
        newsletters = Newsletter.query.all()
        for newsletter in newsletters:
            cw.writerow([
                newsletter.email,
                newsletter.created_at.strftime('%Y-%m-%d %H:%M') if newsletter.created_at else 'N/A',
                'Active'
            ])
        
        # Create the response
        output = si.getvalue()
        si.close()
        
        return Response(
            output,
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=newsletter_subscribers.csv'
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error exporting newsletters: {str(e)}")
        flash('Error exporting newsletters', 'error')
        return redirect(url_for('admin.admin_newsletters'))

@admin_bp.route('/locations/toggle-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_location_status():
    """Toggle location active status"""
    try:
        data = request.get_json()
        location_id = data.get('location_id')
        
        if not location_id:
            return jsonify({'success': False, 'message': 'Location ID is required'}), 400
            
        location = DeliveryLocation.query.get(location_id)
        if not location:
            return jsonify({'success': False, 'message': 'Location not found'}), 404
            
        location.is_active = not location.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Location {"activated" if location.is_active else "deactivated"} successfully',
            'is_active': location.is_active
        })
    except Exception as e:
        current_app.logger.error(f"Error toggling location status: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@admin_bp.route('/subscriptions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_subscription(id):
    """Edit a subscription"""
    try:
        subscription = Subscription.query.get_or_404(id)
        meal_plans = MealPlan.query.filter_by(is_active=True).all()
    
        if request.method == 'POST':
            # Get form data and convert to uppercase
            status = request.form.get('status', '').upper()
            meal_plan_id = request.form.get('meal_plan_id')
            next_meal_plan_id = request.form.get('next_meal_plan_id')
            frequency = request.form.get('frequency', '').upper()
            stripe_subscription_id = request.form.get('stripe_subscription_id') or None
            stripe_customer_id = request.form.get('stripe_customer_id') or None
            cancel_at_period_end = 'cancel_at_period_end' in request.form
            pause_collection = 'pause_collection' in request.form
            price = request.form.get('price')
            next_price = request.form.get('next_price')
            
            # Get date fields
            start_date_str = request.form.get('start_date')
            current_period_start_str = request.form.get('current_period_start')
            current_period_end_str = request.form.get('current_period_end')
            
            # Validate inputs
            if not meal_plan_id or not status or not frequency or not price:
                flash('All required fields must be filled', 'error')
                return redirect(url_for('admin.admin_edit_subscription', id=id))
            
            try:
                # Convert status and frequency to enum values
                status_enum = SubscriptionStatus(status)
                frequency_enum = SubscriptionFrequency(frequency)
                
                # Update subscription
                subscription.meal_plan_id = int(meal_plan_id)
                if next_meal_plan_id:
                    subscription.next_meal_plan_id = int(next_meal_plan_id)
                subscription.status = status_enum
                subscription.frequency = frequency_enum
                subscription.stripe_subscription_id = stripe_subscription_id
                subscription.stripe_customer_id = stripe_customer_id
                subscription.cancel_at_period_end = cancel_at_period_end
                subscription.pause_collection = pause_collection
                subscription.price = float(price)
                if next_price:
                    subscription.next_price = float(next_price)
                
                # Update dates if provided
                if start_date_str:
                    subscription.start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                if current_period_start_str:
                    subscription.current_period_start = datetime.strptime(current_period_start_str, '%Y-%m-%d')
                if current_period_end_str:
                    subscription.current_period_end = datetime.strptime(current_period_end_str, '%Y-%m-%d')
                
                db.session.commit()
                flash('Subscription updated successfully', 'success')
                return redirect(url_for('admin.admin_subscriptions'))
            except ValueError as e:
                db.session.rollback()
                flash(f'Invalid input: {str(e)}', 'error')
                return redirect(url_for('admin.admin_edit_subscription', id=id))
        
        return render_template('admin/edit_subscription.html', 
                             subscription=subscription,
                             meal_plans=meal_plans,
                             subscription_statuses=SubscriptionStatus,
                             subscription_frequencies=SubscriptionFrequency)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating subscription: {str(e)}")
        flash('Error updating subscription', 'error')
        return redirect(url_for('admin.admin_subscriptions'))

@admin_bp.route('/orders/export/<date>')
@login_required
@admin_required
def admin_export_orders(date):
    """Export orders for a specific date"""
    try:
        # Parse the date
        try:
            selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('admin.admin_orders'))
        
        # Get orders for the date using get_daily_orders
        from utils.report_utils import get_daily_orders
        orders = get_daily_orders(selected_date)
        
        # Create HTML content
        html_content = """
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                .filters {
                    margin-bottom: 20px;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                }
                .filter-group {
                    margin-bottom: 10px;
                }
                .filter-group label {
                    font-weight: bold;
                    margin-right: 10px;
                }
                select, input {
                    padding: 5px;
                    margin-right: 15px;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                tr.skipped {
                    background-color: #ffebee;
                }
                tr.skipped td {
                    color: #d32f2f;
                }
                .status-skipped {
                    font-weight: bold;
                    color: #d32f2f;
                }
                .filter-button {
                    padding: 5px 15px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                }
                .filter-button:hover {
                    background-color: #45a049;
                }
            </style>
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Add event listeners to filter inputs
                    document.getElementById('cityFilter').addEventListener('input', filterTable);
                    document.getElementById('mealFilter').addEventListener('change', filterTable);
                });

                function filterTable() {
                    const cityFilter = document.getElementById('cityFilter').value.toLowerCase();
                    const mealFilter = document.getElementById('mealFilter').value.toLowerCase();
                    const table = document.querySelector('table');
                    const rows = table.getElementsByTagName('tr');

                    // Start from index 1 to skip header row
                    for (let i = 1; i < rows.length; i++) {
                        const row = rows[i];
                        const city = row.cells[5].textContent.toLowerCase();
                        const meal = row.cells[8].textContent.toLowerCase();
                        
                        // Check if meal is vegetarian
                        const isVegetarian = meal.includes('vegetarian') || meal.includes('veg');
                        
                        // Apply filters
                        const cityMatch = cityFilter === '' || city.includes(cityFilter);
                        const mealMatch = mealFilter === '' || 
                            (mealFilter === 'veg' && isVegetarian) ||
                            (mealFilter === 'nonveg' && !isVegetarian);
                        
                        // Show/hide row based on filters
                        row.style.display = (cityMatch && mealMatch) ? '' : 'none';
                    }
                }

                function resetFilters() {
                    document.getElementById('cityFilter').value = '';
                    document.getElementById('mealFilter').value = '';
                    const table = document.querySelector('table');
                    const rows = table.getElementsByTagName('tr');
                    
                    // Show all rows except header
                    for (let i = 1; i < rows.length; i++) {
                        rows[i].style.display = '';
                    }
                }
            </script>
        </head>
        <body>
            <div class="filters">
                <div class="filter-group">
                    <label>Filter by City:</label>
                    <input type="text" id="cityFilter" placeholder="Enter city name">
                </div>
                <div class="filter-group">
                    <label>Filter by Meal Type:</label>
                    <select id="mealFilter">
                        <option value="">All Meals</option>
                        <option value="veg">Vegetarian</option>
                        <option value="nonveg">Non-Vegetarian</option>
                    </select>
                </div>
                <button class="filter-button" onclick="resetFilters()" style="background-color: #666;">Reset Filters</button>
            </div>
            <table>
                <tr>
                    <th>Order ID</th>
                    <th>Customer Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Address</th>
                    <th>City</th>
                    <th>Province</th>
                    <th>Postal Code</th>
                    <th>Meal Plan</th>
                    <th>Status</th>
                    <th>Delivery Date</th>
                    <th>Created At</th>
                    <th>Tracking Number</th>
                    <th>Notes</th>
                    <th>Is Skipped</th>
                </tr>
        """
        
        # Add rows
        for order in orders:
            # Get delivery details if available
            delivery = order.get('delivery', {})
            tracking_number = delivery.get('tracking_number', 'N/A') if delivery else 'N/A'
            notes = delivery.get('notes', 'N/A') if delivery else 'N/A'
            
            # Check if delivery is skipped/cancelled
            is_skipped = order.get('delivery_status', '') == 'cancelled'
            
            # Add a prefix to the status if it's skipped
            status = order.get('delivery_status', 'N/A')
            if is_skipped:
                status = f'<span class="status-skipped">SKIPPED - {status}</span>'
            
            # Create row with appropriate class
            row_class = ' class="skipped"' if is_skipped else ''
            html_content += f"""
                <tr{row_class}>
                    <td>{order.get('subscription_id', 'N/A')}</td>
                    <td>{order.get('user_name', 'N/A')}</td>
                    <td>{order.get('user_email', 'N/A')}</td>
                    <td>{order.get('user_phone', 'N/A')}</td>
                    <td>{order.get('delivery_address', 'N/A')}</td>
                    <td>{order.get('delivery_city', 'N/A')}</td>
                    <td>{order.get('delivery_province', 'N/A')}</td>
                    <td>{order.get('delivery_postal_code', 'N/A')}</td>
                    <td>{order.get('meal_plan_name', 'N/A')}</td>
                    <td>{status}</td>
                    <td>{order.get('delivery_date', 'N/A')}</td>
                    <td>{order.get('created_at', 'N/A')}</td>
                    <td>{tracking_number}</td>
                    <td>{notes}</td>
                    <td>{'YES' if is_skipped else 'NO'}</td>
                </tr>
            """
        
        # Close HTML
        html_content += """
            </table>
        </body>
        </html>
        """
        
        return Response(
            html_content,
            mimetype='text/html',
            headers={
                'Content-Disposition': f'attachment; filename=orders_{date}.html'
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error exporting orders: {str(e)}")
        flash('Error exporting orders', 'error')
        return redirect(url_for('admin.admin_orders'))

@admin_bp.route('/subscriptions/view/<int:id>')
@login_required
@admin_required
def admin_view_subscription(id):
    """View subscription details"""
    try:
        subscription = Subscription.query.get_or_404(id)
        return render_template('admin/view_subscription.html', subscription=subscription)
    except Exception as e:
        current_app.logger.error(f"Error viewing subscription: {str(e)}")
        flash('Error viewing subscription', 'error')
        return redirect(url_for('admin.admin_subscriptions'))

@admin_bp.route('/orders/labels')
@login_required
@admin_required
def admin_labels():
    """Label management page"""
    try:
        # Get today's date
        today = datetime.now().date()
        
        # Get date from query parameters or use today
        date_str = request.args.get('date')
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = today
        else:
            selected_date = today
            
        # Get orders for the selected date
        orders = Delivery.query.filter(
            func.date(Delivery.delivery_date) == selected_date
        ).all()
        
        return render_template('admin/labels.html',
                             orders=orders,
                             selected_date=selected_date,
                             today=today)
    except Exception as e:
        current_app.logger.error(f"Error loading labels page: {str(e)}")
        flash('Error loading labels page', 'error')
        return redirect(url_for('admin.admin_orders'))

@admin_bp.route('/orders/labels/edit/<int:delivery_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_label(delivery_id):
    """Edit label details"""
    try:
        delivery = Delivery.query.get_or_404(delivery_id)
        
        if request.method == 'POST':
            # Update delivery details
            delivery.tracking_number = request.form.get('tracking_number')
            delivery.delivery_time = datetime.strptime(
                request.form.get('delivery_time'), '%H:%M'
            ).time() if request.form.get('delivery_time') else None
            
            # Update meal details
            delivery.meal_notes = request.form.get('meal_notes')
            delivery.special_instructions = request.form.get('special_instructions')
            
            db.session.commit()
            flash('Label details updated successfully', 'success')
            return redirect(url_for('admin.admin_labels', date=delivery.delivery_date.strftime('%Y-%m-%d')))
            
        return render_template('admin/edit_label.html', delivery=delivery)
    except Exception as e:
        current_app.logger.error(f"Error editing label: {str(e)}")
        flash('Error editing label', 'error')
        return redirect(url_for('admin.admin_labels'))

@admin_bp.route('/orders/generate-labels/<date>')
@login_required
@admin_required
def admin_generate_labels(date):
    """Generate shipping labels for orders on a specific date"""
    try:
        # Parse the date
        try:
            selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('admin.admin_orders'))
        
        # Get orders for the date
        from utils.report_utils import get_daily_orders
        orders = get_daily_orders(selected_date)
        if not orders:
            flash('No orders found for this date', 'error')
            return redirect(url_for('admin.admin_orders'))
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=(4*inch, 4*inch), rightMargin=0.25*inch, leftMargin=0.25*inch, topMargin=0.25*inch, bottomMargin=0.25*inch)
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#379777')
        )
        label_style = ParagraphStyle(
            'CustomLabel',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#CCCCCC')
        )
        value_style = ParagraphStyle(
            'CustomValue',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#FFFFFF')
        )
        
        # Build PDF content
        elements = []
        
        # Add logo if exists
        logo_path = os.path.join(current_app.static_folder, 'images', 'logo.png')
        if os.path.exists(logo_path):
            img = Image(logo_path, width=1.5*inch, height=0.75*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.1*inch))
        
        # Add header
        elements.append(Paragraph(f"HealthyRizz Delivery", title_style))
        elements.append(Paragraph(f"Date: {selected_date.strftime('%B %d, %Y')}", label_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Process each order
        for order in orders:
            try:
                # Skip cancelled deliveries
                if order.get('is_skipped', False):
                    continue
                    
                # Get customer and delivery details
                customer_name = order.get('user_name', 'N/A')
                delivery_address = order.get('delivery_address', 'N/A')
                delivery_city = order.get('delivery_city', 'N/A')
                meal_plan_name = order.get('meal_plan_name', 'N/A')
                meal_type = 'Vegetarian' if order.get('is_vegetarian', False) else 'Non-Vegetarian'
                tracking_number = order.get('tracking_number', 'N/A')
                special_instructions = order.get('notes', '')
                
                # Create label data
                label_data = [
                    ['Customer:', customer_name],
                    ['Address:', delivery_address],
                    ['City:', delivery_city],
                    ['Meal Plan:', meal_plan_name],
                    ['Meal Type:', meal_type],
                    ['Tracking:', tracking_number]
                ]
                
                # Add special instructions if any
                if special_instructions:
                    label_data.append(['Instructions:', special_instructions])
                
                # Create table
                table = Table(label_data, colWidths=[1.5*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#333333')),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#252525')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#CCCCCC')),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#FFFFFF')),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(table)
                elements.append(PageBreak())
                
            except Exception as e:
                current_app.logger.error(f"Error processing order: {str(e)}")
                continue
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'shipping_labels_{date}.pdf'
        )
    except Exception as e:
        flash(f'Error generating labels: {str(e)}', 'error')
        return redirect(url_for('admin.admin_orders'))

@admin_bp.route('/edit-province', methods=['POST'])
@login_required
@admin_required
def edit_province():
    """Add cities to an existing province"""
    try:
        province_code = request.form.get('province_code')
        cities_str = request.form.get('cities', '')
        
        if not province_code or not cities_str:
            return jsonify({'success': False, 'message': 'Province code and cities are required'})
        
        # Check if province exists
        existing_locations = DeliveryLocation.query.filter_by(
            province=province_code,
            is_active=True
        ).first()
        
        if not existing_locations:
            return jsonify({'success': False, 'message': 'Province does not exist'})
        
        # Split cities string and clean up
        cities = [city.strip() for city in cities_str.split(',') if city.strip()]
        
        # Add each new city
        for city in cities:
            # Check if city already exists
            existing = DeliveryLocation.query.filter_by(
                province=province_code,
                city=city,
                is_active=True
            ).first()
            
            if not existing:
                location = DeliveryLocation(
                    province=province_code,
                    city=city,
                    is_active=True
                )
                db.session.add(location)
            
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding cities: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})
        
@admin_bp.route('/delete-province/<province_code>', methods=['DELETE'])
@login_required
@admin_required
def delete_province(province_code):
    """Delete a province and all its cities"""
    try:
        # Soft delete all locations in this province
        DeliveryLocation.query.filter_by(province=province_code).update({'is_active': False})
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting province: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/delete-city/<int:city_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_city(city_id):
    """Delete a specific city"""
    try:
        # Soft delete the location
        location = DeliveryLocation.query.get_or_404(city_id)
        location.is_active = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting city: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/orders/update-status/<int:delivery_id>', methods=['POST'])
@login_required
@admin_required
def admin_update_delivery_status(delivery_id):
    """Update delivery status"""
    try:
        if not delivery_id:
            flash('Invalid delivery ID provided', 'error')
            return redirect(url_for('admin.admin_orders'))
            
        # Get the delivery record
        delivery = Delivery.query.get(delivery_id)
        if not delivery:
            flash('Delivery record not found', 'error')
            return redirect(url_for('admin.admin_orders'))
            
        new_status = request.form.get('status')
        if not new_status:
            flash('Please select a valid status', 'error')
            return redirect(url_for('admin.admin_orders'))
            
        try:
            # Update delivery status
            delivery.status = DeliveryStatus(new_status)
            
            # Add tracking number if status is delivered
            if new_status == 'delivered':
                delivery.tracking_number = f"TRK{delivery.id:06d}"
                
            db.session.commit()
            flash(f'Delivery status updated to {new_status.title()} successfully', 'success')
            
        except ValueError as ve:
            db.session.rollback()
            current_app.logger.error(f"Invalid status value: {str(ve)}")
            flash('Invalid status value provided', 'error')
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating delivery status: {str(e)}")
        flash('Failed to update delivery status. Please try again.', 'error')
        
    return redirect(url_for('admin.admin_orders'))

@admin_bp.route('/meal-plans/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_meal_plan(id):
    """Edit a meal plan"""
    try:
        meal_plan = MealPlan.query.get_or_404(id)
        
        if request.method == 'POST':
            # Get form data
            meal_plan.name = request.form.get('name')
            meal_plan.description = request.form.get('description')
            meal_plan.calories = request.form.get('calories')
            meal_plan.protein = request.form.get('protein')
            meal_plan.fat = request.form.get('fat')
            meal_plan.carbs = request.form.get('carbs')
            meal_plan.price_weekly = float(request.form.get('price_weekly'))
            meal_plan.price_monthly = float(request.form.get('price_monthly'))
            meal_plan.price_trial = float(request.form.get('price_trial', 14.99))
            meal_plan.is_active = request.form.get('is_active') == 'true'
            meal_plan.available_for_trial = request.form.get('available_for_trial') == 'true'
            meal_plan.includes_breakfast = request.form.get('includes_breakfast') == 'true'
            meal_plan.for_gender = request.form.get('for_gender', 'both')
            meal_plan.tag = request.form.get('tag')
            meal_plan.is_vegetarian = request.form.get('is_vegetarian') == 'true'
            meal_plan.is_vegan = request.form.get('is_vegan') == 'true'
            meal_plan.is_gluten_free = request.form.get('is_gluten_free') == 'true'
            meal_plan.is_dairy_free = request.form.get('is_dairy_free') == 'true'
            meal_plan.is_keto = request.form.get('is_keto') == 'true'
            meal_plan.is_paleo = request.form.get('is_paleo') == 'true'
            meal_plan.is_low_carb = request.form.get('is_low_carb') == 'true'
            meal_plan.is_high_protein = request.form.get('is_high_protein') == 'true'
            meal_plan.image_url = request.form.get('image_url')
            meal_plan.is_popular = request.form.get('is_popular') == 'true'
            
            db.session.commit()
            flash('Meal plan updated successfully', 'success')
            return redirect(url_for('admin.admin_meal_plans'))
            
        return render_template('admin/edit_meal_plan.html', meal_plan=meal_plan)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error editing meal plan: {str(e)}")
        flash('Error editing meal plan', 'error')
        return redirect(url_for('admin.admin_meal_plans'))

@admin_bp.route('/orders/generate-simple-labels/<date>')
@login_required
@admin_required
def admin_generate_simple_labels(date):
    """Generate simple shipping labels with minimal information - OPTIMIZED FOR SPEED"""
    try:
        # Parse the date
        try:
            selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('admin.admin_orders'))
        
        # Get orders for the date using optimized function
        from utils.report_utils import generate_simple_labels
        labels_pdf = generate_simple_labels(selected_date)
        
        if not labels_pdf:
            flash('No orders found for this date', 'error')
            return redirect(url_for('admin.admin_orders'))
        
        return send_file(
            labels_pdf,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'simple_labels_{date}.pdf'
        )
    except Exception as e:
        flash(f'Error generating simple labels: {str(e)}', 'error')
        return redirect(url_for('admin.admin_orders'))

@admin_bp.route('/edit-blog-post/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_blog_post(id):
    """Edit a blog post"""
    try:
        post = BlogPost.query.get_or_404(id)
        
        if request.method == 'POST':
            post.title = request.form.get('title')
            post.content = request.form.get('content')
            post.category = request.form.get('category')
            post.tags = request.form.get('tags')
            post.is_published = request.form.get('is_published') == 'true'
            
            # Update slug if title changed
            new_slug = post.title.lower().replace(' ', '-')
            if new_slug != post.slug:
                # Check if new slug already exists
                existing = BlogPost.query.filter_by(slug=new_slug).first()
                if existing and existing.id != post.id:
                    flash('A blog post with this title already exists', 'error')
                    return redirect(url_for('admin.admin_edit_blog_post', id=id))
                post.slug = new_slug
            
            # Handle featured image upload
            if 'image' in request.files:
                image = request.files['image']
                if image and image.filename:
                    filename = secure_filename(image.filename)
                    image_path = os.path.join('static', 'uploads', 'blog', filename)
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    image.save(image_path)
                    post.featured_image = f'/static/uploads/blog/{filename}'
            
            # Update published date if status changed to published
            if post.is_published and not post.published_date:
                post.published_date = datetime.now()
            
            db.session.commit()
            flash('Blog post updated successfully', 'success')
            return redirect(url_for('admin.admin_blog'))
        
        # Define available categories
        categories = [
            'Nutrition',
            'Fitness',
            'Wellness',
            'Recipes',
            'Lifestyle',
            'Health Tips',
            'Workout',
            'Diet'
        ]
        
        return render_template('admin/edit_blog_post.html', post=post, categories=categories)
    except Exception as e:
        current_app.logger.error(f"Error editing blog post: {str(e)}")
        flash('Error editing blog post', 'error')
        return redirect(url_for('admin.admin_blog'))

# Media Management Routes
@admin_bp.route('/media')
@login_required
@admin_required
def admin_media():
    """Media management dashboard"""
    try:
        hero_slides = HeroSlide.query.order_by(HeroSlide.order, HeroSlide.created_at).all()
        videos = Video.query.order_by(Video.order, Video.created_at).all()
        team_members = TeamMember.query.order_by(TeamMember.order, TeamMember.created_at).all()
        full_width_sections = FullWidthSection.query.order_by(FullWidthSection.order, FullWidthSection.created_at).all()
        # Fetch all site settings as a dictionary
        site_settings = {s.key: s.value for s in SiteSetting.query.all()}
        
        return render_template('admin/media.html',
                             hero_slides=hero_slides,
                             videos=videos,
                             team_members=team_members,
                             full_width_sections=full_width_sections,
                             site_settings=site_settings)
    except Exception as e:
        current_app.logger.error(f"Error loading media dashboard: {str(e)}")
        flash('An error occurred while loading the media dashboard.', 'error')
        return redirect(url_for('admin.admin_dashboard'))

# Hero Slides Management
@admin_bp.route('/media/hero-slides/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_hero_slide():
    """Add a new hero slide"""
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            image_url = request.form.get('image_url')
            image_file = request.files.get('image_file')
            order = int(request.form.get('order', 0))
            is_active = 'is_active' in request.form
            
            # Handle image upload
            final_image_url = image_url
            if image_file and image_file.filename:
                # Secure the filename and create upload path
                filename = secure_filename(image_file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                
                # Save the file
                image_file.save(file_path)
                final_image_url = f'/static/uploads/{filename}'
            
            hero_slide = HeroSlide(
                title=title,
                subtitle=subtitle,
                image_url=final_image_url,
                order=order,
                is_active=is_active
            )
            
            db.session.add(hero_slide)
            db.session.commit()
            
            flash('Hero slide added successfully!', 'success')
            return redirect(url_for('admin.admin_media'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding hero slide: {str(e)}")
            flash('An error occurred while adding the hero slide.', 'error')
    
    return render_template('admin/add_hero_slide.html')

@admin_bp.route('/media/hero-slides/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_hero_slide(id):
    """Edit a hero slide"""
    hero_slide = HeroSlide.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            hero_slide.title = request.form.get('title')
            hero_slide.subtitle = request.form.get('subtitle')
            image_url = request.form.get('image_url')
            image_file = request.files.get('image_file')
            hero_slide.order = int(request.form.get('order', 0))
            hero_slide.is_active = 'is_active' in request.form
            
            # Handle image upload
            if image_file and image_file.filename:
                # Secure the filename and create upload path
                filename = secure_filename(image_file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                
                # Save the file
                image_file.save(file_path)
                hero_slide.image_url = f'/static/uploads/{filename}'
            elif image_url:
                hero_slide.image_url = image_url
            
            db.session.commit()
            
            flash('Hero slide updated successfully!', 'success')
            return redirect(url_for('admin.admin_media'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating hero slide: {str(e)}")
            flash('An error occurred while updating the hero slide.', 'error')
    
    return render_template('admin/edit_hero_slide.html', hero_slide=hero_slide)

@admin_bp.route('/media/hero-slides/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_hero_slide(id):
    """Delete a hero slide"""
    try:
        hero_slide = HeroSlide.query.get_or_404(id)
        db.session.delete(hero_slide)
        db.session.commit()
        
        flash('Hero slide deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting hero slide: {str(e)}")
        flash('An error occurred while deleting the hero slide.', 'error')
    
    return redirect(url_for('admin.admin_media'))

# Videos Management
@admin_bp.route('/media/videos/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_video():
    """Add a new video - supports both YouTube and file upload"""
    from forms.video_forms import VideoUploadForm
    form = VideoUploadForm()
    
    if form.validate_on_submit():
        try:
            video_type = form.video_type.data
            title = form.title.data
            description = form.description.data
            order = form.order.data or 0
            is_active = form.is_active.data
            
            # Initialize video object
            video = Video(
                title=title,
                description=description,
                order=order,
                is_active=is_active,
                video_type=video_type
            )
            
            if video_type == 'youtube':
                # Handle YouTube video
                video.youtube_url = form.youtube_url.data
                
                # Handle custom thumbnail upload for YouTube
                if form.thumbnail_file.data:
                    thumbnail_file = form.thumbnail_file.data
                    filename = secure_filename(thumbnail_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = f"{timestamp}_{filename}"
                    
                    thumbnail_folder = os.path.join(current_app.root_path, 'static', 'images', 'video_thumbnails')
                    os.makedirs(thumbnail_folder, exist_ok=True)
                    thumbnail_path = os.path.join(thumbnail_folder, filename)
                    
                    thumbnail_file.save(thumbnail_path)
                    video.thumbnail_url = f'/static/images/video_thumbnails/{filename}'
                    
            elif video_type == 'upload':
                # Handle video file upload
                if form.video_file.data:
                    video_file = form.video_file.data
                    filename = secure_filename(video_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = f"{timestamp}_{filename}"
                    
                    # Save video file
                    video_folder = os.path.join(current_app.root_path, 'static', 'videos')
                    os.makedirs(video_folder, exist_ok=True)
                    video_path = os.path.join(video_folder, filename)
                    
                    video_file.save(video_path)
                    video.video_file = filename
                    
                    # Handle thumbnail upload for uploaded video
                    if form.thumbnail_file.data:
                        thumbnail_file = form.thumbnail_file.data
                        thumb_filename = secure_filename(thumbnail_file.filename)
                        thumb_filename = f"{timestamp}_thumb_{thumb_filename}"
                        
                        thumbnail_folder = os.path.join(current_app.root_path, 'static', 'images', 'video_thumbnails')
                        os.makedirs(thumbnail_folder, exist_ok=True)
                        thumbnail_path = os.path.join(thumbnail_folder, thumb_filename)
                        
                        thumbnail_file.save(thumbnail_path)
                        video.thumbnail_url = f'/static/images/video_thumbnails/{thumb_filename}'
                else:
                    flash('Please select a video file to upload.', 'error')
                    return render_template('admin/add_video.html', form=form)
            
            db.session.add(video)
            db.session.commit()
            
            flash(f'{video_type.title()} video added successfully!', 'success')
            return redirect(url_for('admin.admin_media'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding video: {str(e)}")
            flash(f'An error occurred while adding the video: {str(e)}', 'error')
    
    return render_template('admin/add_video.html', form=form)

@admin_bp.route('/media/videos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_video(id):
    """Edit a video - supports both YouTube and file upload"""
    from forms.video_forms import VideoEditForm
    video = Video.query.get_or_404(id)
    form = VideoEditForm(obj=video)
    
    if form.validate_on_submit():
        try:
            video_type = form.video_type.data
            video.title = form.title.data
            video.description = form.description.data
            video.order = form.order.data or 0
            video.is_active = form.is_active.data
            video.video_type = video_type
            
            if video_type == 'youtube':
                # Handle YouTube video
                video.youtube_url = form.youtube_url.data
                # Clear video file if switching from upload to YouTube
                video.video_file = None
                
                # Handle custom thumbnail upload for YouTube
                if form.thumbnail_file.data:
                    thumbnail_file = form.thumbnail_file.data
                    filename = secure_filename(thumbnail_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = f"{timestamp}_{filename}"
                    
                    thumbnail_folder = os.path.join(current_app.root_path, 'static', 'images', 'video_thumbnails')
                    os.makedirs(thumbnail_folder, exist_ok=True)
                    thumbnail_path = os.path.join(thumbnail_folder, filename)
                    
                    thumbnail_file.save(thumbnail_path)
                    video.thumbnail_url = f'/static/images/video_thumbnails/{filename}'
                    
            elif video_type == 'upload':
                # Handle video file upload
                if form.video_file.data:
                    video_file = form.video_file.data
                    filename = secure_filename(video_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = f"{timestamp}_{filename}"
                    
                    # Save video file
                    video_folder = os.path.join(current_app.root_path, 'static', 'videos')
                    os.makedirs(video_folder, exist_ok=True)
                    video_path = os.path.join(video_folder, filename)
                    
                    video_file.save(video_path)
                    video.video_file = filename
                    # Clear YouTube URL if switching from YouTube to upload
                    video.youtube_url = None
                    
                    # Handle thumbnail upload for uploaded video
                    if form.thumbnail_file.data:
                        thumbnail_file = form.thumbnail_file.data
                        thumb_filename = secure_filename(thumbnail_file.filename)
                        thumb_filename = f"{timestamp}_thumb_{thumb_filename}"
                        
                        thumbnail_folder = os.path.join(current_app.root_path, 'static', 'images', 'video_thumbnails')
                        os.makedirs(thumbnail_folder, exist_ok=True)
                        thumbnail_path = os.path.join(thumbnail_folder, thumb_filename)
                        
                        thumbnail_file.save(thumbnail_path)
                        video.thumbnail_url = f'/static/images/video_thumbnails/{thumb_filename}'
                elif not video.video_file:
                    # If no file uploaded and no existing file, require one
                    flash('Please select a video file to upload.', 'error')
                    return render_template('admin/edit_video.html', form=form, video=video)
            
            db.session.commit()
            
            flash(f'{video_type.title()} video updated successfully!', 'success')
            return redirect(url_for('admin.admin_media'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating video: {str(e)}")
            flash(f'An error occurred while updating the video: {str(e)}', 'error')
    
    return render_template('admin/edit_video.html', form=form, video=video)

@admin_bp.route('/media/videos/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_video(id):
    """Delete a video"""
    try:
        video = Video.query.get_or_404(id)
        db.session.delete(video)
        db.session.commit()
        
        flash('Video deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting video: {str(e)}")
        flash('An error occurred while deleting the video.', 'error')
    
    return redirect(url_for('admin.admin_media'))

# Team Members Management
@admin_bp.route('/media/team-members/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_team_member():
    """Add a new team member"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            position = request.form.get('position')
            bio = request.form.get('bio')
            image_url = request.form.get('image_url')
            image_file = request.files.get('image_file')
            order = int(request.form.get('order', 0))
            is_active = 'is_active' in request.form
            
            # Handle image upload
            final_image_url = image_url
            if image_file and image_file.filename:
                # Secure the filename and create upload path
                filename = secure_filename(image_file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                
                # Save the file
                image_file.save(file_path)
                final_image_url = f'/static/uploads/{filename}'
            
            team_member = TeamMember(
                name=name,
                position=position,
                bio=bio,
                image_url=final_image_url,
                order=order,
                is_active=is_active
            )
            
            db.session.add(team_member)
            db.session.commit()
            
            flash('Team member added successfully!', 'success')
            return redirect(url_for('admin.admin_media'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding team member: {str(e)}")
            flash('An error occurred while adding the team member.', 'error')
    
    return render_template('admin/add_team_member.html')

@admin_bp.route('/media/team-members/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_team_member(id):
    """Edit a team member"""
    team_member = TeamMember.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            team_member.name = request.form.get('name')
            team_member.position = request.form.get('position')
            team_member.bio = request.form.get('bio')
            image_url = request.form.get('image_url')
            image_file = request.files.get('image_file')
            team_member.order = int(request.form.get('order', 0))
            team_member.is_active = 'is_active' in request.form
            
            # Handle image upload
            if image_file and image_file.filename:
                # Secure the filename and create upload path
                filename = secure_filename(image_file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                
                # Save the file
                image_file.save(file_path)
                team_member.image_url = f'/static/uploads/{filename}'
            elif image_url:
                team_member.image_url = image_url
            
            db.session.commit()
            
            flash('Team member updated successfully!', 'success')
            return redirect(url_for('admin.admin_media'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating team member: {str(e)}")
            flash('An error occurred while updating the team member.', 'error')
    
    return render_template('admin/edit_team_member.html', team_member=team_member)

@admin_bp.route('/media/team-members/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_team_member(id):
    """Delete a team member"""
    try:
        team_member = TeamMember.query.get_or_404(id)
        db.session.delete(team_member)
        db.session.commit()
        
        flash('Team member deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting team member: {str(e)}")
        flash('An error occurred while deleting the team member.', 'error')
    
    return redirect(url_for('admin.admin_media'))

# Site Settings Management
@admin_bp.route('/media/site-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_site_settings():
    """Admin site settings page"""
    try:
        if request.method == 'POST':
            # Handle file uploads
            logo_file = request.files.get('site_logo_file')
            
            # Handle logo upload
            if logo_file and logo_file.filename:
                if allowed_file(logo_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}):
                    filename = secure_filename(f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{logo_file.filename}")
                    logo_path = os.path.join(current_app.root_path, 'static', 'images', filename)
                    os.makedirs(os.path.dirname(logo_path), exist_ok=True)
                    logo_file.save(logo_path)
                    SiteSetting.set_setting('site_logo', f'/static/images/{filename}', 'Site logo image')
                    flash('Logo updated successfully!', 'success')
                else:
                    flash('Invalid logo file format. Please use PNG, JPG, JPEG, GIF, SVG, or WEBP.', 'error')
            
            # Handle logo URL (only if provided and no file upload)
            logo_url = request.form.get('site_logo', '').strip()
            if logo_url and not logo_file:
                # Validate URL format if provided
                if logo_url.startswith(('http://', 'https://', '/static/')):
                    SiteSetting.set_setting('site_logo', logo_url, 'Site logo URL')
                    flash('Logo URL updated successfully!', 'success')
                else:
                    flash('Please enter a valid URL starting with http://, https://, or /static/', 'error')
                    return redirect(url_for('admin.admin_site_settings'))
            elif not logo_url and not logo_file:
                # Both fields are empty, which is fine - don't update logo
                pass
            elif logo_url == '' and not logo_file:
                # URL field is empty and no file uploaded - this is also fine
                pass
            
            # Handle other settings
            settings_to_update = {
                'company_name': request.form.get('company_name', ''),
                'hero_subtitle': request.form.get('hero_subtitle', ''),
                'contact_email': request.form.get('contact_email', ''),
                'contact_phone': request.form.get('contact_phone', ''),
                'fssai_license_number': request.form.get('fssai_license_number', ''),
                'hygiene_badge_text': request.form.get('hygiene_badge_text', ''),
                'facebook_url': request.form.get('facebook_url', ''),
                'instagram_url': request.form.get('instagram_url', '')
            }
            
            # Handle boolean settings
            show_fssai_badge = request.form.get('show_fssai_badge') == 'on'
            show_hygiene_badge = request.form.get('show_hygiene_badge') == 'on'
            
            settings_to_update['show_fssai_badge'] = str(show_fssai_badge)
            settings_to_update['show_hygiene_badge'] = str(show_hygiene_badge)
            
            # Update settings
            for key, value in settings_to_update.items():
                if value is not None:  # Only update if value is provided
                    SiteSetting.set_setting(key, value, f'{key.replace("_", " ").title()}')
            
            # If no files uploaded and no URLs provided, just show success message
            if not logo_file and not logo_url:
                flash('Site settings updated successfully!', 'success')
            
            return redirect(url_for('admin.admin_site_settings'))
        
        # Get current settings
        settings = {}
        site_settings = SiteSetting.query.all()
        for setting in site_settings:
            settings[setting.key] = setting.value
        
        return render_template('admin/site_settings.html', 
                             site_settings=settings,
                             now=datetime.now())
                             
    except Exception as e:
        current_app.logger.error(f"Error in admin_site_settings: {str(e)}")
        flash('An error occurred while updating site settings.', 'error')
        return redirect(url_for('admin.admin_dashboard'))

# Contact Inquiries Management
@admin_bp.route('/contact-inquiries')
@login_required
@admin_required
def admin_contact_inquiries():
    """Admin contact inquiries page"""
    try:
        # Get filter parameters
        inquiry_type = request.args.get('type')
        status = request.args.get('status')
        priority = request.args.get('priority')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Build query
        query = ContactInquiry.query
        
        if inquiry_type:
            query = query.filter(ContactInquiry.inquiry_type == inquiry_type)
        if status:
            query = query.filter(ContactInquiry.status == status)
        if priority:
            query = query.filter(ContactInquiry.priority == priority)
        
        # Order by priority and creation date
        query = query.order_by(
            ContactInquiry.priority.desc(),
            ContactInquiry.created_at.desc()
        )
        
        # Paginate
        inquiries = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get counts for filters
        total_inquiries = ContactInquiry.query.count()
        new_inquiries = ContactInquiry.query.filter_by(status='new').count()
        urgent_inquiries = ContactInquiry.query.filter_by(priority='urgent').count()
        
        # Get inquiry type counts
        type_counts = db.session.query(
            ContactInquiry.inquiry_type,
            func.count(ContactInquiry.id)
        ).group_by(ContactInquiry.inquiry_type).all()
        
        return render_template('admin/contact_inquiries.html',
                             inquiries=inquiries,
                             total_inquiries=total_inquiries,
                             new_inquiries=new_inquiries,
                             urgent_inquiries=urgent_inquiries,
                             type_counts=type_counts,
                             current_filters={
                                 'type': inquiry_type,
                                 'status': status,
                                 'priority': priority
                             })
    except Exception as e:
        current_app.logger.error(f"Error loading contact inquiries: {str(e)}")
        flash('An error occurred while loading contact inquiries.', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/contact-inquiries/<int:inquiry_id>')
@login_required
@admin_required
def admin_contact_inquiry_detail(inquiry_id):
    """Admin contact inquiry detail page"""
    try:
        inquiry = ContactInquiry.query.get_or_404(inquiry_id)
        
        return render_template('admin/contact_inquiry_detail.html', inquiry=inquiry)
    except Exception as e:
        current_app.logger.error(f"Error loading contact inquiry detail: {str(e)}")
        flash('An error occurred while loading the inquiry details.', 'error')
        return redirect(url_for('admin.admin_contact_inquiries'))

@admin_bp.route('/contact-inquiries/<int:inquiry_id>/update-status', methods=['POST'])
@login_required
@admin_required
def admin_update_inquiry_status(inquiry_id):
    """Update contact inquiry status"""
    try:
        inquiry = ContactInquiry.query.get_or_404(inquiry_id)
        new_status = request.form.get('status')
        notes = request.form.get('notes', '')
        
        if new_status in ['new', 'in_progress', 'contacted', 'resolved', 'closed']:
            inquiry.status = new_status
            inquiry.notes = notes
            inquiry.updated_at = datetime.utcnow()
            
            # Update timestamps based on status
            if new_status == 'contacted':
                inquiry.contacted_at = datetime.utcnow()
            elif new_status == 'resolved':
                inquiry.resolved_at = datetime.utcnow()
            
            db.session.commit()
            flash('Inquiry status updated successfully!', 'success')
        else:
            flash('Invalid status provided.', 'error')
        
        return redirect(url_for('admin.admin_contact_inquiry_detail', inquiry_id=inquiry_id))
    except Exception as e:
        current_app.logger.error(f"Error updating inquiry status: {str(e)}")
        flash('An error occurred while updating the inquiry status.', 'error')
        return redirect(url_for('admin.admin_contact_inquiries'))

@admin_bp.route('/contact-inquiries/<int:inquiry_id>/update-priority', methods=['POST'])
@login_required
@admin_required
def admin_update_inquiry_priority(inquiry_id):
    """Update contact inquiry priority"""
    try:
        inquiry = ContactInquiry.query.get_or_404(inquiry_id)
        new_priority = request.form.get('priority')
        
        if new_priority in ['low', 'normal', 'high', 'urgent']:
            inquiry.priority = new_priority
            inquiry.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Inquiry priority updated successfully!', 'success')
        else:
            flash('Invalid priority provided.', 'error')
        
        return redirect(url_for('admin.admin_contact_inquiry_detail', inquiry_id=inquiry_id))
    except Exception as e:
        current_app.logger.error(f"Error updating inquiry priority: {str(e)}")
        flash('An error occurred while updating the inquiry priority.', 'error')
        return redirect(url_for('admin.admin_contact_inquiries'))

@admin_bp.route('/contact-inquiries/<int:inquiry_id>/assign', methods=['POST'])
@login_required
@admin_required
def admin_assign_inquiry(inquiry_id):
    """Assign contact inquiry to admin"""
    try:
        inquiry = ContactInquiry.query.get_or_404(inquiry_id)
        assigned_to = request.form.get('assigned_to')
        
        inquiry.assigned_to = assigned_to
        inquiry.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Inquiry assigned successfully!', 'success')
        return redirect(url_for('admin.admin_contact_inquiry_detail', inquiry_id=inquiry_id))
    except Exception as e:
        current_app.logger.error(f"Error assigning inquiry: {str(e)}")
        flash('An error occurred while assigning the inquiry.', 'error')
        return redirect(url_for('admin.admin_contact_inquiries'))

@admin_bp.route('/contact-inquiries/<int:inquiry_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_inquiry(inquiry_id):
    """Delete contact inquiry"""
    try:
        inquiry = ContactInquiry.query.get_or_404(inquiry_id)
        db.session.delete(inquiry)
        db.session.commit()
        
        flash('Inquiry deleted successfully!', 'success')
        return redirect(url_for('admin.admin_contact_inquiries'))
    except Exception as e:
        current_app.logger.error(f"Error deleting inquiry: {str(e)}")
        flash('An error occurred while deleting the inquiry.', 'error')
        return redirect(url_for('admin.admin_contact_inquiries'))

@admin_bp.route('/contact-inquiries/export')
@login_required
@admin_required
def admin_export_contact_inquiries():
    """Export contact inquiries to CSV"""
    try:
        # Get filter parameters
        inquiry_type = request.args.get('type')
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        # Build query
        query = ContactInquiry.query
        
        if inquiry_type:
            query = query.filter(ContactInquiry.inquiry_type == inquiry_type)
        if status:
            query = query.filter(ContactInquiry.status == status)
        if priority:
            query = query.filter(ContactInquiry.priority == priority)
        
        inquiries = query.order_by(ContactInquiry.created_at.desc()).all()
        
        # Create CSV content
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Name', 'Email', 'Phone', 'Inquiry Type', 'Subject',
            'Status', 'Priority', 'Created At', 'City', 'State',
            'Investment Range', 'Business Experience', 'Consultation Type',
            'Preferred Time', 'Message'
        ])
        
        # Write data
        for inquiry in inquiries:
            writer.writerow([
                inquiry.id,
                inquiry.name,
                inquiry.email,
                inquiry.phone or '',
                inquiry.inquiry_type,
                inquiry.subject,
                inquiry.status,
                inquiry.priority,
                inquiry.created_at.strftime('%Y-%m-%d %H:%M'),
                inquiry.city or '',
                inquiry.state or '',
                inquiry.investment_range or '',
                inquiry.business_experience or '',
                inquiry.consultation_type or '',
                inquiry.preferred_time or '',
                inquiry.message[:100] + '...' if len(inquiry.message) > 100 else inquiry.message
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=contact_inquiries_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
    except Exception as e:
        current_app.logger.error(f"Error exporting contact inquiries: {str(e)}")
        flash('An error occurred while exporting the inquiries.', 'error')
        return redirect(url_for('admin.admin_contact_inquiries'))

@admin_bp.route('/social-media-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def social_media_settings():
    """Manage social media links and branding"""
    try:
        if request.method == 'POST':
            # Handle file uploads
            logo_file = request.files.get('site_logo')
            favicon_file = request.files.get('site_favicon')
            
            # Handle logo upload
            if logo_file and logo_file.filename:
                if allowed_file(logo_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'svg'}):
                    filename = secure_filename(f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{logo_file.filename}")
                    logo_path = os.path.join(current_app.root_path, 'static', 'images', filename)
                    os.makedirs(os.path.dirname(logo_path), exist_ok=True)
                    logo_file.save(logo_path)
                    SiteSetting.set_setting('site_logo', f'/static/images/{filename}', 'Site logo image')
                    flash('Logo updated successfully!', 'success')
                else:
                    flash('Invalid logo file format. Please use PNG, JPG, JPEG, GIF, or SVG.', 'error')
            
            # Handle favicon upload
            if favicon_file and favicon_file.filename:
                if allowed_file(favicon_file.filename, {'ico', 'png', 'jpg', 'jpeg'}):
                    filename = secure_filename(f"favicon_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{favicon_file.filename}")
                    favicon_path = os.path.join(current_app.root_path, 'static', 'images', filename)
                    os.makedirs(os.path.dirname(favicon_path), exist_ok=True)
                    favicon_file.save(favicon_path)
                    SiteSetting.set_setting('site_favicon', f'/static/images/{filename}', 'Site favicon')
                    flash('Favicon updated successfully!', 'success')
                else:
                    flash('Invalid favicon file format. Please use ICO, PNG, JPG, or JPEG.', 'error')
            
            # Handle logo URL (only if provided and no file upload)
            logo_url = request.form.get('logo_url', '').strip()
            if logo_url and not logo_file:
                SiteSetting.set_setting('site_logo', logo_url, 'Site logo URL')
                flash('Logo URL updated successfully!', 'success')
            
            # Handle favicon URL (only if provided and no file upload)
            favicon_url = request.form.get('favicon_url', '').strip()
            if favicon_url and not favicon_file:
                SiteSetting.set_setting('site_favicon', favicon_url, 'Site favicon URL')
                flash('Favicon URL updated successfully!', 'success')
            
            # Handle social media links
            social_links = {
                'instagram_url': request.form.get('instagram_url', ''),
                'facebook_url': request.form.get('facebook_url', ''),
                'twitter_url': request.form.get('twitter_url', ''),
                'linkedin_url': request.form.get('linkedin_url', ''),
                'youtube_url': request.form.get('youtube_url', ''),
                'whatsapp_number': request.form.get('whatsapp_number', ''),
                'whatsapp_message': request.form.get('whatsapp_message', '')
            }
            
            # Save social media settings
            for key, value in social_links.items():
                SiteSetting.set_setting(key, value, f'{key.replace("_", " ").title()}')
            
            # Handle branding settings
            branding_settings = {
                'company_name': request.form.get('company_name', ''),
                'company_tagline': request.form.get('company_tagline', ''),
                'company_email': request.form.get('company_email', ''),
                'company_phone': request.form.get('company_phone', ''),
                'company_address': request.form.get('company_address', ''),
                'show_social_links': request.form.get('show_social_links') == 'on',
                'show_whatsapp_button': request.form.get('show_whatsapp_button') == 'on'
            }
            
            # Save branding settings
            for key, value in branding_settings.items():
                SiteSetting.set_setting(key, str(value), f'{key.replace("_", " ").title()}')
            
            flash('Social media and branding settings updated successfully!', 'success')
            return redirect(url_for('admin.social_media_settings'))
        
        # Get current settings
        settings = {}
        site_settings = SiteSetting.query.all()
        for setting in site_settings:
            settings[setting.key] = setting.value
        
        return render_template('admin/social_media_settings.html', 
                             settings=settings,
                             now=datetime.now())
                             
    except Exception as e:
        current_app.logger.error(f"Error in social media settings: {str(e)}")
        flash('Error updating settings', 'error')
        return redirect(url_for('admin.admin_dashboard'))

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@admin_bp.route('/orders/email', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_orders_email():
    """Send orders email report"""
    try:
        if request.method == 'POST':
            flash('Email report sent successfully!', 'success')
        return render_template('admin/orders_email.html')
    except Exception as e:
        current_app.logger.error(f"Error in orders email: {str(e)}")
        flash('Error sending email report', 'error')
        return redirect(url_for('admin.admin_orders'))

@admin_bp.route('/media/logo-management', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_logo_management():
    """Manage site logo and favicon with direct upload"""
    try:
        if request.method == 'POST':
            # Handle logo upload
            logo_file = request.files.get('site_logo')
            favicon_file = request.files.get('site_favicon')
            
            # Handle logo upload
            if logo_file and logo_file.filename:
                if allowed_file(logo_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'svg'}):
                    filename = secure_filename(f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{logo_file.filename}")
                    logo_path = os.path.join(current_app.root_path, 'static', 'images', filename)
                    os.makedirs(os.path.dirname(logo_path), exist_ok=True)
                    logo_file.save(logo_path)
                    SiteSetting.set_setting('site_logo', f'/static/images/{filename}', 'Site logo image')
                    flash('Logo updated successfully!', 'success')
                else:
                    flash('Invalid logo file format. Please use PNG, JPG, JPEG, GIF, or SVG.', 'error')
            
            # Handle favicon upload
            if favicon_file and favicon_file.filename:
                if allowed_file(favicon_file.filename, {'ico', 'png', 'jpg', 'jpeg'}):
                    filename = secure_filename(f"favicon_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{favicon_file.filename}")
                    favicon_path = os.path.join(current_app.root_path, 'static', 'images', filename)
                    os.makedirs(os.path.dirname(favicon_path), exist_ok=True)
                    favicon_file.save(favicon_path)
                    SiteSetting.set_setting('site_favicon', f'/static/images/{filename}', 'Site favicon')
                    
                    # Generate PWA icons from the new favicon
                    try:
                        from PIL import Image
                        import io
                        
                        # Open the uploaded favicon
                        with Image.open(favicon_path) as img:
                            # Convert to RGBA if needed
                            if img.mode != 'RGBA':
                                img = img.convert('RGBA')
                            
                            # Define PWA icon sizes
                            pwa_sizes = [
                                (16, 16, 'pwa_icon_16'),
                                (32, 32, 'pwa_icon_32'),
                                (192, 192, 'pwa_icon_192'),
                                (512, 512, 'pwa_icon_512')
                            ]
                            
                            # Create pwa_icons directory
                            pwa_icons_dir = os.path.join(current_app.root_path, 'static', 'images', 'pwa_icons')
                            os.makedirs(pwa_icons_dir, exist_ok=True)
                            
                            # Generate PWA icons
                            for size, size_name in pwa_sizes:
                                # Resize image
                                resized_img = img.resize(size, Image.Resampling.LANCZOS)
                                
                                # Save as PNG
                                icon_filename = f"pwa_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{size[0]}x{size[1]}.png"
                                icon_path = os.path.join(pwa_icons_dir, icon_filename)
                                resized_img.save(icon_path, 'PNG')
                                
                                # Update database setting
                                SiteSetting.set_setting(size_name, f'/static/images/pwa_icons/{icon_filename}', f'PWA icon {size[0]}x{size[1]}')
                            
                            # Also create maskable icons (same as regular for now)
                            for size, size_name in pwa_sizes:
                                maskable_key = f"{size_name}_maskable"
                                SiteSetting.set_setting(maskable_key, f'/static/images/pwa_icons/{icon_filename}', f'PWA maskable icon {size[0]}x{size[1]}')
                        
                        # Regenerate manifest.json
                        generate_manifest_json()
                        flash('Favicon updated successfully! PWA icons generated and manifest updated.', 'success')
                        
                    except ImportError:
                        flash('Favicon updated successfully! PIL not available for PWA icon generation.', 'warning')
                    except Exception as e:
                        current_app.logger.error(f"Error generating PWA icons: {str(e)}")
                        flash('Favicon updated successfully! Error generating PWA icons.', 'warning')
                else:
                    flash('Invalid favicon file format. Please use ICO, PNG, JPG, or JPEG.', 'error')
            
            # Handle logo URL (only if provided and no file upload)
            logo_url = request.form.get('logo_url', '').strip()
            if logo_url and not logo_file:
                SiteSetting.set_setting('site_logo', logo_url, 'Site logo URL')
                flash('Logo URL updated successfully!', 'success')
            
            # Handle favicon URL (only if provided and no file upload)
            favicon_url = request.form.get('favicon_url', '').strip()
            if favicon_url and not favicon_file:
                SiteSetting.set_setting('site_favicon', favicon_url, 'Site favicon URL')
                flash('Favicon URL updated successfully!', 'success')
            
            # If no files uploaded and no URLs provided, just show success message
            if not logo_file and not favicon_file and not logo_url and not favicon_url:
                flash('No changes made to logo or favicon.', 'info')
            
            return redirect(url_for('admin.admin_logo_management'))
        
        # Get current settings
        settings = {}
        site_settings = SiteSetting.query.all()
        for setting in site_settings:
            settings[setting.key] = setting.value
        
        return render_template('admin/logo_management.html', 
                             settings=settings,
                             now=datetime.now())
                             
    except Exception as e:
        current_app.logger.error(f"Error in logo management: {str(e)}")
        flash('Error updating logo settings', 'error')
        return redirect(url_for('admin.admin_dashboard'))

# FullWidthSection Management Routes
@admin_bp.route('/media/full-width-sections')
@login_required
@admin_required
def admin_full_width_sections():
    """Manage full-width image sections"""
    try:
        sections = FullWidthSection.query.order_by(FullWidthSection.order, FullWidthSection.created_at).all()
        return render_template('admin/full_width_sections.html', sections=sections)
    except Exception as e:
        current_app.logger.error(f"Error loading full-width sections: {str(e)}")
        flash('Error loading sections', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/media/full-width-sections/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_full_width_section():
    """Add a new full-width section"""
    try:
        if request.method == 'POST':
            # Handle image upload
            image_file = request.files.get('image')
            if not image_file or not image_file.filename:
                flash('Please select an image file.', 'error')
                return render_template('admin/add_full_width_section.html')
            
            if not allowed_file(image_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'webp'}):
                flash('Invalid image format. Please use PNG, JPG, JPEG, GIF, or WEBP.', 'error')
                return render_template('admin/add_full_width_section.html')
            
            # Save image
            filename = secure_filename(f"fullwidth_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image_file.filename}")
            image_path = os.path.join(current_app.root_path, 'static', 'images', filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image_file.save(image_path)
            
            # Create section
            section = FullWidthSection(
                title=request.form.get('title', '').strip(),
                image_url=f'/static/images/{filename}',
                button_text=request.form.get('button_text', '').strip(),
                button_url=request.form.get('button_url', '').strip(),
                image_link_url=request.form.get('image_link_url', '').strip(),
                show_button=request.form.get('show_button') == 'on',
                order=int(request.form.get('order', 0)),
                is_active=request.form.get('is_active') == 'on'
            )
            
            db.session.add(section)
            db.session.commit()
            
            flash('Full-width section added successfully!', 'success')
            return redirect(url_for('admin.admin_full_width_sections'))
        
        return render_template('admin/add_full_width_section.html')
        
    except Exception as e:
        current_app.logger.error(f"Error adding full-width section: {str(e)}")
        flash('Error adding section', 'error')
        return redirect(url_for('admin.admin_full_width_sections'))

@admin_bp.route('/media/full-width-sections/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_full_width_section(id):
    """Edit a full-width section"""
    try:
        section = FullWidthSection.query.get_or_404(id)
        
        if request.method == 'POST':
            # Handle image upload
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                if not allowed_file(image_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'webp'}):
                    flash('Invalid image format. Please use PNG, JPG, JPEG, GIF, or WEBP.', 'error')
                    return render_template('admin/edit_full_width_section.html', section=section)
                
                # Save new image
                filename = secure_filename(f"fullwidth_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image_file.filename}")
                image_path = os.path.join(current_app.root_path, 'static', 'images', filename)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                image_file.save(image_path)
                section.image_url = f'/static/images/{filename}'
            
            # Update other fields
            section.title = request.form.get('title', '').strip()
            section.button_text = request.form.get('button_text', '').strip()
            section.button_url = request.form.get('button_url', '').strip()
            section.image_link_url = request.form.get('image_link_url', '').strip()
            section.show_button = request.form.get('show_button') == 'on'
            section.order = int(request.form.get('order', 0))
            section.is_active = request.form.get('is_active') == 'on'
            section.updated_at = datetime.now()
            
            db.session.commit()
            flash('Full-width section updated successfully!', 'success')
            return redirect(url_for('admin.admin_full_width_sections'))
        
        return render_template('admin/edit_full_width_section.html', section=section)
        
    except Exception as e:
        current_app.logger.error(f"Error editing full-width section: {str(e)}")
        flash('Error updating section', 'error')
        return redirect(url_for('admin.admin_full_width_sections'))

@admin_bp.route('/media/full-width-sections/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_full_width_section(id):
    """Delete a full-width section"""
    try:
        section = FullWidthSection.query.get_or_404(id)
        
        # Delete the image file if it exists
        if section.image_url and section.image_url.startswith('/static/images/'):
            image_path = os.path.join(current_app.root_path, 'static', 'images', 
                                     os.path.basename(section.image_url))
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(section)
        db.session.commit()
        
        flash('Full-width section deleted successfully!', 'success')
        return redirect(url_for('admin.admin_full_width_sections'))
        
    except Exception as e:
        current_app.logger.error(f"Error deleting full-width section: {str(e)}")
        flash('Error deleting section', 'error')
        return redirect(url_for('admin.admin_full_width_sections'))

@admin_bp.route('/media/full-width-sections/toggle/<int:id>', methods=['POST'])
@login_required
@admin_required
def admin_toggle_full_width_section(id):
    """Toggle full-width section active status"""
    try:
        section = FullWidthSection.query.get_or_404(id)
        section.is_active = not section.is_active
        section.updated_at = datetime.now()
        db.session.commit()
        
        status = 'activated' if section.is_active else 'deactivated'
        flash(f'Full-width section {status} successfully!', 'success')
        return redirect(url_for('admin.admin_full_width_sections'))
        
    except Exception as e:
        current_app.logger.error(f"Error toggling full-width section: {str(e)}")
        flash('Error updating section status', 'error')
        return redirect(url_for('admin.admin_full_width_sections'))

# PWA Management Routes
@admin_bp.route('/media/pwa-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_pwa_settings():
    """Manage PWA settings including icons, manifest, and theme colors"""
    try:
        # Get current PWA settings from database
        pwa_settings = {}
        site_settings = SiteSetting.query.filter(
            SiteSetting.key.in_(['pwa_name', 'pwa_short_name', 'pwa_description', 
                               'pwa_theme_color', 'pwa_background_color', 'pwa_display_mode',
                               'pwa_orientation', 'pwa_start_url', 'pwa_scope'])
        ).all()
        
        for setting in site_settings:
            pwa_settings[setting.key] = setting.value
        
        # Set defaults if not found
        defaults = {
            'pwa_name': 'HealthyRizz - Healthy Meal Delivery',
            'pwa_short_name': 'HealthyRizz',
            'pwa_description': 'Fresh, healthy meal plans delivered to your doorstep',
            'pwa_theme_color': '#10b981',
            'pwa_background_color': '#ffffff',
            'pwa_display_mode': 'standalone',
            'pwa_orientation': 'portrait-primary',
            'pwa_start_url': '/',
            'pwa_scope': '/'
        }
        
        for key, default_value in defaults.items():
            if key not in pwa_settings:
                pwa_settings[key] = default_value
        
        if request.method == 'POST':
            try:
                # Update PWA settings
                for key in defaults.keys():
                    value = request.form.get(key, defaults[key])
                    
                    # Find existing setting or create new one
                    setting = SiteSetting.query.filter_by(key=key).first()
                    if setting:
                        setting.value = value
                    else:
                        setting = SiteSetting(key=key, value=value)
                        db.session.add(setting)
                
                db.session.commit()
                
                # Regenerate manifest.json
                generate_manifest_json()
                
                flash('PWA settings updated successfully!', 'success')
                return redirect(url_for('admin.admin_pwa_settings'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating PWA settings: {str(e)}")
                flash('An error occurred while updating PWA settings.', 'error')
        
        return render_template('admin/pwa_settings.html', pwa_settings=pwa_settings)
        
    except Exception as e:
        current_app.logger.error(f"Error loading PWA settings: {str(e)}")
        flash('An error occurred while loading PWA settings.', 'error')
        return redirect(url_for('admin.admin_media'))

@admin_bp.route('/media/pwa-icons', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_pwa_icons():
    """Manage PWA icons for different sizes and purposes"""
    try:
        # Get current PWA icon settings
        icon_settings = {}
        site_settings = SiteSetting.query.filter(
            SiteSetting.key.like('pwa_icon_%')
        ).all()
        
        for setting in site_settings:
            icon_settings[setting.key] = setting.value
        
        # Define required icon sizes for PWA
        required_icons = [
            {'size': '192x192', 'purpose': 'any', 'key': 'pwa_icon_192'},
            {'size': '512x512', 'purpose': 'any', 'key': 'pwa_icon_512'},
            {'size': '192x192', 'purpose': 'maskable', 'key': 'pwa_icon_192_maskable'},
            {'size': '512x512', 'purpose': 'maskable', 'key': 'pwa_icon_512_maskable'},
            {'size': '32x32', 'purpose': 'any', 'key': 'pwa_icon_32'},
            {'size': '16x16', 'purpose': 'any', 'key': 'pwa_icon_16'}
        ]
        
        if request.method == 'POST':
            try:
                # Handle icon uploads
                for icon_info in required_icons:
                    file_key = f"icon_{icon_info['size'].replace('x', '_')}"
                    if file_key in request.files:
                        file = request.files[file_key]
                        if file and file.filename:
                            # Secure filename and save
                            filename = secure_filename(file.filename)
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                            filename = f"pwa_{timestamp}{filename}"
                            
                            # Save to static/images/pwa_icons/
                            upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'pwa_icons')
                            os.makedirs(upload_folder, exist_ok=True)
                            file_path = os.path.join(upload_folder, filename)
                            
                            file.save(file_path)
                            
                            # Update database
                            setting_key = icon_info['key']
                            setting = SiteSetting.query.filter_by(key=setting_key).first()
                            if setting:
                                setting.value = f'/static/images/pwa_icons/{filename}'
                            else:
                                setting = SiteSetting(key=setting_key, value=f'/static/images/pwa_icons/{filename}')
                                db.session.add(setting)
                
                db.session.commit()
                
                # Regenerate manifest.json
                generate_manifest_json()
                
                flash('PWA icons updated successfully!', 'success')
                return redirect(url_for('admin.admin_pwa_icons'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating PWA icons: {str(e)}")
                flash('An error occurred while updating PWA icons.', 'error')
        
        return render_template('admin/pwa_icons.html', 
                             icon_settings=icon_settings, 
                             required_icons=required_icons)
        
    except Exception as e:
        current_app.logger.error(f"Error loading PWA icons: {str(e)}")
        flash('An error occurred while loading PWA icons.', 'error')
        return redirect(url_for('admin.admin_media'))

@admin_bp.route('/media/pwa-preview')
@login_required
@admin_required
def admin_pwa_preview():
    """Preview PWA manifest and installation experience"""
    try:
        # Get current PWA settings
        pwa_settings = {}
        site_settings = SiteSetting.query.filter(
            SiteSetting.key.like('pwa_%')
        ).all()
        
        for setting in site_settings:
            pwa_settings[setting.key] = setting.value
        
        # Generate preview manifest
        manifest_data = generate_manifest_data()
        
        return render_template('admin/pwa_preview.html', 
                             pwa_settings=pwa_settings,
                             manifest_data=manifest_data)
        
    except Exception as e:
        current_app.logger.error(f"Error loading PWA preview: {str(e)}")
        flash('An error occurred while loading PWA preview.', 'error')
        return redirect(url_for('admin.admin_media'))

def generate_manifest_data():
    """Generate PWA manifest data from database settings"""
    try:
        # Get PWA settings from database
        pwa_settings = {}
        site_settings = SiteSetting.query.filter(
            SiteSetting.key.like('pwa_%')
        ).all()
        
        for setting in site_settings:
            pwa_settings[setting.key] = setting.value
        
        # Set defaults
        defaults = {
            'pwa_name': 'HealthyRizz - Healthy Meal Delivery',
            'pwa_short_name': 'HealthyRizz',
            'pwa_description': 'Fresh, healthy meal plans delivered to your doorstep',
            'pwa_theme_color': '#10b981',
            'pwa_background_color': '#ffffff',
            'pwa_display_mode': 'standalone',
            'pwa_orientation': 'portrait-primary',
            'pwa_start_url': '/',
            'pwa_scope': '/'
        }
        
        for key, default_value in defaults.items():
            if key not in pwa_settings:
                pwa_settings[key] = default_value
        
        # Build icons array
        icons = []
        icon_mappings = {
            'pwa_icon_192': {'sizes': '192x192', 'purpose': 'any'},
            'pwa_icon_512': {'sizes': '512x512', 'purpose': 'any'},
            'pwa_icon_192_maskable': {'sizes': '192x192', 'purpose': 'maskable'},
            'pwa_icon_512_maskable': {'sizes': '512x512', 'purpose': 'maskable'},
            'pwa_icon_32': {'sizes': '32x32', 'purpose': 'any'},
            'pwa_icon_16': {'sizes': '16x16', 'purpose': 'any'}
        }
        
        for key, icon_info in icon_mappings.items():
            if key in pwa_settings and pwa_settings[key]:
                icons.append({
                    'src': pwa_settings[key],
                    'sizes': icon_info['sizes'],
                    'type': 'image/png',
                    'purpose': icon_info['purpose']
                })
        
        # If no custom icons, use defaults
        if not icons:
            icons = [
                {'src': '/static/images/logo white.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any maskable'},
                {'src': '/static/favicon.ico', 'sizes': '32x32', 'type': 'image/x-icon'}
            ]
        
        manifest_data = {
            'name': pwa_settings['pwa_name'],
            'short_name': pwa_settings['pwa_short_name'],
            'description': pwa_settings['pwa_description'],
            'start_url': pwa_settings['pwa_start_url'],
            'display': pwa_settings['pwa_display_mode'],
            'background_color': pwa_settings['pwa_background_color'],
            'theme_color': pwa_settings['pwa_theme_color'],
            'orientation': pwa_settings['pwa_orientation'],
            'icons': icons,
            'categories': ['food', 'health', 'lifestyle'],
            'lang': 'en',
            'dir': 'ltr'
        }
        
        return manifest_data
        
    except Exception as e:
        current_app.logger.error(f"Error generating manifest data: {str(e)}")
        return {}

def generate_manifest_json():
    """Generate and save manifest.json file"""
    try:
        manifest_data = generate_manifest_data()
        
        # Save to static/manifest.json
        manifest_path = os.path.join(current_app.root_path, 'static', 'manifest.json')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        
        current_app.logger.info("Manifest.json generated successfully")
        
    except Exception as e:
        current_app.logger.error(f"Error generating manifest.json: {str(e)}")
        raise

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('You do not have admin privileges.', 'error')
            return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account is inactive. Please contact support.', 'error')
                return redirect(url_for('admin.admin_login'))
            
            if not user.is_admin:
                flash('You do not have admin privileges.', 'error')
                return redirect(url_for('admin.admin_login'))
            
            # Log successful admin login
            current_app.logger.info(f'Admin user {user.email} logged in successfully')
            
            # Login user
            login_user(user, remember=form.remember_me.data)
            
            # Get next page from args or default to admin dashboard
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('admin.admin_dashboard')
            
            return redirect(next_page)
        else:
            # Log failed login attempt
            current_app.logger.warning(f'Failed admin login attempt for email: {form.email.data}')
            flash('Invalid email or password', 'error')
            return redirect(url_for('admin.admin_login'))
    
    return render_template('admin/login.html', form=form)
