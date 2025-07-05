import os
import logging
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import escape
import werkzeug.exceptions
from flask import render_template, request, redirect, url_for, session, flash, jsonify, make_response, current_app, abort
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail
from flask_login import current_user, login_user
import re
import razorpay
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Import app, db and models
from app import db, create_app
from database.models import (
    User, DeliveryLocation, MealPlan, CouponCode, Banner, BlogPost, 
    Subscription, SkippedDelivery, SubscriptionStatus, SubscriptionFrequency, 
    Newsletter, ServiceRequest, Delivery, DeliveryStatus, DeliveryMessage, 
    FAQ, SubscriptionVegDay, TrialRequest, CouponUsage,
    HeroSlide, Video, TeamMember, SiteSetting, Order
)
from contact_forms import LoginForm, RegisterForm, ProfileForm, MealCalculatorForm, NewsletterForm, TrialRequestForm
from utils.sms_utils import send_delivery_notification, send_subscription_confirmation, send_subscription_reminder, send_sms
from utils.calculator import process_calculator_data
from utils.stripe_utils import create_stripe_customer, create_stripe_checkout_session, retrieve_subscription
from utils.smtp_email import init_mail, send_trial_request_notification, send_trial_confirmation, send_order_confirmation, send_delivery_notification as send_email_delivery_notification

# Create the Flask app
app = create_app()

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize rate limiter
try:
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=1)
    redis_client.ping()  # Test connection
    storage_uri = "redis://localhost:6379/1"
except (redis.ConnectionError, ImportError):
    app.logger.warning("Redis not available, using memory storage for rate limiting")
    storage_uri = "memory://"

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=storage_uri,
    strategy="fixed-window",
    headers_enabled=True
)

# Initialize Flask-Mail with SMTP configuration
init_mail(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET'])
)

def init_db():
    """Initialize database and create tables"""
    try:
        with app.app_context():
            # Get the absolute path for the database file
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'healthyrizz.db')
            app.logger.info(f"Database path: {db_path}")
            
            # Ensure the database file exists
            if not os.path.exists(db_path):
                app.logger.info("Database file does not exist, creating new database")
                # Create an empty file to ensure the directory is writable
                with open(db_path, 'w') as f:
                    pass
                app.logger.info("Created empty database file")
            
            # Update SQLAlchemy database URI to use absolute path
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
            app.logger.info(f"Updated database URI to: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Drop existing tables if they exist
            try:
                db.drop_all()
                app.logger.info("Dropped all existing tables")
            except Exception as e:
                app.logger.error(f"Error dropping tables: {str(e)}")
                raise e
            
            # Create all tables
            try:
                db.create_all()
                app.logger.info("Created all tables")
            except Exception as e:
                app.logger.error(f"Error creating tables: {str(e)}")
                raise e
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            app.logger.info(f"Created tables: {tables}")
            
            # Create admin user
            try:
                admin = User(
                    username='admin',
                    email='admin@healthyrizz.com',
                    phone='1234567890',  # Required field
                    is_admin=True
                )
                admin.set_password('admin123')  # Set a default password
                db.session.add(admin)
                db.session.commit()
                app.logger.info(f"Created admin user with ID: {admin.id}")
            except Exception as e:
                app.logger.error(f"Error creating admin user: {str(e)}")
                raise e
            
            # Create test blog posts
            test_posts = [
                {
                    'title': '10 Healthy Breakfast Ideas for Busy Mornings',
                    'content': 'Start your day right with these quick and nutritious breakfast ideas. From overnight oats to protein-packed smoothies, we\'ve got you covered with easy-to-make recipes that will keep you energized throughout the morning.',
                    'category': 'Nutrition',
                    'tags': 'breakfast, healthy eating, meal prep',
                    'is_published': True,
                    'is_featured': True
                },
                {
                    'title': 'The Ultimate Guide to Strength Training',
                    'content': 'Learn the fundamentals of strength training and how to build muscle effectively. This comprehensive guide covers everything from proper form to workout programming for beginners and advanced lifters alike.',
                    'category': 'Fitness',
                    'tags': 'strength training, workout, fitness tips',
                    'is_published': True,
                    'is_featured': False
                },
                {
                    'title': 'Mindful Eating: A Path to Better Health',
                    'content': 'Discover how mindful eating can transform your relationship with food. Learn practical techniques to eat more mindfully, understand your hunger cues, and develop a healthier relationship with food.',
                    'category': 'Wellness',
                    'tags': 'mindful eating, wellness, healthy habits',
                    'is_published': True,
                    'is_featured': False
                }
            ]
            
            # Create posts one by one with detailed error handling
            for post_data in test_posts:
                try:
                    slug = post_data['title'].lower().replace(' ', '-')
                    app.logger.info(f"Creating post: {post_data['title']}")
                    
                    post = BlogPost(
                        title=post_data['title'],
                        slug=slug,
                        content=post_data['content'],
                        category=post_data['category'],
                        tags=post_data['tags'],
                        author_id=admin.id,
                        is_published=post_data['is_published'],
                        is_featured=post_data['is_featured'],
                        summary=post_data['content'][:200] + '...',
                        created_at=datetime.now(),
                        published_date=datetime.now() if post_data['is_published'] else None
                    )
                    
                    # Log post details before adding to session
                    app.logger.info(f"Post details before adding to session: {post.__dict__}")
                    
                    db.session.add(post)
                    db.session.flush()
                    app.logger.info(f"Created test post: {post.title} (ID: {post.id})")
                except Exception as e:
                    app.logger.error(f"Error creating test post '{post_data['title']}': {str(e)}")
                    db.session.rollback()
                    continue
            
            try:
                db.session.commit()
                app.logger.info("Successfully committed test blog posts")
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error committing test posts: {str(e)}")
                raise e
            
            # Verify posts were created
            posts = BlogPost.query.all()
            app.logger.info(f"After creation: Found {len(posts)} blog posts")
            
            if len(posts) == 0:
                app.logger.error("No posts were created despite no errors!")
                # Try to query the table directly
                try:
                    result = db.session.execute("SELECT * FROM blog_posts").fetchall()
                    app.logger.info(f"Direct SQL query found {len(result)} posts")
                except Exception as e:
                    app.logger.error(f"Error querying blog_posts table directly: {str(e)}")
            
            for post in posts:
                app.logger.info(f"Post: {post.title} (ID: {post.id}, Published: {post.is_published}, Featured: {post.is_featured}, Author: {post.author_id})")
                
    except Exception as e:
        app.logger.error(f"Error during database initialization: {str(e)}")
        raise e

def check_and_init_db():
    """Check if database exists and initialize if needed"""
    try:
        with app.app_context():
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'healthyrizz.db')
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if not os.path.exists(db_path) or not tables:
                app.logger.info("Database not found or empty, initializing...")
                init_db()
            else:
                app.logger.info("Database exists and has tables")
    except Exception as e:
        app.logger.error(f"Error checking/initializing database: {str(e)}")
        raise e

# Initialize database when app starts
check_and_init_db()

@app.context_processor
def inject_now():
    from datetime import datetime, timedelta
    return {
        'now': datetime.now(),
        'datetime': datetime,
        'timedelta': timedelta
    }
    
@app.context_processor
def inject_active_banner():
    # Get the active banner if one exists, with error handling
    try:
        banner = Banner.get_active_banner()
        app.logger.debug(f"Active banner found: {banner.message if banner else 'None'}")
        return {'banner': banner}
    except Exception as e:
        # Log the error
        app.logger.error(f"Error fetching active banner: {str(e)}")
        # Return None for banner to avoid breaking templates
        return {'banner': None}
    
@app.context_processor
def inject_current_user():
    """Inject current user data into all templates"""
    try:
        if current_user.is_authenticated:
            return {'current_user': current_user}
        elif 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                return {'current_user': user}
            else:
                session.pop('user_id', None)
    except Exception as e:
        app.logger.error(f"Error in inject_current_user: {str(e)}")
        session.pop('user_id', None)
    return {'current_user': None}

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    app.logger.info(f"404 error: {request.path}")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    app.logger.error(f"500 error: {str(e)}")
    error_message = "An unexpected error occurred. Our team has been notified."
    return render_template('error.html', error=error_message), 500

# Global error handler to catch database transaction errors
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions"""
    if isinstance(e, NotFound):
        return render_template('404.html'), 404
    elif isinstance(e, BadRequest):
        return render_template('400.html'), 400
    elif isinstance(e, Unauthorized):
        return render_template('401.html'), 401
    elif isinstance(e, Forbidden):
        return render_template('403.html'), 403
    else:
        # Log the error
        app.logger.error(f"Unhandled exception: {str(e)}")
        return render_template('500.html'), 500

# Security headers middleware
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://js.stripe.com; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://fonts.googleapis.com; img-src 'self' data:; connect-src 'self'; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; object-src 'none'; media-src 'self'; frame-src https://js.stripe.com;"
    return response

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First try to use Flask-Login's current_user if available
        try:
            from flask_login import current_user
            
            if current_user.is_authenticated:
                # If Flask-Login user is authenticated, ensure session is also set for compatibility
                if 'user_id' not in session:
                    session['user_id'] = current_user.id
                
                # User is logged in, proceed with the request
                return f(*args, **kwargs)
        except Exception as e:
            app.logger.warning(f"Error checking Flask-Login status: {str(e)}")
                
        # Fall back to checking session
        if 'user_id' not in session:
            # Check for redirect loop detection
            redirect_count = session.get('redirect_count', 0)
            if redirect_count > 3:
                app.logger.error("Detected redirect loop, showing error page")
                session.pop('redirect_count', None)  # Clear the counter
                return render_template('error.html', 
                                    error_title="Authentication Error",
                                    error_message="We're having trouble with your login session. Please clear your cookies and try again.")
            
            # Increment redirect counter
            session['redirect_count'] = redirect_count + 1
            
            # Store current URL in session to redirect back after login
            session['post_login_redirect'] = request.url
            app.logger.info(f"User not logged in, redirecting to login page. Stored URL in session: {request.url}")
            flash('Please login to access this page', 'info')
            return redirect(url_for('login'))
        
        try:
            # Import db directly from models
            from database.models import db
            
            # Safely convert user_id to int
            try:
                user_id = int(session.get('user_id'))
            except (ValueError, TypeError):
                app.logger.error("Invalid user_id in session")
                session.pop('user_id', None)
                session.pop('redirect_count', None)  # Clear any redirect counter
                flash('Please login to access this page', 'error')
                return redirect(url_for('login'))
            
            # Verify user exists using the main session
            user = User.query.get(user_id)
            
            if not user:
                app.logger.warning(f"User ID {user_id} not found in database, clearing session")
                session.pop('user_id', None)
                session.pop('redirect_count', None)  # Clear any redirect counter
                flash('Please login to access this page', 'error')
                return redirect(url_for('login'))
            
            # User exists, so continue with the request
            # Clear any redirect counter since we're successfully authenticated
            session.pop('redirect_count', None)
            return f(*args, **kwargs)
            
        except Exception as e:
            # Log the error
            error_message = str(e)
            app.logger.error(f"Error in login_required: {error_message}")
            
            # Handle specific template errors separately
            if "Encountered unknown tag 'endblock'" in error_message:
                app.logger.error("Template error detected. This could be caused by a template rendering issue.")
                return render_template('error.html', 
                                     error_message="A template error occurred. Please try again or contact support.")
            
            # For database errors, rollback the transaction
            try:
                from database.models import db
                db.session.rollback()
                app.logger.info("Successfully rolled back transaction after error")
            except Exception as rollback_error:
                app.logger.error(f"Error rolling back transaction: {str(rollback_error)}")
            
            # Don't automatically clear the session for all errors
            # Only clear it for authentication-related errors
            if "database" in error_message.lower() or "session" in error_message.lower():
                session.pop('user_id', None)
                flash('An error occurred with your session. Please log in again.', 'error')
                return redirect(url_for('login', next=request.url))
            
            # For other errors, just show an error page
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('index'))
            
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # First check if user is logged in via Flask-Login
            if not current_user.is_authenticated:
                app.logger.info(f"User not logged in, redirecting to login page. Next URL: {request.url}")
                flash('Please login to access this page', 'error')
                return redirect(url_for('login', next=request.url))
            
            # Check if user is admin
            if not current_user.is_admin:
                app.logger.warning(f"User {current_user.email} attempted to access admin page without admin privileges")
                flash('You do not have permission to access this page', 'error')
                return redirect(url_for('index'))
            
            # User is admin, proceed with request
            return f(*args, **kwargs)
            
        except Exception as e:
            app.logger.error(f"Error in admin_required: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('login', next=request.url))
            
    return decorated_function

@app.route('/')
def index():
    # Get active FAQs ordered by their display order
    faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.order, FAQ.created_at).all()
    
    # Get homepage content from database
    hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.order, HeroSlide.created_at).all()
    videos = Video.query.filter_by(is_active=True).order_by(Video.order, Video.created_at).all()
    team_members = TeamMember.query.filter_by(is_active=True).order_by(TeamMember.order, TeamMember.created_at).all()
    
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
            {'title': 'Customer Success Stories', 'description': 'Hear from our satisfied customers about their transformation journey with HealthyRizz nutrition plans.', 'youtube_url': 'https://www.youtube.com/watch?v=kJQP7kiw5Fk', 'thumbnail_url': '/static/images/healthy-meal-bowl.webp'},
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
                         site_settings=site_settings)

@app.route('/trial-request/<int:plan_id>', methods=['GET', 'POST'])
def trial_request(plan_id):
    """
    Handle trial meal plan requests.
    This allows users to request a 1-day trial of a meal plan at a customized trial price.
    Requests are stored in the database for admin review and payment processing.
    """
    # Get the meal plan
    meal_plan = MealPlan.query.get_or_404(plan_id)
    
    # Check if this meal plan is available for trial
    if not meal_plan.available_for_trial:
        flash('This meal plan is not available for trial. Please select an available plan.', 'error')
        return redirect(url_for('meal_plans'))
    
    # Create the form
    form = TrialRequestForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Create a new trial request
            trial = TrialRequest(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                address=form.address.data,
                city=form.city.data,
                province=form.province.data,
                postal_code=form.postal_code.data,
                meal_plan_id=plan_id,
                notes=form.additional_notes.data if form.additional_notes.data else None,
                preferred_date=form.preferred_delivery_date.data if form.preferred_delivery_date.data else None
            )
            
            db.session.add(trial)
            db.session.commit()
            
            # Send email notifications
            try:
                # Send notification to admin
                send_trial_request_notification(trial)
                # Send confirmation to customer
                send_trial_confirmation(trial)
                app.logger.info(f"Email notifications sent for trial request {trial.id}")
            except Exception as e:
                app.logger.error(f"Error sending email notifications: {str(e)}")
                # Don't fail the request if email fails
            
            flash('Your trial request has been submitted successfully! Our team will contact you shortly to arrange delivery and payment details.', 'success')
            return redirect(url_for('meal_plans'))
            
        except Exception as e:
            app.logger.error(f"Error submitting trial request: {str(e)}")
            db.session.rollback()
            flash('An error occurred while submitting your request. Please try again.', 'error')
    
    return render_template('trial_request.html', form=form, meal_plan=meal_plan)

@app.route('/meal-plans')
def meal_plans():
    """Display meal plans with filtering options"""
    # Get filter parameters
    gender = request.args.get('gender', '')
    meal_type = request.args.get('type', '')  # balanced, weight-loss, athletic, vegetarian, keto
    breakfast = request.args.get('breakfast', '')
    trial_only = request.args.get('trial_only', '')
    
    # Start with all active meal plans
    query = MealPlan.query.filter(MealPlan.is_active == True)
    
    # Apply gender filter if specified
    if gender:
        query = query.filter((MealPlan.for_gender == gender) | (MealPlan.for_gender == 'both'))
        
    # Apply breakfast filter if specified
    if breakfast:
        includes_breakfast = True if breakfast == '1' else False
        query = query.filter(MealPlan.includes_breakfast == includes_breakfast)
        
    # Apply meal type filter if specified
    if meal_type:
        if meal_type == 'vegetarian':
            query = query.filter(MealPlan.is_vegetarian == True)
        elif meal_type == 'weight-loss':
            query = query.filter(MealPlan.tag == 'Low Carb')
        elif meal_type == 'athletic':
            query = query.filter(MealPlan.tag == 'High Protein')
        elif meal_type == 'balanced':
            query = query.filter(MealPlan.tag == 'Balanced')
        elif meal_type == 'keto':
            query = query.filter(MealPlan.tag == 'Keto')
        
    # Apply trial availability filter if specified
    if trial_only == '1':
        query = query.filter(MealPlan.available_for_trial == True)
        
    # Get the filtered plans
    plans = query.order_by(MealPlan.price_weekly).all()
    
    return render_template('meal_plans.html', plans=plans)

# Route to handle '/subscribe/<plan_id>' URLs and redirect to checkout
@app.route('/subscribe/<int:plan_id>')
def subscribe(plan_id):
    """
    Redirect /subscribe/<plan_id> requests to the checkout route.
    This prevents users from getting logged out when clicking 'Subscribe Now'
    by maintaining the session across the redirect.
    """
    # First try to use Flask-Login's current_user if available
    try:
        from flask_login import current_user
        if current_user.is_authenticated:
            # Set session user_id for compatibility
            session['user_id'] = current_user.id
            # Clear redirect counter
            session.pop('redirect_count', None)
    except Exception as e:
        app.logger.warning(f"Error checking Flask-Login status: {str(e)}")
    
    # Log session state
    user_id = session.get('user_id')
    app.logger.info(f"In /subscribe route: User ID in session: {user_id}")
    
    # Check for redirect loop detection
    redirect_count = session.get('redirect_count', 0)
    if redirect_count > 3:
        app.logger.error("Detected redirect loop, showing error page")
        session.pop('redirect_count', None)  # Clear the counter
        return render_template('error.html', 
                               error_title="Subscription Error",
                               error_message="We're having trouble processing your subscription. Please try again later or contact support.")
    
    # Increment redirect counter
    session['redirect_count'] = redirect_count + 1
    
    # Check if user is logged in
    if not user_id:
        app.logger.warning("User not logged in, redirecting to login page")
        flash('Please login to subscribe to a meal plan', 'info')
        
        # Store destination in session with query parameters included
        frequency = request.args.get('frequency', 'weekly')
        checkout_url = url_for('checkout', plan_id=plan_id, frequency=frequency)
        app.logger.info(f"Storing checkout URL in session: {checkout_url}")
        session['post_login_redirect'] = checkout_url
        return redirect(url_for('login'))
    
    # User is logged in, clear the redirect counter
    session.pop('redirect_count', None)
    
    # Pass along any query parameters that might be present
    query_string = request.query_string.decode('utf-8')
    redirect_url = url_for('checkout', plan_id=plan_id)
    
    if query_string:
        redirect_url += f'?{query_string}'
    
    # Use a response object to preserve the session
    response = make_response(redirect(redirect_url))
    
    # Log the redirection
    app.logger.info(f"Redirecting to: {redirect_url}, session contains user_id: {user_id}")
    
    return response

@app.route('/checkout/<int:plan_id>')
@login_required
@csrf.exempt
def checkout(plan_id):
    """Subscribe to a meal plan with proper total calculation and location dropdown"""
    try:
        # Get meal plan
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
        # Get frequency from query params (default to weekly)
        frequency = request.args.get('frequency', 'weekly')
        
        # Calculate prices properly
        if frequency == 'weekly':
            base_price = float(meal_plan.price_weekly)
        else:
            base_price = float(meal_plan.price_monthly)
        
        # Calculate GST (5%)
        gst_amount = base_price * 0.05
        total_amount = base_price + gst_amount
        
        # Get all active delivery locations for dropdown
        delivery_locations = DeliveryLocation.query.filter_by(is_active=True).order_by(DeliveryLocation.city).all()
        
        # Get user data if logged in
        user_data = None
        if current_user.is_authenticated:
            user_data = {
                'name': current_user.name,
                'email': current_user.email,
                'phone': current_user.phone,
                'address': current_user.address,
                'city': current_user.city,
                'state': current_user.state,
                'postal_code': current_user.postal_code
            }
        
        return render_template('checkout.html',
                             meal_plan=meal_plan,
                             frequency=frequency,
                             base_price=base_price,
                             gst_amount=gst_amount,
                             total_amount=total_amount,
                             delivery_locations=delivery_locations,
                             user_data=user_data)
                             
    except Exception as e:
        app.logger.error(f"Error in checkout route: {str(e)}")
        flash('An error occurred while loading the checkout page.', 'error')
        return redirect(url_for('meal_plans'))



@app.route('/verify_payment', methods=['POST'])
@login_required
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
            return redirect(url_for('meal_plans'))
        
        # Get user
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if not user:
            flash('User not found. Please login again.', 'error')
            return redirect(url_for('login'))
        
        # Create Order record for payment history
        order = Order(
            user_id=user.id,
            meal_plan_id=order_data['notes']['plan_id'],
            amount=float(order_data['amount']) / 100,  # Convert from paise to rupees
            status='confirmed',
            payment_status='captured',
            payment_id=razorpay_payment_id,
            order_id=razorpay_order_id,
            created_at=datetime.now()
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
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
            ),
            order_id=order.id  # Link to the order
        )
        
        db.session.add(subscription)
        
        # Track coupon usage if coupon was applied
        if order_data['notes'].get('applied_coupon'):
            coupon = CouponCode.query.filter_by(code=order_data['notes']['applied_coupon']).first()
            if coupon:
                # Create coupon usage record
                coupon_usage = CouponUsage(
                    coupon_id=coupon.id,
                    user_id=user.id,
                    order_id=order.id
                )
                db.session.add(coupon_usage)
                
                # Update coupon usage count
                coupon.current_uses += 1
        
        db.session.commit()
        
        # Clear session data
        session.pop('razorpay_order', None)
        
        flash('Your subscription has been created successfully!', 'success')
        return redirect(url_for('profile'))
        
    except Exception as e:
        app.logger.error(f"Error verifying payment: {str(e)}")
        db.session.rollback()
        flash('An error occurred while processing your payment. Please contact support.', 'error')
        return redirect(url_for('meal_plans'))

@app.route('/checkout-success')
def checkout_success():
    """
    Handle successful checkout.
    """
    try:
        # Get checkout data from session
        checkout_data = session.get('checkout_data')
        checkout_session_id = session.get('checkout_session_id')
        
        if not checkout_data or not checkout_session_id:
            # If no session data, try to get from URL parameters or redirect
            flash('Invalid checkout session. Please try again.', 'warning')
            return redirect(url_for('meals'))
        
        # Get meal plan
        plan_id = checkout_data.get('plan_id')
        if not plan_id:
            flash('Invalid meal plan. Please try again.', 'warning')
            return redirect(url_for('meals'))
            
        meal_plan = MealPlan.query.get(plan_id)
        if not meal_plan:
            flash('Meal plan not found. Please try again.', 'warning')
            return redirect(url_for('meals'))
        
        # Get user ID from session
        user_id = session.get('user_id')
        
        if not user_id:
            flash('User session expired. Please try again.', 'warning')
            return redirect(url_for('login'))
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            flash('User not found. Please try again.', 'warning')
            return redirect(url_for('login'))
        
        # Check if subscription already exists for this session
        existing_subscription = Subscription.query.filter_by(
            user_id=user_id,
            stripe_subscription_id=checkout_session_id
        ).first()
        
        if existing_subscription:
            subscription = existing_subscription
        else:
            # Create subscription record
            frequency = SubscriptionFrequency.WEEKLY if checkout_data.get('frequency') == 'weekly' else SubscriptionFrequency.MONTHLY
            
            # Create subscription
            subscription = Subscription(
                user_id=user_id,
                meal_plan_id=plan_id,
                frequency=frequency,
                status=SubscriptionStatus.ACTIVE,
                price=checkout_data.get('price', meal_plan.get_price_weekly()),
                stripe_customer_id=user.stripe_customer_id if user else None,
                stripe_subscription_id=checkout_session_id,
                vegetarian_days=checkout_data.get('vegetarian_days', ''),
                start_date=datetime.now(),
                # Set current period based on frequency
                current_period_start=datetime.now(),
                current_period_end=(
                    datetime.now() + timedelta(days=7) if frequency == SubscriptionFrequency.WEEKLY 
                    else datetime.now() + timedelta(days=30)
                )
            )
            
            db.session.add(subscription)
            db.session.commit()
        
        # Clear checkout session data
        session.pop('checkout_data', None)
        session.pop('checkout_session_id', None)
        
        # Show success page
        return render_template('checkout_success.html', 
                              subscription=subscription, 
                              plan=meal_plan)
                              
    except Exception as e:
        app.logger.error(f"Error processing checkout success: {str(e)}")
        flash('An error occurred while processing your subscription.', 'danger')
        return redirect(url_for('meals'))

@app.route('/checkout-cancel')
def checkout_cancel():
    """
    Handle cancelled checkout.
    """
    # Clear checkout session data
    session.pop('checkout_data', None)
    session.pop('checkout_session_id', None)
    
    flash('Your checkout was cancelled. Please try again when you\'re ready.', 'info')
    return redirect(url_for('meals'))

@app.route('/admin/blog')
@admin_required
def admin_blog():
    """Admin blog management page"""
    try:
        # Get all blog posts with author information
        posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        app.logger.info(f"Admin blog route - Found {len(posts)} blog posts")
        
        # Get unique categories
        categories = db.session.query(BlogPost.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        # Log post details for debugging
        for post in posts:
            app.logger.info(f"Admin blog post: {post.title} (ID: {post.id}, Published: {post.is_published}, Featured: {post.is_featured}, Created: {post.created_at})")
        
        return render_template('admin/blog.html', posts=posts, categories=categories)
    except Exception as e:
        app.logger.error(f"Error fetching blog posts: {str(e)}")
        flash('Error loading blog posts', 'error')
        return render_template('admin/blog.html', posts=[], categories=[])

@app.route('/blog')
def blog():
    """Public blog page"""
    try:
        # Get published blog posts with author information
        posts = BlogPost.query.filter_by(is_published=True).order_by(
            BlogPost.is_featured.desc(),  # Featured posts first
            BlogPost.published_date.desc()  # Then by publish date
        ).all()
        
        # Get unique categories
        categories = db.session.query(BlogPost.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        app.logger.info(f"Public blog route - Found {len(posts)} published blog posts")
        
        # Log post details for debugging
        for post in posts:
            app.logger.info(f"Public blog post: {post.title} (ID: {post.id}, Featured: {post.is_featured}, Published: {post.published_date}, Author: {post.author_id})")
        
        return render_template('blog.html', posts=posts, categories=categories)
    except Exception as e:
        app.logger.error(f"Error fetching published blog posts: {str(e)}")
        flash('Error loading blog posts', 'error')
        return render_template('blog.html', posts=[], categories=[])

@app.route('/blog/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    # Create newsletter form for the blog post page
    newsletter_form = NewsletterForm()
    return render_template('blog-post.html', post=post, newsletter_form=newsletter_form)

@app.route('/newsletter-signup', methods=['POST'])
def newsletter_signup():
    """Handle newsletter signups"""
    form = NewsletterForm()
    
    if form.validate_on_submit():
        email = form.email.data
        
        # Check if email already exists
        existing_signup = Newsletter.query.filter_by(email=email).first()
        if existing_signup:
            flash('You are already subscribed to our newsletter!', 'info')
        else:
            # Create new newsletter subscription
            newsletter = Newsletter(email=email)
            db.session.add(newsletter)
            try:
                db.session.commit()
                flash('Thank you for subscribing to our newsletter!', 'success')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error signing up for newsletter: {str(e)}")
                flash('There was an issue processing your subscription. Please try again.', 'error')
    else:
        # Form validation failed
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", 'error')
    
    # Redirect back to referring page or home
    return redirect(request.referrer or url_for('index'))
    
@app.route('/meal-calculator', methods=['GET'])
@csrf.exempt
def meal_calculator():
    return render_template('meal_calculator.html')
    
@app.route('/calculate-meal-plan', methods=['POST'])
def calculate_meal_plan():
    try:
    # Get form data
        age = int(request.form.get('age'))
        gender = request.form.get('gender')
        weight = float(request.form.get('weight'))
        height = float(request.form.get('height'))
        activity_level = request.form.get('activity_level')
        goal = request.form.get('goal')
        
        # Calculate BMR using Mifflin-St Jeor Equation
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Apply activity multiplier
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very': 1.725,
            'extra': 1.9
        }
        
        tdee = bmr * activity_multipliers.get(activity_level, 1.2)
        
        # Adjust calories based on goal
        if goal == 'lose':
            calories = tdee - 500  # 500 calorie deficit
        elif goal == 'gain':
            calories = tdee + 500  # 500 calorie surplus
        else:  # maintain
            calories = tdee
        
        # Calculate macronutrients
        protein = weight * 2.2  # 2.2g per kg of body weight
        fat = (calories * 0.25) / 9  # 25% of calories from fat
        carbs = (calories - (protein * 4) - (fat * 9)) / 4  # Remaining calories from carbs
        
        # Find suitable meal plans
        suitable_plans = MealPlan.query.filter(
            MealPlan.is_active == True,
            MealPlan.calories.between(calories - 200, calories + 200)
        ).all()
        
        return jsonify({
            'success': True,
            'calculations': {
                'bmr': round(bmr),
                'tdee': round(tdee),
                'calories': round(calories),
                'protein': round(protein),
                'fat': round(fat),
                'carbs': round(carbs)
            },
            'suitable_plans': [{
                'id': plan.id,
                'name': plan.name,
                'calories': plan.calories,
                'protein': plan.protein,
                'price_weekly': plan.price_weekly,
                'price_monthly': plan.price_monthly
            } for plan in suitable_plans]
        })
        
    except Exception as e:
        app.logger.error(f"Error calculating meal plan: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while calculating your meal plan. Please try again.'
        }), 500

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("30 per minute")
def login():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Get user from database
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                # Set user ID in session
                session['user_id'] = user.id
                session.permanent = True
                
                # Login user with Flask-Login
                login_user(user, remember=True)
                
                # Log successful login
                app.logger.info(f"User {user.id} ({user.email}) logged in successfully")
                
                # Get the next URL from either session or query parameter
                next_url = session.pop('post_login_redirect', None) or request.args.get('next')
                
                # Handle admin redirects
                if user.is_admin:
                    if next_url and '/admin' in next_url:
                        flash('Login successful!', 'success')
                        return redirect(next_url)
                    else:
                        flash('Login successful!', 'success')
                        return redirect(url_for('admin_dashboard'))  # Changed from admin.admin_dashboard
                else:
                    # Regular user - go to next page or profile
                    destination = next_url if next_url else url_for('profile')
                    flash('Login successful!', 'success')
                    return redirect(destination)
            else:
                flash('Invalid email or password', 'error')
                return render_template('login.html')
        
        # Get the next parameter for the login form
        next_url = request.args.get('next', '')
        
        # Render login page
        return render_template('login.html', next=next_url)
    except Exception as e:
        app.logger.error(f"Error in login route: {str(e)}")
        flash('An error occurred during login. Please try again.', 'error')
        return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def forgot_password():
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
                app.logger.error(f"Error sending password reset email: {str(e)}")
                flash('An error occurred while sending the password reset email. Please try again.', 'error')
        else:
            # Don't reveal whether the email exists or not
            flash('If an account exists with that email, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def reset_password(token):
    try:
        email = verify_password_reset_token(token)
        if not email:
            flash('The password reset link is invalid or has expired.', 'error')
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('reset_password.html')
            
            user = User.query.filter_by(email=email).first()
            if user:
                user.set_password(password)
                db.session.commit()
                flash('Your password has been reset successfully.', 'success')
                return redirect(url_for('login'))
            else:
                flash('User not found.', 'error')
                return redirect(url_for('login'))
        
        return render_template('reset_password.html')
    except Exception as e:
        app.logger.error(f"Error in reset_password route: {str(e)}")
        flash('An error occurred while resetting your password. Please try again.', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Get form data
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            name = request.form.get('name')
            phone = request.form.get('phone')
            address = request.form.get('address')
            city = request.form.get('city')
            province = request.form.get('province')
            postal_code = request.form.get('postal_code')
            
            # Validate required fields
            if not all([email, password, confirm_password, name]):
                flash('Please fill in all required fields.', 'error')
                return redirect(url_for('register'))
            
            # Check if passwords match
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('register'))
            
            # Check if email is already registered
            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'error')
                return redirect(url_for('register'))
            
            # Check if delivery is available in the area
            if postal_code and city and province:
                delivery_available = DeliveryLocation.check_delivery_available(
                    postal_code, city, province
                )
                
                if not delivery_available:
                    session['location_info'] = {
                        'city': city,
                        'province': province,
                        'postal_code': postal_code
                    }
                    flash('Delivery is not available in your area yet. We will notify you when it becomes available.', 'error')
                    return redirect(url_for('coming_soon'))
            
            # Create new user using the create_user method
            user = User.create_user(
                email=email,
                username=name,  # Use name as username
                password=password,
                phone=phone,
                address=address,
                city=city,
                province=province,
                postal_code=postal_code
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html', title='Register')

@app.route('/coming-soon')
def coming_soon():
    # Get location info from session
    location_info = session.get('location_info', {})
    
    # Get active delivery locations to display
    active_locations = DeliveryLocation.query.filter_by(is_active=True).all()
    
    city = location_info.get('city', '')
    province = location_info.get('province', '')
    postal_code = location_info.get('postal_code', '')
    
    return render_template('coming-soon.html', 
                          city=city, 
                          province=province, 
                          postal_code=postal_code,
                          active_locations=active_locations)

@app.route('/offline')
def offline():
    """Offline page for PWA functionality - adds support for Safari and other browsers"""
    return render_template('offline.html')

@app.route('/get-active-provinces', methods=['GET'])
@csrf.exempt  # Exempt this route from CSRF protection for AJAX
def get_active_provinces():
    """Get a list of provinces with active delivery locations"""
    from sqlalchemy import func
    # Import db to ensure it's available
    from database.models import db
    
    # Clear SQLAlchemy session to ensure we get fresh data
    db.session.expire_all()
    
    # Query for provinces that have active delivery locations
    provinces = db.session.query(DeliveryLocation.province).filter(
        DeliveryLocation.is_active == True
    ).distinct().order_by(DeliveryLocation.province).all()
    
    province_list = [province[0] for province in provinces]
    app.logger.debug(f"Found active province(s): {province_list}")
    
    # Admins can see all provinces
    is_admin = current_user.is_authenticated and current_user.is_admin
    
    # If no provinces found or user is admin, return all Canadian provinces
    if not province_list or is_admin:
        province_list = ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'ON', 'PE', 'QC', 'SK', 'NT', 'NU', 'YT']
        if is_admin:
            app.logger.debug("Admin user, showing all provinces")
        else:
            app.logger.debug("No active provinces found, showing all provinces")
    
    # Map province codes to full names for display
    province_map = {
        'AB': 'Alberta',
        'BC': 'British Columbia',
        'MB': 'Manitoba',
        'NB': 'New Brunswick',
        'NL': 'Newfoundland and Labrador',
        'NS': 'Nova Scotia',
        'ON': 'Ontario',
        'PE': 'Prince Edward Island',
        'QC': 'Quebec',
        'SK': 'Saskatchewan',
        'NT': 'Northwest Territories',
        'NU': 'Nunavut',
        'YT': 'Yukon'
    }
    
    # Format provinces as [{code: 'AB', name: 'Alberta'}, ...]
    formatted_provinces = [{'code': p, 'name': province_map.get(p, p)} for p in province_list]
    
    return jsonify({
        'success': True,
        'provinces': formatted_provinces,
        'is_admin': is_admin
    })

@app.route('/get-cities-by-province', methods=['GET'])
@csrf.exempt  # Exempt this route from CSRF protection for AJAX
def get_cities_by_province():
    """Get a list of available cities for a given province"""
    province = request.args.get('province', '')
    postal_code = request.args.get('postal_code', '')
    user_city = request.args.get('user_city', '')
    
    if not province:
        return jsonify({'success': False, 'message': 'Province is required'})
    
    # Get distinct cities for the province
    from sqlalchemy import func
    # Import db to ensure it's available
    from database.models import db
    
    # Clear SQLAlchemy session to ensure we get fresh data
    db.session.expire_all()
    
    # Force SQLAlchemy to re-execute the query for fresh data
    db.session.commit()
    
    cities = db.session.query(DeliveryLocation.city).filter(
        DeliveryLocation.province == province.upper(),
        DeliveryLocation.is_active == True
    ).distinct().order_by(DeliveryLocation.city).all()
    
    city_list = [city[0] for city in cities]
    app.logger.debug(f"Found cities for province {province}: {city_list}")
    
    # Check if user is from an active delivery area to show "Other" option
    is_active_location = False
    
    # Check if we have a postal code (with or without user city)
    if postal_code and len(postal_code) >= 3:
        # Get the prefix (first 3 characters of the postal code)
        prefix = postal_code[:3].upper()
        
        # Check if user location matches any active delivery area by postal code prefix
        location = DeliveryLocation.query.filter(
            DeliveryLocation.postal_code_prefix == prefix,
            DeliveryLocation.province == province.upper(),
            DeliveryLocation.is_active == True
        ).first()
        
        is_active_location = location is not None
        app.logger.debug(f"Postal code {postal_code} is in active area: {is_active_location}")
        
        # If user is from an active delivery area, add "Other" to the list
        if is_active_location and "Other" not in city_list:
            city_list.append("Other")
    
    # If the user is an admin, let them see all Canadian cities
    if current_user.is_authenticated and current_user.is_admin:
        if "Other" not in city_list:
            city_list.append("Other")
            app.logger.debug("Admin user, adding 'Other' option")
    
    return jsonify({
        'success': True,
        'cities': city_list,
        'is_active_location': is_active_location
    })

@app.route('/request-service', methods=['POST'])
def request_service():
    """Submit a request for delivery service in a new area"""
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    city = request.form.get('city', '')
    province = request.form.get('province', '')
    postal_code = request.form.get('postal_code', '')
    other_location = request.form.get('other_location', '')
    message = request.form.get('message', '')
    
    if not name or not email or not province or not postal_code:
        flash('Please fill in all required fields', 'error')
        return redirect(url_for('index'))
    
    # If city is "Other", use the specific location provided
    if city == "Other":
        if not other_location:
            flash('Please specify your location', 'error')
            return redirect(url_for('index'))
        
        # Store both the "Other" city and the specific location in the message
        message = f"Specific location: {other_location}\n\n{message}"
    
    # Create a new service request
    from models import ServiceRequest
    service_request = ServiceRequest(
        name=name,
        email=email,
        phone=phone,
        city=city,
        province=province,
        postal_code=postal_code,
        message=message
    )
    
    try:
        db.session.add(service_request)
        db.session.commit()
        flash('Your service request has been submitted. We will notify you when delivery becomes available in your area.', 'success')
    except Exception as e:
        app.logger.error(f"Error submitting service request: {str(e)}")
        db.session.rollback()
        flash('An error occurred while submitting your request. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/check-location', methods=['POST'])
@csrf.exempt  # Exempt this route from CSRF protection for AJAX
def check_location():
    """Check if delivery is available in the specified location"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
            
        postal_code = data.get('postal_code', '').strip()
        city = data.get('city', '').strip()
        province = data.get('province', '').strip()
        
        # Basic validation
        if not postal_code or not city or not province:
            return jsonify({
                'success': False,
                'message': 'Please provide postal code, city, and province'
            }), 400
            
        # Validate postal code format (Canadian format)
        if not re.match(r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$', postal_code):
            return jsonify({
                'success': False,
                'message': 'Please enter a valid Canadian postal code'
            }), 400
            
        # Check if delivery is available
        from database.models import DeliveryLocation
        is_available = DeliveryLocation.check_delivery_available(postal_code, city, province)
        
        if is_available:
            return jsonify({
                'success': True,
                'message': 'Delivery is available in your area!',
                'is_available': True
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Sorry, delivery is not available in your area yet.',
                'is_available': False
            })
            
    except Exception as e:
        current_app.logger.error(f"Error checking location: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while checking your location'
        }), 500

@app.route('/subscribe-newsletter', methods=['POST'])
def subscribe_newsletter():
    email = request.form.get('email', '').strip().lower()
    
    if not email:
        flash('Please enter an email address', 'error')
        return redirect(request.referrer or url_for('index'))
    
    # Import db to ensure it's available
    from models import db
    
    # Check if email already exists in newsletter
    existing_subscription = Newsletter.query.filter_by(email=email).first()
    
    if existing_subscription:
        if existing_subscription.is_active:
            flash('You are already subscribed to our newsletter', 'info')
        else:
            # Reactivate subscription
            existing_subscription.is_active = True
            db.session.commit()
            flash('Your newsletter subscription has been reactivated', 'success')
    else:
        # Create new subscription
        new_subscription = Newsletter(email=email)
        db.session.add(new_subscription)
        db.session.commit()
        flash('Thank you for subscribing to our newsletter!', 'success')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/verify-coupon', methods=['GET', 'POST'])
@csrf.exempt
def verify_coupon():
    # Handle both GET and POST requests
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        order_amount = float(request.form.get('order_amount', 0))
        frequency = request.form.get('frequency', 'weekly')
        plan_id = request.form.get('plan_id')
    else:
        code = request.args.get('code', '').strip().upper()
        order_amount = float(request.args.get('order_amount', 0) or 0)
        frequency = request.args.get('frequency', 'weekly')
        plan_id = request.args.get('plan_id')
        
    # If we have a plan_id, get the price for order_amount calculation
    if plan_id and not order_amount:
        try:
            plan = MealPlan.query.get(plan_id)
            if plan:
                if frequency == 'weekly':
                    order_amount = float(plan.price_weekly)
                else:
                    order_amount = float(plan.price_monthly)
        except Exception as e:
            app.logger.error(f"Error getting plan price: {e}")
    
    if not code:
        return jsonify({'success': False, 'message': 'Please enter a coupon code'})
    
    coupon = CouponCode.query.filter_by(code=code).first()
    
    if not coupon:
        return jsonify({'success': False, 'message': 'Invalid coupon code'})
    
    if not coupon.is_valid():
        return jsonify({'success': False, 'message': 'This coupon has expired or is no longer valid'})
    
    # Check if coupon is single-use and user has already used it
    if coupon.is_single_use and 'user_id' in session:
        user_id = session['user_id']
        existing_usage = CouponUsage.query.filter_by(
            coupon_id=coupon.id,
            user_id=user_id
        ).first()
        
        if existing_usage:
            return jsonify({
                'success': False,
                'message': 'You have already used this coupon code'
            })
    
    # Check minimum order value
    if order_amount < float(coupon.min_order_value):
        return jsonify({
            'success': False, 
            'message': f'This coupon requires a minimum order of ${coupon.min_order_value}'
        })
    
    # Calculate discount
    discount_amount = coupon.calculate_discount(order_amount)
    
    # Format discount description based on type
    discount_description = "Discount"
    if coupon.discount_type == 'percent':
        discount_description = f"{coupon.discount_value}% discount"
    elif coupon.discount_type == 'fixed':
        discount_description = f"${coupon.discount_value} discount"
    elif coupon.discount_type == 'shipping':
        discount_description = "Free shipping"
    
    return jsonify({
        'success': True,
        'valid': True,
        'message': 'Coupon applied successfully!',
        'discount_amount': discount_amount,
        'discount_description': discount_description,
        'order_total': max(0, order_amount - discount_amount)
    })

@app.route('/validate-coupon')
@csrf.exempt
def validate_coupon():
    """Validate coupon code for GET requests (used for recalculations)"""
    code = request.args.get('code', '').strip().upper()
    amount = float(request.args.get('amount', 0))
    
    if not code:
        return jsonify({'valid': False, 'message': 'No coupon code provided'})
    
    coupon = CouponCode.query.filter_by(code=code).first()
    
    if not coupon or not coupon.is_valid():
        return jsonify({'valid': False, 'message': 'Invalid or expired coupon'})
    
    if amount < float(coupon.min_order_value):
        return jsonify({'valid': False, 'message': f'Minimum order amount is ${coupon.min_order_value}'})
    
    discount_amount = coupon.calculate_discount(amount)
    
    return jsonify({
        'valid': True,
        'discount_amount': discount_amount,
        'order_total': max(0, amount - discount_amount)
    })

@app.route('/profile')
@login_required
def profile():
    """User profile page to view and manage account and subscriptions"""
    # Initialize variables with default values
    active_subscriptions = []
    paused_subscriptions = []
    canceled_subscriptions = []
    subscription_deliveries = {}
    payments = []
    orders = []
    
    try:
        # Get user's orders for payment history
        orders = Order.query.filter_by(
            user_id=current_user.id
        ).order_by(Order.created_at.desc()).all()
        
        # Get user's subscriptions
        subscriptions = Subscription.query.filter_by(
            user_id=current_user.id
        ).order_by(Subscription.start_date.desc()).all()
        
        # Group subscriptions by status
        for s in subscriptions:
            if s.status == SubscriptionStatus.ACTIVE:
                active_subscriptions.append(s)
            elif s.status == SubscriptionStatus.PAUSED:
                paused_subscriptions.append(s)
            elif s.status == SubscriptionStatus.CANCELED:
                canceled_subscriptions.append(s)
        
        # Get upcoming deliveries for active and paused subscriptions
        for subscription in active_subscriptions + paused_subscriptions:
            try:
                subscription_deliveries[subscription.id] = subscription.get_upcoming_deliveries(days=14)
            except Exception as del_error:
                app.logger.error(f"Error processing deliveries for subscription {subscription.id}: {str(del_error)}")
                subscription_deliveries[subscription.id] = []
        
        # Generate payment history from orders
        payments = []
        for order in orders:
            if order.meal_plan:
                payment = {
                    'date': order.created_at,
                    'description': f"{order.meal_plan.name} - Order #{order.id}",
                    'amount': float(order.amount),
                    'status': order.payment_status,
                    'order_id': order.id,
                    'payment_id': order.payment_id,
                    'invoice_url': '#'
                }
                payments.append(payment)
        
        # Sort payments by date
        if payments:
            payments.sort(key=lambda x: x.get('date', datetime.now()), reverse=True)
                
    except Exception as e:
        app.logger.error(f"Error in profile page: {str(e)}")
        db.session.rollback()
        flash('An error occurred while loading your profile. Please try again.', 'error')
    
    return render_template('profile.html', 
                          user=current_user,
                          active_subscriptions=active_subscriptions,
                          paused_subscriptions=paused_subscriptions,
                          canceled_subscriptions=canceled_subscriptions,
                          subscription_deliveries=subscription_deliveries,
                          payments=payments,
                          orders=orders)

@app.route('/profile/deliveries')
@login_required
def user_deliveries():
    """View user's upcoming and past deliveries with status"""
    upcoming_deliveries = []
    past_deliveries = []
    messages_by_delivery = {}
    
    try:
        # Get user's subscriptions
        subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
        subscription_ids = [sub.id for sub in subscriptions]
        
        # Get current date
        today = datetime.now().date()
        
        if subscription_ids:
            # Get upcoming deliveries
            upcoming_deliveries = Delivery.query.filter(
                Delivery.subscription_id.in_(subscription_ids),
                Delivery.delivery_date >= today
            ).order_by(Delivery.delivery_date).limit(10).all()
            
            # Get past deliveries (last 30 days)
            thirty_days_ago = today - timedelta(days=30)
            past_deliveries = Delivery.query.filter(
                Delivery.subscription_id.in_(subscription_ids),
                Delivery.delivery_date < today,
                Delivery.delivery_date >= thirty_days_ago
            ).order_by(Delivery.delivery_date.desc()).all()
            
            # Get delivery messages
            delivery_ids = [d.id for d in upcoming_deliveries + past_deliveries]
            if delivery_ids:
                messages = DeliveryMessage.query.filter(
                    DeliveryMessage.delivery_id.in_(delivery_ids)
                ).order_by(DeliveryMessage.created_at.desc()).all()
                
                for message in messages:
                    if message.delivery_id not in messages_by_delivery:
                        messages_by_delivery[message.delivery_id] = []
                    messages_by_delivery[message.delivery_id].append(message)
    
    except Exception as e:
        app.logger.error(f"Error in deliveries page: {str(e)}")
        db.session.rollback()
        flash('An error occurred while loading your deliveries. Please try again.', 'error')
    
    return render_template('deliveries.html',
                          upcoming_deliveries=upcoming_deliveries,
                          past_deliveries=past_deliveries,
                          messages_by_delivery=messages_by_delivery)

@app.route('/delivery/<int:delivery_id>', methods=['GET'])
@login_required
def view_delivery(delivery_id):
    """View details of a specific delivery"""
    try:
        # Get the delivery
        delivery = Delivery.query.get_or_404(delivery_id)
        
        # Verify ownership
        if delivery.subscription.user_id != current_user.id:
            flash('You do not have permission to view this delivery.', 'error')
            return redirect(url_for('user_deliveries'))
        
        # Get delivery messages
        messages = DeliveryMessage.query.filter_by(
            delivery_id=delivery_id
        ).order_by(DeliveryMessage.created_at.desc()).all()
        
        return render_template('delivery_detail.html',
                             delivery=delivery,
                             messages=messages)
    
    except Exception as e:
        app.logger.error(f"Error viewing delivery {delivery_id}: {str(e)}")
        flash('An error occurred while loading the delivery details.', 'error')
        return redirect(url_for('user_deliveries'))

@app.route('/subscription/pause/<int:subscription_id>', methods=['POST'])
@login_required
def pause_subscription(subscription_id):
    """Pause a subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        
        # Verify that the subscription belongs to the current user
        if subscription.user_id != current_user.id:
            flash('You do not have permission to manage this subscription', 'error')
            return redirect(url_for('profile'))
        
        # Only active subscriptions can be paused
        if subscription.status != SubscriptionStatus.ACTIVE:
            flash('Only active subscriptions can be paused', 'error')
            return redirect(url_for('profile'))
        
        # Pause the subscription
        subscription.pause()
        db.session.commit()
        
        # Send an SMS notification if the user has a phone number
        if current_user.phone:
            try:
                message = (
                    f"Hi {current_user.username.split()[0]}, your Fit Smart subscription to the {subscription.meal_plan.name} plan "
                    f"has been paused. You can resume your deliveries anytime from your profile."
                )
                send_sms(current_user.phone, message)
            except Exception as e:
                app.logger.error(f"Failed to send pause subscription SMS: {str(e)}")
        
        flash('Your subscription has been paused. You can resume it anytime.', 'success')
    except Exception as e:
        app.logger.error(f"Error pausing subscription {subscription_id}: {str(e)}")
        db.session.rollback()
        flash('Error pausing subscription. Please try again or contact support.', 'error')
    
    return redirect(url_for('profile'))

@app.route('/subscription/resume/<int:subscription_id>', methods=['POST'])
@login_required
def resume_subscription(subscription_id):
    """Resume a paused subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        
        # Verify that the subscription belongs to the current user
        if subscription.user_id != current_user.id:
            flash('You do not have permission to manage this subscription', 'error')
            return redirect(url_for('profile'))
        
        # Only paused subscriptions can be resumed
        if subscription.status != SubscriptionStatus.PAUSED:
            flash('Only paused subscriptions can be resumed', 'error')
            return redirect(url_for('profile'))
        
        # Resume the subscription
        subscription.resume()
        db.session.commit()
        
        # Calculate next delivery date (3 days from now)
        next_delivery_date = (datetime.now() + timedelta(days=3)).strftime('%A, %B %d')
        
        # Send an SMS notification if the user has a phone number
        if current_user.phone:
            try:
                message = (
                    f"Hi {current_user.username.split()[0]}, your Fit Smart subscription to the {subscription.meal_plan.name} plan "
                    f"has been resumed. Your next delivery is scheduled for {next_delivery_date}."
                )
                send_sms(current_user.phone, message)
            except Exception as e:
                app.logger.error(f"Failed to send resume subscription SMS: {str(e)}")
        
        flash('Your subscription has been resumed. Next delivery is scheduled.', 'success')
    except Exception as e:
        app.logger.error(f"Error resuming subscription {subscription_id}: {str(e)}")
        db.session.rollback()
        flash('Error resuming subscription. Please try again or contact support.', 'error')
    
    return redirect(url_for('profile'))

@app.route('/subscription/cancel/<int:subscription_id>', methods=['POST'])
@login_required
def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        
        # Verify that the subscription belongs to the current user
        if subscription.user_id != current_user.id:
            flash('You do not have permission to manage this subscription', 'error')
            return redirect(url_for('profile'))
        
        # Only active or paused subscriptions can be canceled
        if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.PAUSED]:
            flash('This subscription cannot be canceled', 'error')
            return redirect(url_for('profile'))
        
        # Cancel the subscription
        subscription.cancel()
        db.session.commit()
        
        # Send an SMS notification if the user has a phone number
        if current_user.phone:
            try:
                message = (
                    f"Hi {current_user.username.split()[0]}, your Fit Smart subscription to the {subscription.meal_plan.name} plan "
                    f"has been canceled. We hope to see you again soon! If you change your mind, "
                    f"you can always sign up for a new meal plan at healthyrizz.ca/meal-plans."
                )
                send_sms(current_user.phone, message)
            except Exception as e:
                app.logger.error(f"Failed to send cancel subscription SMS: {str(e)}")
        
        flash('Your subscription has been canceled. We hope to see you again soon!', 'success')
    except Exception as e:
        app.logger.error(f"Error canceling subscription {subscription_id}: {str(e)}")
        db.session.rollback()
        flash('Error canceling subscription. Please try again or contact support.', 'error')
    
    return redirect(url_for('profile'))

@app.route('/subscription/skip-delivery/<int:subscription_id>', methods=['POST'])
@login_required
def skip_delivery(subscription_id):
    """Skip a delivery for a specific date"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        
        # Verify that the subscription belongs to the current user
        if subscription.user_id != current_user.id:
            flash('You do not have permission to manage this subscription', 'error')
            return redirect(url_for('profile'))
        
        # Only active subscriptions can skip deliveries
        if subscription.status != SubscriptionStatus.ACTIVE:
            flash('Only active subscriptions can skip deliveries', 'error')
            return redirect(url_for('profile'))
        
        # Get the delivery date from the form
        delivery_date = request.form.get('delivery_date')
        if not delivery_date:
            flash('Delivery date is required', 'error')
            return redirect(url_for('profile'))
        
        # Skip the delivery
        success, message = subscription.skip_delivery(delivery_date)
        
        if success:
            # Send an SMS notification if the user has a phone number
            if current_user.phone:
                try:
                    formatted_date = datetime.strptime(delivery_date, '%Y-%m-%d').strftime('%A, %B %d')
                    message = (
                        f"Hi {current_user.username.split()[0]}, your Fit Smart meal delivery for {formatted_date} "
                        f"has been skipped as requested. You can manage your deliveries anytime from your profile."
                    )
                    send_sms(current_user.phone, message)
                except Exception as e:
                    app.logger.error(f"Failed to send skip delivery SMS: {str(e)}")
        
        flash(message, 'success' if success else 'error')
    except Exception as e:
        app.logger.error(f"Error skipping delivery for subscription {subscription_id}: {str(e)}")
        db.session.rollback()
        flash('Error skipping delivery. Please try again or contact support.', 'error')
    
    return redirect(url_for('profile'))

@app.route('/subscription/unskip-delivery/<int:subscription_id>', methods=['POST'])
@login_required
def unskip_delivery(subscription_id):
    """Cancel a previously skipped delivery"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        
        # Verify that the subscription belongs to the current user
        if subscription.user_id != current_user.id:
            flash('You do not have permission to manage this subscription', 'error')
            return redirect(url_for('profile'))
        
        # Only active subscriptions can unskip deliveries
        if subscription.status != SubscriptionStatus.ACTIVE:
            flash('Only active subscriptions can manage deliveries', 'error')
            return redirect(url_for('profile'))
        
        # Get the delivery date from the form
        delivery_date = request.form.get('delivery_date')
        if not delivery_date:
            flash('Delivery date is required', 'error')
            return redirect(url_for('profile'))
        
        # Unskip the delivery
        success, message = subscription.unskip_delivery(delivery_date)
        
        if success:
            # Send an SMS notification if the user has a phone number
            if current_user.phone:
                try:
                    formatted_date = datetime.strptime(delivery_date, '%Y-%m-%d').strftime('%A, %B %d')
                    message = (
                        f"Hi {current_user.username.split()[0]}, your Fit Smart meal delivery for {formatted_date} "
                        f"has been restored. Your meal will be delivered as originally scheduled."
                    )
                    send_sms(current_user.phone, message)
                except Exception as e:
                    app.logger.error(f"Failed to send unskip delivery SMS: {str(e)}")
        
        flash(message, 'success' if success else 'error')
    except Exception as e:
        app.logger.error(f"Error unskipping delivery for subscription {subscription_id}: {str(e)}")
        db.session.rollback()
        flash('Error restoring delivery. Please try again or contact support.', 'error')
    
    return redirect(url_for('profile'))

@app.route('/admin/send-delivery-notification/<int:subscription_id>', methods=['POST'])
@admin_required
def send_delivery_notification_admin(subscription_id):
    """Send delivery notification to a user (admin function)"""
    subscription = Subscription.query.get_or_404(subscription_id)
    
    # Only active subscriptions can receive delivery notifications
    if subscription.status != SubscriptionStatus.ACTIVE:
        flash('Only active subscriptions can receive delivery notifications', 'error')
        return redirect(url_for('admin.admin_view_subscription', id=subscription_id))
    
    # Get the user
    user = User.query.get(subscription.user_id)
    if not user or not user.phone:
        flash('User does not have a valid phone number', 'error')
        return redirect(url_for('admin.admin_view_subscription', id=subscription_id))
    
    # Get estimated delivery time from form or generate a default time window
    estimated_time = request.form.get('estimated_time', '')
    if not estimated_time:
        # Generate a default time window for the current day
        now = datetime.now()
        start_hour = now.hour + 1 if now.hour < 23 else now.hour
        end_hour = start_hour + 1 if start_hour < 23 else 23
        estimated_time = f"between {start_hour}:00 and {end_hour}:00 today"
    
    # Generate a random order number if not provided
    order_number = request.form.get('order_number', '')
    if not order_number:
        order_number = f"FS-{subscription.id}-{int(datetime.now().timestamp())}"
    
    # Send the delivery notification
    try:
        send_delivery_notification(
            customer_name=user.name.split()[0],  # First name
            phone_number=user.phone,
            meal_plan_name=subscription.meal_plan.name,
            delivery_time_range=estimated_time
        )
        
        flash('Delivery notification sent successfully', 'success')
        app.logger.info(f"Delivery notification sent to {user.phone}")
    except Exception as e:
        flash(f'Failed to send delivery notification: {str(e)}', 'error')
        app.logger.error(f"Failed to send delivery notification: {str(e)}")
    
    return redirect(url_for('admin.admin_view_subscription', id=subscription_id))

def generate_password_reset_token(user, expires_sec=3600):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return s.dumps(user.email, salt='password-reset-salt')

def verify_password_reset_token(token, expires_sec=3600):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
    except Exception:
        return None
    return email

def send_password_reset_email(to_email, token):
    reset_url = url_for('reset_password', token=token, _external=True)
    msg = Message(
        subject="Password Reset Request - HealthyRizz",
        sender=app.config.get("MAIL_DEFAULT_SENDER", "noreply@healthyrizz.ca"),
        recipients=[to_email]
    )
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email.
'''
    with app.app_context():
        mail.send(msg)

@app.route('/admin/blog/add', methods=['GET', 'POST'])
@admin_required
def admin_add_blog_post():
    """Add new blog post"""
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            content = request.form.get('content')
            category = request.form.get('category')
            tags = request.form.get('tags')
            is_published = request.form.get('is_published') == 'on'
            is_featured = request.form.get('is_featured') == 'on'
            
            app.logger.info(f"Creating new blog post with title: {title}")
            
            # Validate required fields
            if not all([title, content, category]):
                flash('Title, content and category are required', 'error')
                return redirect(url_for('admin_add_blog_post'))
            
            # Check for duplicate title
            existing_post = BlogPost.query.filter_by(title=title).first()
            if existing_post:
                flash('A post with this title already exists', 'error')
                return redirect(url_for('admin_add_blog_post'))
            
            # Create slug from title
            slug = title.lower().replace(' ', '-')
            
            # Get admin user
            admin = User.query.filter_by(email='admin@healthyrizz.com').first()
            if not admin:
                flash('Admin user not found', 'error')
                return redirect(url_for('admin_add_blog_post'))
            
            # Create new post
            post = BlogPost(
                title=title,
                slug=slug,
                content=content,
                category=category,
                tags=tags,
                author_id=admin.id,
                is_published=is_published,
                summary=content[:200] + '...' if len(content) > 200 else content,
                created_at=datetime.now(),
                published_date=datetime.now() if is_published else None
            )
            
            # Set featured status after creation
            post.is_featured = is_featured
            
            # Handle featured image upload
            if 'featured_image' in request.files:
                file = request.files['featured_image']
                if file and file.filename:
                    try:
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'blog', filename)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        file.save(file_path)
                        post.featured_image = f'blog/{filename}'
                        app.logger.info(f"Saved featured image: {file_path}")
                    except Exception as e:
                        app.logger.error(f"Error saving featured image: {str(e)}")
                        flash('Error saving featured image', 'error')
            
            # Save to database
            db.session.add(post)
            db.session.commit()
            
            app.logger.info(f"Successfully created blog post with ID: {post.id}")
            flash('Blog post created successfully', 'success')
            return redirect(url_for('admin_blog'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating blog post: {str(e)}")
            flash(f'Error creating blog post: {str(e)}', 'error')
            return redirect(url_for('admin_add_blog_post'))
    
    return render_template('admin/add_blog_post.html')

@app.route('/admin/blog/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete_blog_post(id):
    """Delete a blog post"""
    try:
        post = BlogPost.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Blog post deleted successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting blog post: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/blog/edit/<int:id>', methods=['GET', 'POST'])
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
                    return redirect(url_for('admin_edit_blog_post', id=id))
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
            return redirect(url_for('admin_blog'))
        
        # Define available categories
        categories = [
            'Nutrition',
            'Fitness',
            'Wellness',
            'Recipes',
            'Lifestyle',
            'News'
        ]
        
        return render_template('admin/edit_blog_post.html', post=post, categories=categories)
    except Exception as e:
        app.logger.error(f"Error editing blog post: {str(e)}")
        flash('Error editing blog post', 'error')
        return redirect(url_for('admin_blog'))

# Add admin dashboard route
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics and overview"""
    try:
        # Get user statistics
        total_users = User.query.count()
        new_users = User.query.filter(
            User.created_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Get subscription statistics
        active_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).count()
        trial_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).count()  # All active are considered trials for now
        
        # Get meal plan statistics
        total_meal_plans = MealPlan.query.count()
        active_meal_plans = MealPlan.query.filter_by(is_active=True).count()
        
        # Get location statistics
        total_locations = DeliveryLocation.query.count()
        active_locations = DeliveryLocation.query.filter_by(is_active=True).count()
        
        # Get recent activity (last 10 subscriptions)
        recent_subscriptions = Subscription.query.order_by(
            Subscription.created_at.desc()
        ).limit(10).all()
        
        recent_activity = []
        for sub in recent_subscriptions:
            recent_activity.append({
                'type': 'subscription',
                'details': f"New {sub.frequency.value} subscription to {sub.meal_plan.name} by {sub.user.username}",
                'created_at': sub.created_at
            })
        
        # Add some recent user registrations
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        for user in recent_users:
            recent_activity.append({
                'type': 'user',
                'details': f"New user registration: {user.username} ({user.email})",
                'created_at': user.created_at
            })
        
        # Sort by creation date
        recent_activity.sort(key=lambda x: x['created_at'], reverse=True)
        recent_activity = recent_activity[:10]  # Keep only 10 most recent
        
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
        app.logger.error(f"Error loading admin dashboard: {str(e)}")
        flash('Error loading dashboard data', 'error')
        return render_template('admin/dashboard.html',
                              total_users=0,
                              new_users=0,
                              active_subscriptions=0,
                              trial_subscriptions=0,
                              total_meal_plans=0,
                              active_meal_plans=0,
                              total_locations=0,
                              active_locations=0,
                              recent_activity=[])

@app.route('/admin/blog/test')
@admin_required
def create_test_post():
    """Create a test blog post"""
    try:
        # Get admin user
        admin = User.query.filter_by(email='admin@healthyrizz.com').first()
        if not admin:
            flash('Admin user not found', 'error')
            return redirect(url_for('admin_blog'))
        
        app.logger.info(f"Creating test post with admin ID: {admin.id}")
        
        # Create test post
        post = BlogPost(
            title='Test Blog Post',
            slug='test-blog-post',
            content='This is a test blog post content.',
            category='Test',
            tags='test,blog',
            author_id=admin.id,
            is_published=True,
            summary='This is a test blog post.',
            created_at=datetime.now(),
            published_date=datetime.now()
        )
        
        db.session.add(post)
        db.session.flush()  # Flush to get the ID
        app.logger.info(f"Created test post with ID: {post.id}")
        
        db.session.commit()
        app.logger.info("Successfully committed test post")
        
        # Verify post was created
        created_post = BlogPost.query.get(post.id)
        if created_post:
            app.logger.info(f"Verified post exists: {created_post.title} (ID: {created_post.id})")
        else:
            app.logger.error("Post was not found after creation!")
        
        flash('Test blog post created successfully', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating test post: {str(e)}")
        flash(f'Error creating test post: {str(e)}', 'error')
    
    return redirect(url_for('admin_blog'))

@app.route('/admin/media')
@admin_required
def admin_media():
    """Media management dashboard"""
    hero_slides = HeroSlide.query.order_by(HeroSlide.order, HeroSlide.created_at).all()
    videos = Video.query.order_by(Video.order, Video.created_at).all()
    team_members = TeamMember.query.order_by(TeamMember.order, TeamMember.created_at).all()
    site_settings = SiteSetting.query.all()
    
    return render_template('admin/media.html', 
                         hero_slides=hero_slides,
                         videos=videos,
                         team_members=team_members,
                         site_settings=site_settings)

# HERO SLIDES MANAGEMENT
@app.route('/admin/media/hero-slides/add', methods=['GET', 'POST'])
@admin_required
def admin_add_hero_slide():
    if request.method == 'POST':
        try:
            slide = HeroSlide(
                title=request.form.get('title'),
                subtitle=request.form.get('subtitle'),
                image_url=request.form.get('image_url'),
                order=int(request.form.get('order', 0)),
                is_active=bool(request.form.get('is_active'))
            )
            
            db.session.add(slide)
            db.session.commit()
            
            flash('Hero slide added successfully!', 'success')
            return redirect(url_for('admin_media'))
            
        except Exception as e:
            app.logger.error(f"Error adding hero slide: {str(e)}")
            db.session.rollback()
            flash('Error adding hero slide. Please try again.', 'error')
    
    return render_template('admin/add_hero_slide.html')

@app.route('/admin/media/hero-slides/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_hero_slide(id):
    slide = HeroSlide.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            slide.title = request.form.get('title')
            slide.subtitle = request.form.get('subtitle')
            slide.image_url = request.form.get('image_url')
            slide.order = int(request.form.get('order', 0))
            slide.is_active = bool(request.form.get('is_active'))
            
            db.session.commit()
            
            flash('Hero slide updated successfully!', 'success')
            return redirect(url_for('admin_media'))
            
        except Exception as e:
            app.logger.error(f"Error updating hero slide: {str(e)}")
            db.session.rollback()
            flash('Error updating hero slide. Please try again.', 'error')
    
    return render_template('admin/edit_hero_slide.html', slide=slide)

@app.route('/admin/media/hero-slides/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete_hero_slide(id):
    try:
        slide = HeroSlide.query.get_or_404(id)
        db.session.delete(slide)
        db.session.commit()
        
        flash('Hero slide deleted successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting hero slide: {str(e)}")
        db.session.rollback()
        flash('Error deleting hero slide. Please try again.', 'error')
    
    return redirect(url_for('admin_media'))

# VIDEOS MANAGEMENT
@app.route('/admin/media/videos/add', methods=['GET', 'POST'])
@admin_required
def admin_add_video():
    if request.method == 'POST':
        try:
            video = Video(
                title=request.form.get('title'),
                description=request.form.get('description'),
                video_type=request.form.get('video_type', 'youtube'),
                video_url=request.form.get('video_url'),
                thumbnail_url=request.form.get('thumbnail_url'),
                order=int(request.form.get('order', 0)),
                is_active=bool(request.form.get('is_active'))
            )
            
            db.session.add(video)
            db.session.commit()
            
            flash('Video added successfully!', 'success')
            return redirect(url_for('admin_media'))
            
        except Exception as e:
            app.logger.error(f"Error adding video: {str(e)}")
            db.session.rollback()
            flash('Error adding video. Please try again.', 'error')
    
    return render_template('admin/add_video.html')

@app.route('/admin/media/videos/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_video(id):
    video = Video.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            video.title = request.form.get('title')
            video.description = request.form.get('description')
            video.video_type = request.form.get('video_type', 'youtube')
            video.video_url = request.form.get('video_url')
            video.thumbnail_url = request.form.get('thumbnail_url')
            video.order = int(request.form.get('order', 0))
            video.is_active = bool(request.form.get('is_active'))
            
            db.session.commit()
            
            flash('Video updated successfully!', 'success')
            return redirect(url_for('admin_media'))
            
        except Exception as e:
            app.logger.error(f"Error updating video: {str(e)}")
            db.session.rollback()
            flash('Error updating video. Please try again.', 'error')
    
    return render_template('admin/edit_video.html', video=video)

@app.route('/admin/media/videos/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete_video(id):
    try:
        video = Video.query.get_or_404(id)
        db.session.delete(video)
        db.session.commit()
        
        flash('Video deleted successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting video: {str(e)}")
        db.session.rollback()
        flash('Error deleting video. Please try again.', 'error')
    
    return redirect(url_for('admin_media'))

# TEAM MEMBERS MANAGEMENT
@app.route('/admin/media/team/add', methods=['GET', 'POST'])
@admin_required
def admin_add_team_member():
    if request.method == 'POST':
        try:
            member = TeamMember(
                name=request.form.get('name'),
                role=request.form.get('role'),
                image_url=request.form.get('image_url'),
                bio=request.form.get('bio'),
                order=int(request.form.get('order', 0)),
                is_active=bool(request.form.get('is_active'))
            )
            
            db.session.add(member)
            db.session.commit()
            
            flash('Team member added successfully!', 'success')
            return redirect(url_for('admin_media'))
            
        except Exception as e:
            app.logger.error(f"Error adding team member: {str(e)}")
            db.session.rollback()
            flash('Error adding team member. Please try again.', 'error')
    
    return render_template('admin/add_team_member.html')

@app.route('/admin/media/team/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_team_member(id):
    member = TeamMember.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            member.name = request.form.get('name')
            member.role = request.form.get('role')
            member.image_url = request.form.get('image_url')
            member.bio = request.form.get('bio')
            member.order = int(request.form.get('order', 0))
            member.is_active = bool(request.form.get('is_active'))
            
            db.session.commit()
            
            flash('Team member updated successfully!', 'success')
            return redirect(url_for('admin_media'))
            
        except Exception as e:
            app.logger.error(f"Error updating team member: {str(e)}")
            db.session.rollback()
            flash('Error updating team member. Please try again.', 'error')
    
    return render_template('admin/edit_team_member.html', member=member)

@app.route('/admin/media/team/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete_team_member(id):
    try:
        member = TeamMember.query.get_or_404(id)
        db.session.delete(member)
        db.session.commit()
        
        flash('Team member deleted successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting team member: {str(e)}")
        db.session.rollback()
        flash('Error deleting team member. Please try again.', 'error')
    
    return redirect(url_for('admin_media'))

# SITE SETTINGS MANAGEMENT
@app.route('/admin/media/settings/update', methods=['POST'])
@admin_required
def admin_update_site_settings():
    try:
        settings_to_update = [
            'site_logo',
            'hero_subtitle',
            'company_name',
            'company_tagline'
        ]
        
        for key in settings_to_update:
            value = request.form.get(key)
            if value is not None:
                setting = SiteSetting.query.filter_by(key=key).first()
                if setting:
                    setting.value = value
                    setting.updated_at = datetime.utcnow()
                else:
                    setting = SiteSetting(key=key, value=value)
                    db.session.add(setting)
        
        db.session.commit()
        flash('Site settings updated successfully!', 'success')
        
    except Exception as e:
        app.logger.error(f"Error updating site settings: {str(e)}")
        db.session.rollback()
        flash('Error updating site settings. Please try again.', 'error')
    
    return redirect(url_for('admin_media'))

@app.route('/test')
def test():
    return "Hello, Flask is working!"

@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin users management page"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return render_template('admin/users.html', users=users)
    except Exception as e:
        app.logger.error(f"Error loading users: {str(e)}")
        flash('Error loading users', 'error')
        return render_template('admin/users.html', users=[])

@app.route('/admin/subscriptions')
@admin_required
def admin_subscriptions():
    """Admin subscriptions management page"""
    try:
        subscriptions = Subscription.query.order_by(Subscription.created_at.desc()).all()
        return render_template('admin/subscriptions.html', subscriptions=subscriptions)
    except Exception as e:
        app.logger.error(f"Error loading subscriptions: {str(e)}")
        flash('Error loading subscriptions', 'error')
        return render_template('admin/subscriptions.html', subscriptions=[])

@app.route('/admin/meal-plans')
@admin_required
def admin_meal_plans():
    """Admin meal plans management page"""
    try:
        meal_plans = MealPlan.query.order_by(MealPlan.name).all()
        return render_template('admin/meal_plans.html', meal_plans=meal_plans)
    except Exception as e:
        app.logger.error(f"Error loading meal plans: {str(e)}")
        flash('Error loading meal plans', 'error')
        return render_template('admin/meal_plans.html', meal_plans=[])

@app.route('/admin/location-tree')
@admin_required
def admin_location_tree():
    """Admin location management page"""
    try:
        locations = DeliveryLocation.query.order_by(DeliveryLocation.city).all()
        return render_template('admin/location_tree.html', locations=locations)
    except Exception as e:
        app.logger.error(f"Error loading locations: {str(e)}")
        flash('Error loading locations', 'error')
        return render_template('admin/location_tree.html', locations=[])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

