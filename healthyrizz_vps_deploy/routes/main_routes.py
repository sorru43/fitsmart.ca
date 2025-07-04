"""
Main routes for the application
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, current_app, make_response
from sqlalchemy import or_
from extensions import db, csrf
from models import User, MealPlan, Order, Subscription, TrialRequest, BlogPost, HeroSlide, Video, TeamMember, SiteSetting, State, City, Area, ContactInquiry, FAQ
from contact_forms import CheckoutForm, TrialRequestForm, MultiPurposeContactForm
import logging
import json
from datetime import datetime, timedelta
from flask_login import login_required, current_user, login_user, logout_user
from flask_mail import Message
from extensions import mail
from utils.razorpay_utils import create_razorpay_order, verify_payment_signature, create_razorpay_customer, get_razorpay_key
from forms.auth_forms import LoginForm, RegisterForm
from utils.token_utils import generate_password_reset_token
from utils.email_utils import send_password_reset_email, send_contact_notification
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from urllib.parse import urlparse
from routes.admin_routes import admin_required

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

main_bp = Blueprint('main', __name__)

class TestForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

@main_bp.route('/')
def index():
    """Home page route"""
    # Get active FAQs ordered by their display order
    faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.order, FAQ.created_at).all()
    
    # Get homepage content from database
    hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.order, HeroSlide.created_at).all()
    videos = Video.query.filter_by(is_active=True).order_by(Video.order, Video.created_at).all()
    team_members = TeamMember.query.filter_by(is_active=True).order_by(TeamMember.order, TeamMember.created_at).all()
    
    # Get meal plans for the homepage
    meal_plans = MealPlan.query.filter_by(is_active=True).order_by(MealPlan.is_popular.desc(), MealPlan.price_weekly).limit(6).all()
    
    # Get site settings
    site_settings = {}
    settings = SiteSetting.query.all()
    for setting in settings:
        site_settings[setting.key] = setting.value
    
    # Fallback to defaults if no content in database
    if not hero_slides:
        hero_slides = [
            {'title': "It's Not An Ordinary Meal Box, It's a Nutrition Box", 'image_url': '/static/images/healthy-meal-bowl.jpg'},
            {'title': "Personalized Nutrition Delivered", 'image_url': '/static/images/meal-plate.jpg'},
            {'title': "Eat Healthy, Live Better", 'image_url': '/static/images/healthy-meal-bowl.webp'}
        ]
    
    if not videos:
        videos = [
            {'title': 'How HealthyRizz Works', 'description': 'Choose your plan, connect with a nutrition expert, get chef-prepared meals delivered, and transform your lifestyle!', 'youtube_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'thumbnail_url': '/static/images/healthy-meal-bowl.jpg'},
            {'title': 'Our Kitchen Process', 'description': 'See how we prepare fresh, nutritious meals in our state-of-the-art kitchen facilities with expert chefs.', 'youtube_url': 'https://www.youtube.com/watch?v=9bZkp7q19f0', 'thumbnail_url': '/static/images/meal-plate.jpg'},
            {'title': 'Customer Success Stories', 'description': 'Hear from our satisfied customers about their transformation journey with HealthyRizz nutrition plans.', 'youtube_url': 'https://www.youtube.com/watch?v=kJQP7q19f0', 'thumbnail_url': '/static/images/healthy-meal-bowl.webp'},
            {'title': 'Expert Nutrition Guidance', 'description': 'Learn how our certified nutrition experts create personalized meal plans tailored to your health goals.', 'youtube_url': 'https://www.youtube.com/watch?v=ZZ5LpwO-An4', 'thumbnail_url': '/static/images/healthy-meal-bowl.jpg'}
        ]
    
    if not team_members:
        team_members = [
            {'name': 'Ankit Bathla', 'position': 'Certified Nutrition and Fitness Expert', 'image_url': '/static/images/default-avatar.png'},
            {'name': 'Anu Bathla', 'position': 'Exercise Science & Nutrition Expert', 'image_url': '/static/images/default-avatar.png'},
            {'name': 'Vidit Juneja', 'position': 'Recipe Expert', 'image_url': '/static/images/default-avatar.png'},
            {'name': 'Ashish Arora', 'position': 'Operation Head', 'image_url': '/static/images/default-avatar.png'}
        ]
    
    # Default site settings
    default_settings = {
        'site_logo': '/static/images/logo white.png',
        'hero_subtitle': 'In Supervision Of Nutrition Experts',
        'company_name': 'HealthyRizz',
        'company_tagline': 'Healthy Meal Delivery'
    }
    
    # Merge with database settings
    for key, default_value in default_settings.items():
        if key not in site_settings:
            site_settings[key] = default_value
    
    return render_template('index.html', 
                         faqs=faqs,
                         hero_slides=hero_slides,
                         videos=videos,
                         team_members=team_members,
                         meal_plans=meal_plans,
                         site_settings=site_settings,
                         now=datetime.now())

@main_bp.route('/about')
def about():
    """About page route"""
    return render_template('about.html', now=datetime.now())

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route with multi-purpose form"""
    from contact_forms import MultiPurposeContactForm
    from models import ContactInquiry
    
    form = MultiPurposeContactForm()
    
    if form.validate_on_submit():
        try:
            # Create contact inquiry
            inquiry = ContactInquiry(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                inquiry_type=form.inquiry_type.data,
                subject=form.subject.data,
                message=form.message.data,
                city=form.city.data,
                state=form.state.data,
                pincode=form.pincode.data,
                investment_range=form.investment_range.data,
                business_experience=form.business_experience.data,
                preferred_location=form.preferred_location.data,
                consultation_type=form.consultation_type.data,
                preferred_time=form.preferred_time.data,
                preferred_date=form.preferred_date.data,
                user_id=current_user.id if current_user.is_authenticated else None
            )
            
            # Set priority based on urgency
            if form.urgency.data == 'urgent':
                inquiry.priority = 'urgent'
            elif form.urgency.data == 'high':
                inquiry.priority = 'high'
            elif form.urgency.data == 'low':
                inquiry.priority = 'low'
            else:
                inquiry.priority = 'normal'
            
            db.session.add(inquiry)
            db.session.commit()
            
            # Send email notification to admin
            try:
                send_contact_notification(inquiry)
            except Exception as e:
                current_app.logger.error(f"Failed to send contact notification email: {str(e)}")
            
            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('main.contact'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating contact inquiry: {str(e)}")
            flash('An error occurred while sending your message. Please try again.', 'error')
    
    return render_template('contact.html', form=form, now=datetime.now())

@main_bp.route('/meal-calculator')
def meal_calculator():
    """Meal calculator page"""
    return render_template('meal_calculator.html', now=datetime.now())

@main_bp.route('/calculate-meal', methods=['POST'])
def calculate_meal():
    """Calculate meal plan macros and return JSON response for AJAX requests"""
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['age', 'gender', 'weight', 'height', 'activity', 'goal']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Convert numeric values
        try:
            age = float(data['age'])
            weight = float(data['weight'])
            height = float(data['height'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid numeric values for age, weight, or height'}), 400
        
        # Validate numeric ranges
        if not (10 <= age <= 120):
            return jsonify({'error': 'Age must be between 10 and 120 years'}), 400
        if not (30 <= weight <= 300):
            return jsonify({'error': 'Weight must be between 30 and 300 kg'}), 400
        if not (100 <= height <= 250):
            return jsonify({'error': 'Height must be between 100 and 250 cm'}), 400
        
        # Calculate BMR using Mifflin-St Jeor Equation
        if data['gender'].lower() == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:  # female
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        # Activity level multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very': 1.725,
            'extra': 1.9
        }
        
        # Calculate TDEE (Total Daily Energy Expenditure)
        activity_level = data['activity'].lower()
        if activity_level not in activity_multipliers:
            return jsonify({'error': 'Invalid activity level'}), 400
        
        tdee = bmr * activity_multipliers[activity_level]
        
        # Adjust calories based on goal
        goal = data['goal'].lower()
        if goal == 'lose':
            calories = tdee - 500  # 500 calorie deficit for weight loss
        elif goal == 'gain':
            calories = tdee + 500  # 500 calorie surplus for weight gain
        else:  # maintain
            calories = tdee
        
        # Ensure minimum calories for safety
        calories = max(1200 if data['gender'].lower() == 'female' else 1500, calories)
        
        # Calculate macros
        # Protein: 1.6-2.2g per kg of body weight (use 1.8g as average)
        protein = round(weight * 1.8)
        
        # Fat: 25-30% of total calories (use 25%)
        fat_calories = calories * 0.25
        fat = round(fat_calories / 9)  # 9 calories per gram of fat
        
        # Carbs: Remaining calories
        remaining_calories = calories - (protein * 4) - (fat * 9)
        carbs = round(remaining_calories / 4)  # 4 calories per gram of carbs
        
        # Return JSON response
        return jsonify({
            'success': True,
            'calories': round(calories),
            'protein': protein,
            'carbs': carbs,
            'fat': fat,
            'bmr': round(bmr),
            'tdee': round(tdee)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in calculate_meal: {str(e)}")
        return jsonify({'error': 'An error occurred while calculating your meal plan'}), 500

@main_bp.route('/meal-plans')
def meal_plans():
    """Meal plans page with advanced filters"""
    plan_type = request.args.get('type')
    breakfast = request.args.get('breakfast')
    trial_only = request.args.get('trial_only')
    search = request.args.get('search')
    
    # Start with all active plans
    query = MealPlan.query.filter_by(is_active=True)

    # Filter by plan type (tag or category)
    if plan_type:
        if plan_type == 'vegetarian':
            query = query.filter(MealPlan.is_vegetarian == True)
        else:
            query = query.filter(MealPlan.tag.ilike(f"%{plan_type.replace('-', ' ')}%"))

    # Filter by breakfast option
    if breakfast == '1':
        query = query.filter(MealPlan.includes_breakfast == True)
    elif breakfast == '0':
        query = query.filter(MealPlan.includes_breakfast == False)

    # Filter by trial availability
    if trial_only == '1':
        query = query.filter(MealPlan.available_for_trial == True)

    # Search by name or description
    if search:
        query = query.filter(or_(MealPlan.name.ilike(f'%{search}%'), MealPlan.description.ilike(f'%{search}%')))

    plans = query.order_by(MealPlan.price_weekly).all()
    
    return render_template('meal_plans.html', 
                         plan_type=plan_type, 
                         plans=plans,
                         now=datetime.now())

@main_bp.route('/blog')
def blog():
    """Blog page"""
    try:
        # Get published blog posts with author information
        posts = BlogPost.query.filter_by(is_published=True).order_by(
            BlogPost.is_featured.desc(),  # Featured posts first
            BlogPost.published_date.desc()  # Then by publish date
        ).all()
        
        # Get unique categories
        categories = db.session.query(BlogPost.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        current_app.logger.info(f"Main blog route - Found {len(posts)} published blog posts")
        
        return render_template('blog.html', posts=posts, categories=categories, now=datetime.now())
    except Exception as e:
        current_app.logger.error(f"Error fetching published blog posts: {str(e)}")
        flash('Error loading blog posts', 'error')
        return render_template('blog.html', posts=[], categories=[], now=datetime.now())

@main_bp.route('/blog/<slug>')
def blog_post(slug):
    """Individual blog post page"""
    try:
        post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
        return render_template('blog-post.html', post=post, now=datetime.now())
    except Exception as e:
        current_app.logger.error(f"Error fetching blog post: {str(e)}")
        flash('Blog post not found', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    current_app.logger.info(f"📄 PROFILE PAGE ACCESSED by {current_user.email}")
    
    try:
        # Get user's active subscriptions
        active_subscriptions = Subscription.query.filter(
            Subscription.user_id == current_user.id,
            Subscription.status == 'active'
        ).all()
        
        # Get user's paused subscriptions
        paused_subscriptions = Subscription.query.filter(
            Subscription.user_id == current_user.id,
            Subscription.status == 'paused'
        ).all()
        
        # Get user's canceled subscriptions
        canceled_subscriptions = Subscription.query.filter(
            Subscription.user_id == current_user.id,
            Subscription.status == 'cancelled'
        ).all()
        
        # Remove delivery processing completely to avoid JSON error
        subscription_deliveries = {}
        
        current_app.logger.info(f"Profile data loaded successfully for {current_user.email}")
        
        return render_template('profile.html', 
                             user=current_user,
                             active_subscriptions=active_subscriptions,
                             paused_subscriptions=paused_subscriptions,
                             canceled_subscriptions=canceled_subscriptions,
                             subscription_deliveries=subscription_deliveries,
                             now=datetime.now())
                             
    except Exception as e:
        current_app.logger.error(f"Error in profile route: {str(e)}")
        current_app.logger.error(f"Error type: {type(e).__name__}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Return a basic error page instead of crashing
        return render_template('error.html', 
                             error_message="Profile temporarily unavailable. Please try again later.",
                             now=datetime.now()), 500

@main_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Handle profile updates"""
    try:
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        province = request.form.get('province', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        form_section = request.form.get('form_section', '').strip()
        
        current_app.logger.info(f"Profile update for user {current_user.email}")
        current_app.logger.info(f"Password fields provided: current={bool(current_password)}, new={bool(new_password)}, confirm={bool(confirm_password)}")
        current_app.logger.info(f"Form section: {form_section}")
        current_app.logger.info(f"Is AJAX request: {is_ajax}")
        
        # Validate required fields
        if not name or not email:
            message = 'Name and email are required'
            if is_ajax:
                return jsonify({'status': 'error', 'message': message})
            flash(message, 'error')
            return redirect(url_for('main.profile'))
        
        # Handle password change if provided - ISOLATED TRANSACTION
        password_changed = False
        if current_password or new_password or confirm_password:
            current_app.logger.info("Password change requested")
            
            # All password fields must be provided
            if not all([current_password, new_password, confirm_password]):
                message = 'All password fields are required to change password'
                current_app.logger.warning("Not all password fields provided")
                if is_ajax:
                    return jsonify({'status': 'error', 'message': message})
                flash(message, 'error')
                return redirect(url_for('main.profile'))
            
            # Store original hash for logging
            original_hash = current_user.password_hash
            current_app.logger.info(f"Original password hash: {original_hash[:20]}...")
            
            # Verify current password
            if not current_user.check_password(current_password):
                message = 'Current password is incorrect'
                current_app.logger.warning("Current password verification failed")
                if is_ajax:
                    return jsonify({'status': 'error', 'message': message})
                flash(message, 'error')
                return redirect(url_for('main.profile'))
            
            current_app.logger.info("Current password verified successfully")
            
            # Check if new passwords match
            if new_password != confirm_password:
                message = 'New passwords do not match'
                current_app.logger.warning("New passwords don't match")
                if is_ajax:
                    return jsonify({'status': 'error', 'message': message})
                flash(message, 'error')
                return redirect(url_for('main.profile'))
            
            # Validate new password strength
            if len(new_password) < 8:
                message = 'New password must be at least 8 characters long'
                current_app.logger.warning("New password too short")
                if is_ajax:
                    return jsonify({'status': 'error', 'message': message})
                flash(message, 'error')
                return redirect(url_for('main.profile'))
            
            # ISOLATED PASSWORD CHANGE TRANSACTION
            try:
                current_app.logger.info("Starting isolated password change transaction")
                
                # Get fresh user instance to avoid session conflicts
                user_id = current_user.id
                fresh_user = User.query.get(user_id)
                
                # Update password on fresh instance
                fresh_user.set_password(new_password)
                new_hash = fresh_user.password_hash
                current_app.logger.info(f"New password hash: {new_hash[:20]}...")
                current_app.logger.info(f"Password hash changed: {original_hash != new_hash}")
                
                # Commit ONLY the password change
                db.session.commit()
                current_app.logger.info("Password change committed successfully")
                
                # Update current_user instance to reflect the change
                current_user.password_hash = fresh_user.password_hash
                
                password_changed = True
                success_message = 'Password updated successfully'
                current_app.logger.info("Password change completed successfully")
                
            except Exception as pwd_error:
                db.session.rollback()
                message = 'Failed to update password. Please try again.'
                current_app.logger.error(f"Password change failed: {str(pwd_error)}")
                if is_ajax:
                    return jsonify({'status': 'error', 'message': message})
                flash(message, 'error')
                return redirect(url_for('main.profile'))
        
        # Update user information
        current_user.name = name
        current_user.email = email
        current_user.phone = phone
        current_user.address = address
        current_user.city = city
        current_user.province = province
        current_user.postal_code = postal_code
        
        # Save changes
        current_app.logger.info("Committing changes to database")
        db.session.commit()
        current_app.logger.info("Database commit successful")
        
        # Determine success message
        if password_changed:
            message = 'Password updated successfully'
        else:
            message = 'Profile updated successfully'
        
        # Return appropriate response
        if is_ajax:
            return jsonify({'status': 'success', 'message': message})
        else:
            flash(message, 'success')
            # Determine redirect for non-AJAX requests
            redirect_url = url_for('main.profile')
            if form_section and form_section in ['settings', 'account', 'subscriptions', 'payments', 'nutrition']:
                redirect_url = url_for('main.profile') + f'#{form_section}'
            elif password_changed:
                redirect_url = url_for('main.profile') + '#settings'
            return redirect(redirect_url)
        
    except Exception as e:
        db.session.rollback()
        message = 'An error occurred while updating your profile'
        current_app.logger.error(f"Error updating profile: {str(e)}")
        
        if is_ajax:
            return jsonify({'status': 'error', 'message': message})
        else:
            flash(message, 'error')
            # Redirect back to the same section on error
            error_redirect_url = url_for('main.profile')
            if form_section and form_section in ['settings', 'account', 'subscriptions', 'payments', 'nutrition']:
                error_redirect_url = url_for('main.profile') + f'#{form_section}'
            return redirect(error_redirect_url)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account is inactive. Please contact support.', 'error')
                return redirect(url_for('main.login'))
            
            # Log successful login
            logging.info(f'User {user.email} logged in successfully')
            
            # Login user
            login_user(user, remember=form.remember_me.data)
            
            # Get next page from args or default to index
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.index')
            
            return redirect(next_page)
        else:
            # Log failed login attempt
            logging.warning(f'Failed login attempt for email: {form.email.data}')
            flash('Invalid email or password', 'error')
            return redirect(url_for('main.login'))
    
    return render_template('login.html', form=form)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data.lower()  # Normalize email to lowercase
        phone = form.phone.data
        password = form.password.data
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html', form=form, now=datetime.now())
        
        try:
            # Create new user using the create_user method
            user = User.create_user(email=email, username=name, password=password, phone=phone)
            db.session.add(user)
            db.session.commit()
            
            # Log successful registration
            logging.info(f'New user registered: {user.email}')
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f'Registration error for {email}: {str(e)}')
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('register.html', form=form, now=datetime.now())
    
    return render_template('register.html', form=form, now=datetime.now())

@main_bp.route('/logout')
def logout():
    """Logout route"""
    current_app.logger.debug("Logout route called")
    
    # Clear Flask-Login session
    logout_user()
    current_app.logger.debug("Flask-Login session cleared")
    
    # Clear all session data
    session.clear()
    current_app.logger.debug("Session data cleared")
    
    # Clear any remember me cookies
    if 'remember_token' in session:
        session.pop('remember_token')
        current_app.logger.debug("Remember token cleared")
    
    # Clear any user-specific data
    session.pop('user_id', None)
    session.pop('_user_id', None)
    session.pop('_fresh', None)
    session.pop('_id', None)
    current_app.logger.debug("User-specific session data cleared")
    
    flash('You have been logged out successfully.', 'success')
    current_app.logger.debug("Redirecting to index page")
    return redirect(url_for('main.index'))

@main_bp.route('/subscribe-newsletter', methods=['POST'])
def subscribe_newsletter():
    """Newsletter subscription"""
    email = request.form.get('email')
    if email:
        # TODO: Implement newsletter subscription logic
        flash('Thank you for subscribing to our newsletter!', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/meals')
def meals():
    """Meals page with filtering"""
    diet_type = request.args.get('diet_type')
    min_calories = request.args.get('min_calories', type=int)
    max_calories = request.args.get('max_calories', type=int)
    search = request.args.get('search')
    
    # Start with base query
    query = Meal.query
    
    # Apply filters
    if diet_type:
        query = query.filter(Meal.diet_type_id == diet_type)
    
    if min_calories:
        query = query.filter(Meal.calories >= min_calories)
    
    if max_calories:
        query = query.filter(Meal.calories <= max_calories)
    
    if search:
        query = query.filter(or_(
            Meal.name.ilike(f'%{search}%'),
            Meal.description.ilike(f'%{search}%')
        ))
    
    meals = query.all()
    diet_types = DietType.query.all()
    
    return render_template('meals.html', 
                          meals=meals, 
                          diet_types=diet_types, 
                          selected_diet=diet_type,
                          min_calories=min_calories,
                          max_calories=max_calories,
                          search=search,
                          now=datetime.now())

@main_bp.route('/meal/<int:meal_id>')
def meal_detail(meal_id):
    """Meal details page"""
    meal = Meal.query.get_or_404(meal_id)
    return render_template('meal_detail.html', meal=meal, now=datetime.now())

@main_bp.route('/cart')
def cart():
    """Shopping cart page"""
    cart_items = session.get('cart', {})
    meals = {}
    total = 0
    
    if cart_items:
        for meal_id, quantity in cart_items.items():
            meal = Meal.query.get(int(meal_id))
            if meal:
                meals[meal_id] = {
                    'meal': meal,
                    'quantity': quantity,
                    'subtotal': meal.price * quantity
                }
                total += meal.price * quantity
    
    return render_template('cart.html', cart_items=meals, total=total, now=datetime.now())

@main_bp.route('/add_to_cart/<int:meal_id>', methods=['POST'])
def add_to_cart(meal_id):
    """Add item to cart"""
    quantity = int(request.form.get('quantity', 1))
    
    # Validate meal exists
    meal = Meal.query.get_or_404(meal_id)
    
    # Initialize cart if needed
    if 'cart' not in session:
        session['cart'] = {}
    
    # Convert to string because session serializes keys as strings
    meal_id_str = str(meal_id)
    
    # Add to cart or update quantity
    if meal_id_str in session['cart']:
        session['cart'][meal_id_str] += quantity
    else:
        session['cart'][meal_id_str] = quantity
    
    # Save session
    session.modified = True
    
    flash(f'Added {meal.name} to your cart!', 'success')
    return redirect(url_for('main.meals'))

@main_bp.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart item quantity"""
    meal_id = request.form.get('meal_id')
    quantity = int(request.form.get('quantity'))
    
    if 'cart' in session and meal_id in session['cart']:
        if quantity > 0:
            session['cart'][meal_id] = quantity
        else:
            # Remove item if quantity is 0
            session['cart'].pop(meal_id)
        session.modified = True
    
    return redirect(url_for('main.cart'))

@main_bp.route('/remove_from_cart/<meal_id>', methods=['POST'])
def remove_from_cart(meal_id):
    """Remove item from cart"""
    if 'cart' in session and meal_id in session['cart']:
        session['cart'].pop(meal_id)
        session.modified = True
        flash('Item removed from cart', 'success')
    
    return redirect(url_for('main.cart'))

@main_bp.route('/cart-checkout', methods=['GET', 'POST'])
def cart_checkout():
    """Checkout page for cart items"""
    form = CheckoutForm()
    
    if not session.get('cart'):
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('main.meals'))
    
    cart_items = session.get('cart', {})
    meals = {}
    total = 0
    
    if cart_items:
        for meal_id, quantity in cart_items.items():
            meal = Meal.query.get(int(meal_id))
            if meal:
                meals[meal_id] = {
                    'meal': meal,
                    'quantity': quantity,
                    'subtotal': meal.price * quantity
                }
                total += meal.price * quantity
    
    if form.validate_on_submit():
        try:
            # Create or get customer
            customer = Customer.query.filter_by(email=form.email.data).first()
            if not customer:
                customer = Customer(
                    name=form.name.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    address=form.address.data
                )
                db.session.add(customer)
                db.session.flush()  # Get ID without committing
            
            # Create order
            order = Order(
                customer_id=customer.id,
                total_amount=total,
                delivery_address=form.address.data,
                delivery_instructions=form.delivery_instructions.data
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Create order items
            for meal_id, item in meals.items():
                order_item = OrderItem(
                    order_id=order.id,
                    meal_id=int(meal_id),
                    quantity=item['quantity'],
                    price=item['meal'].price
                )
                db.session.add(order_item)
            
            db.session.commit()
            session.pop('cart', None)  # Clear cart
            
            flash('Your order has been placed successfully!', 'success')
            return redirect(url_for('main.order_confirmation'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your order. Please try again.', 'error')
            return redirect(url_for('main.cart_checkout'))
    
    return render_template('cart_checkout.html', form=form, meals=meals, total=total)

@main_bp.route('/order_confirmation')
def order_confirmation():
    """Order confirmation page"""
    order_id = session.get('last_order_id')
    if not order_id:
        return redirect(url_for('main.index'))
    
    order = Order.query.get_or_404(order_id)
    return render_template('order_confirmation.html', order=order, now=datetime.now())

@main_bp.route('/init_db', methods=['GET'])
def init_db():
    """Initialize database"""
    try:
        db.create_all()
        return jsonify({'message': 'Database initialized successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate a password reset token
            token = generate_password_reset_token(user)
            
            # Send password reset email
            try:
                send_password_reset_email(user.email, token)
                flash('Password reset instructions have been sent to your email.', 'success')
            except Exception as e:
                current_app.logger.error(f"Error sending password reset email: {str(e)}")
                flash('An error occurred while sending the password reset email. Please try again.', 'error')
        else:
            # Don't reveal whether the email exists or not
            flash('If an account exists with that email, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('main.login'))
    
    return render_template('forgot_password.html', now=datetime.now())

@main_bp.route('/subscribe/<int:plan_id>')
def subscribe(plan_id):
    """Subscribe to a meal plan with new smart logic"""
    meal_plan = MealPlan.query.get_or_404(plan_id)
    
    # Get breakfast option from URL params
    with_breakfast = request.args.get('with_breakfast', 'true').lower() == 'true'
    
    # Create form for checkout
    form = CheckoutForm()
    
    return render_template('checkout.html', 
                         plan=meal_plan,
                         form=form,
                         with_breakfast=with_breakfast)

@main_bp.route('/admin/daily-meal-prep')
@login_required
@admin_required
def daily_meal_prep():
    """Admin view for daily meal preparation planning"""
    from datetime import date, timedelta
    import json
    
    # Get date from query params or use today
    date_str = request.args.get('date')
    if date_str:
        try:
            prep_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            prep_date = date.today()
    else:
        prep_date = date.today()
    
    # Get all active subscriptions
    active_subscriptions = Subscription.query.filter_by(status='active').all()
    
    meal_prep_data = {}
    
    for subscription in active_subscriptions:
        meal_plan = subscription.meal_plan
        
        # Check if this date should have a delivery
        if should_deliver_on_date(subscription, prep_date):
            
            # Parse veg days
            veg_days = []
            if subscription.veg_days_json:
                try:
                    veg_days = json.loads(subscription.veg_days_json)
                except:
                    veg_days = []
            
            # Determine if today is a veg day
            weekday = prep_date.weekday()  # 0 = Monday, 6 = Sunday
            is_veg_day = weekday in veg_days or meal_plan.is_vegetarian
            
            # Initialize meal plan data if not exists
            if meal_plan.id not in meal_prep_data:
                meal_prep_data[meal_plan.id] = {
                    'name': meal_plan.name,
                    'veg_count': 0,
                    'nonveg_count': 0,
                    'breakfast_count': 0,
                    'total_count': 0,
                    'customers': []
                }
            
            # Count the meal
            if is_veg_day:
                meal_prep_data[meal_plan.id]['veg_count'] += 1
            else:
                meal_prep_data[meal_plan.id]['nonveg_count'] += 1
            
            if subscription.with_breakfast:
                meal_prep_data[meal_plan.id]['breakfast_count'] += 1
            
            meal_prep_data[meal_plan.id]['total_count'] += 1
            
            # Add customer info
            meal_prep_data[meal_plan.id]['customers'].append({
                'name': subscription.user.username,
                'email': subscription.user.email,
                'address': subscription.delivery_address,
                'is_veg': is_veg_day,
                'with_breakfast': subscription.with_breakfast
            })
    
    return render_template('admin/daily_meal_prep.html', 
                         prep_date=prep_date,
                         meal_prep_data=meal_prep_data)

def should_deliver_on_date(subscription, check_date):
    """Check if a subscription should have delivery on a specific date"""
    # This is a simplified version - you can enhance with more complex delivery logic
    weekday = check_date.weekday()  # 0 = Monday, 6 = Sunday
    
    # For now, assume delivery Monday to Friday for most subscriptions
    if subscription.meals_per_week >= 5:
        return weekday < 5  # Monday to Friday
    elif subscription.meals_per_week == 3:
        return weekday in [0, 2, 4]  # Monday, Wednesday, Friday
    else:
        return weekday < subscription.meals_per_week

@main_bp.route('/test-csrf', methods=['GET', 'POST'])
def test_csrf():
    """Test CSRF protection"""
    form = TestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash('Form submitted successfully!', 'success')
            return redirect(url_for('main.test_csrf'))
        else:
            flash('Form validation failed', 'danger')
    return render_template('test_csrf.html', form=form)

@main_bp.route('/get-active-provinces')
def get_active_provinces():
    # Always return all Canadian provinces
    province_map = [
        {'code': 'ON', 'name': 'Ontario'},
        {'code': 'BC', 'name': 'British Columbia'},
        {'code': 'AB', 'name': 'Alberta'},
        {'code': 'QC', 'name': 'Quebec'},
        {'code': 'NS', 'name': 'Nova Scotia'},
        {'code': 'NB', 'name': 'New Brunswick'},
        {'code': 'MB', 'name': 'Manitoba'},
        {'code': 'PE', 'name': 'Prince Edward Island'},
        {'code': 'SK', 'name': 'Saskatchewan'},
        {'code': 'NL', 'name': 'Newfoundland and Labrador'},
        {'code': 'NT', 'name': 'Northwest Territories'},
        {'code': 'NU', 'name': 'Nunavut'},
        {'code': 'YT', 'name': 'Yukon'}
    ]
    return jsonify({'success': True, 'provinces': province_map})

@main_bp.route('/get-cities-by-province')
def get_cities_by_province():
    province = request.args.get('province')
    if not province:
        return jsonify({'success': False, 'cities': []})
    cities = DeliveryLocation.query.with_entities(DeliveryLocation.city).filter_by(is_active=True, province=province).distinct().all()
    city_list = [c[0] for c in cities]
    return jsonify({'success': True, 'cities': city_list})

@main_bp.route('/trial-request/<int:plan_id>', methods=['GET', 'POST'])
def trial_request(plan_id):
    meal_plan = MealPlan.query.get_or_404(plan_id)
    form = TrialRequestForm()
    form.meal_plan_id.data = plan_id
    
    if form.validate_on_submit():
        try:
            trial_request = TrialRequest(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                preferred_date=form.preferred_date.data,
                address=form.address.data,
                city=form.city.data,
                province=form.province.data,
                postal_code=form.postal_code.data,
                notes=form.notes.data,
                meal_plan_id=plan_id,
                user_id=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(trial_request)
            db.session.commit()
            
            flash('Your trial request has been submitted successfully! We will contact you shortly to confirm your delivery.', 'success')
            return redirect(url_for('main.meal_plans'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your trial request. Please try again.', 'error')
            current_app.logger.error(f'Error creating trial request: {str(e)}')
    
    return render_template('trial_request.html', meal_plan=meal_plan, form=form)

@main_bp.route('/process_checkout', methods=['POST'])
def process_checkout():
    """Process the checkout form and create Razorpay order"""
    try:
        # Get form data
        plan_id = request.form.get('plan_id')
        frequency = request.form.get('frequency')
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        customer_address = request.form.get('customer_address')
        customer_city = request.form.get('customer_city')
        customer_state = request.form.get('customer_state')
        customer_pincode = request.form.get('customer_pincode')
        vegetarian_days = request.form.get('vegetarian_days', '')
        
        # Get meal plan
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
        # Calculate price with GST
        base_price = float(meal_plan.price_weekly if frequency == 'weekly' else meal_plan.price_monthly)
        gst_amount = base_price * 0.05  # 5% GST
        total_price = base_price + gst_amount
        
        # Create Razorpay order
        order_data = create_razorpay_order(
            amount=int(total_price * 100),  # Convert to paise
            receipt=f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            notes={
                'plan_id': plan_id,
                'frequency': frequency,
                'vegetarian_days': vegetarian_days,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'customer_address': customer_address,
                'customer_city': customer_city,
                'customer_state': customer_state,
                'customer_pincode': customer_pincode
            }
        )
        
        if not order_data:
            flash('Error creating payment order. Please try again.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        # Store order data in session
        session['razorpay_order'] = {
            'order_id': order_data['id'],
            'amount': order_data['amount'],
            'currency': order_data['currency'],
            'receipt': order_data['receipt'],
            'notes': order_data['notes']
        }
        
        # Return Razorpay order details for client-side integration
        return jsonify({
            'key': get_razorpay_key(),
            'order_id': order_data['id'],
            'amount': order_data['amount'],
            'currency': order_data['currency'],
            'name': 'HealthyRizz',
            'description': f'{meal_plan.name} - {frequency.title()} Plan',
            'prefill': {
                'name': customer_name,
                'email': customer_email,
                'contact': customer_phone
            },
            'theme': {
                'color': '#3399cc'
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing checkout: {str(e)}")
        flash('An error occurred while processing your order. Please try again.', 'error')
        return redirect(url_for('main.meal_plans'))

@main_bp.route('/verify_payment', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment and create subscription"""
    try:
        # Get payment verification data
        razorpay_payment_id = request.form.get('razorpay_payment_id')
        razorpay_order_id = request.form.get('razorpay_order_id')
        razorpay_signature = request.form.get('razorpay_signature')
        
        # Get order data from session
        order_data = session.get('razorpay_order')
        if not order_data:
            flash('Invalid order session. Please try again.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        # Verify payment signature
        if not verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
            flash('Payment verification failed. Please contact support.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        # Get user or create new user
        user = User.query.filter_by(email=order_data['notes']['customer_email']).first()
        if not user:
            user = User(
                name=order_data['notes']['customer_name'],
                email=order_data['notes']['customer_email'],
                phone=order_data['notes']['customer_phone'],
                address=order_data['notes']['customer_address'],
                city=order_data['notes']['customer_city'],
                state=order_data['notes']['customer_state'],
                postal_code=order_data['notes']['customer_pincode']
            )
            db.session.add(user)
            db.session.flush()
        
        # Create subscription
        subscription = Subscription(
            user_id=user.id,
            meal_plan_id=order_data['notes']['plan_id'],
            frequency=SubscriptionFrequency.WEEKLY if order_data['notes']['frequency'] == 'weekly' else SubscriptionFrequency.MONTHLY,
            status=SubscriptionStatus.ACTIVE,
            price=float(order_data['amount']) / 100,  # Convert from paise to rupees
            vegetarian_days=order_data['notes']['vegetarian_days'],
            start_date=datetime.now(),
            current_period_start=datetime.now(),
            current_period_end=(
                datetime.now() + timedelta(days=7) if order_data['notes']['frequency'] == 'weekly'
                else datetime.now() + timedelta(days=30)
            )
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        # Clear session data
        session.pop('razorpay_order', None)
        
        flash('Your subscription has been created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        flash('An error occurred while processing your payment. Please contact support.', 'error')
        return redirect(url_for('main.meal_plans'))

@main_bp.route('/privacy-policy')
def privacy_policy():
    """Renders the privacy policy page."""
    return render_template('privacy_policy.html')

@main_bp.route('/terms-of-service')
def terms_of_service():
    """Renders the terms of service page."""
    return render_template('terms_of_service.html')

@main_bp.route('/delivery-locations')
def delivery_locations():
    """Renders the delivery locations page with data from the database."""
    try:
        # Fetch all states with their cities and areas
        states = State.query.options(
            db.joinedload(State.cities).joinedload(City.areas)
        ).all()
        return render_template('delivery_locations.html', states=states)
    except Exception as e:
        current_app.logger.error(f"Error fetching delivery locations: {e}")
        flash("Could not load delivery locations at this time. Please try again later.", "error")
        return render_template('delivery_locations.html', states=[])

@main_bp.route('/cancellation-refund-policy')
def cancellation_refund_policy():
    """Cancellation & Refund Policy page"""
    return render_template('cancellation_refund_policy.html')

@main_bp.route('/shipping-delivery-policy')
def shipping_delivery_policy():
    """Shipping & Delivery Policy page"""
    return render_template('shipping_delivery_policy.html') 
