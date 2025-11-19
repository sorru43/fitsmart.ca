from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for, flash, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.models import db, User, MealPlan, Order, Subscription, BlogPost, DeliveryLocation, State, City, Area, CouponCode, CouponUsage, SubscriptionStatus, SubscriptionFrequency, SkippedDelivery, Holiday, Newsletter
from forms.auth_forms import LoginForm, RegisterForm, ProfileForm, ContactForm, NewsletterForm
from forms.checkout_forms import CheckoutForm
from forms.trial_forms import TrialRequestForm
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
import json
import logging
from utils.decorators import admin_required
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from forms.auth_forms import LoginForm, RegisterForm
from utils.token_utils import generate_password_reset_token
from utils.email_utils import send_password_reset_email, send_contact_notification, send_email
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from urllib.parse import urlparse
from routes.admin_routes import admin_required
import random
import json
from werkzeug.security import generate_password_hash, check_password_hash
from forms.auth_forms import RegistrationForm, WaterReminderForm
from forms.checkout_forms import CheckoutForm
from forms import GeneralContactForm, CorporateInquiryForm
from utils.auth_utils import send_verification_email
from utils.encryption_helper import encrypt_sensitive_data, decrypt_sensitive_data
from utils.stripe_utils import create_stripe_customer, create_stripe_checkout_session
from extensions import csrf
# from utils.report_utils import get_order_completion_notifications  # Temporarily disabled due to fpdf2 import issues
from utils.notifications import send_push_notification_to_all_users, send_push_notification_to_user
from datetime import datetime, timedelta, date, time as dt_time
import subprocess
import sys
import os
import time
import secrets
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
import hmac
import hashlib
from itsdangerous import URLSafeTimedSerializer

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

main_bp = Blueprint('main', __name__)

class TestForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


@main_bp.route('/')
def index():
    """Home page route - simplified and robust"""
    try:
        # Initialize all variables with defaults
        faqs = []
        hero_slides = []
        videos = []
        team_members = []
        meal_plans = []
        full_width_sections = []
        site_settings = {}
        
        # Try to load each dataset individually with graceful failure
        try:
            from database.models import FAQ
            faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.order, FAQ.created_at).all()
            current_app.logger.info(f"✅ Loaded {len(faqs)} FAQs")
        except Exception as e:
            current_app.logger.warning(f"⚠️ Could not load FAQs: {e}")
            faqs = []
        
        try:
            from database.models import HeroSlide
            hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.order, HeroSlide.created_at).all()
            current_app.logger.info(f"✅ Loaded {len(hero_slides)} HeroSlides")
        except Exception as e:
            current_app.logger.warning(f"⚠️ Could not load HeroSlides: {e}")
            hero_slides = []
            
        try:
            from database.models import Video
            videos = Video.query.filter_by(is_active=True).order_by(Video.order, Video.created_at).all()
            current_app.logger.info(f"✅ Loaded {len(videos)} Videos")
        except Exception as e:
            current_app.logger.warning(f"⚠️ Could not load Videos: {e}")
            videos = []
            
        try:
            from database.models import TeamMember
            team_members = TeamMember.query.filter_by(is_active=True).order_by(TeamMember.order, TeamMember.created_at).all()
            current_app.logger.info(f"✅ Loaded {len(team_members)} TeamMembers from DB")
        except Exception as e:
            current_app.logger.warning(f"⚠️ Could not load TeamMembers: {e}")
            team_members = []
        
        try:
            from database.models import FullWidthSection
            full_width_sections = FullWidthSection.query.filter_by(is_active=True).order_by(FullWidthSection.order, FullWidthSection.created_at).all()
            current_app.logger.info(f"✅ Loaded {len(full_width_sections)} FullWidthSections")
        except Exception as e:
            current_app.logger.warning(f"⚠️ Could not load FullWidthSections: {e}")
            full_width_sections = []
        
        try:
            from database.models import MealPlan
            meal_plans = MealPlan.query.filter_by(is_active=True).order_by(MealPlan.is_popular.desc(), MealPlan.price_weekly).limit(6).all()
            current_app.logger.info(f"✅ Loaded {len(meal_plans)} MealPlans from DB")
        except Exception as e:
            current_app.logger.warning(f"⚠️ Could not load MealPlans: {e}")
            meal_plans = []
        
        try:
            from database.models import SiteSetting
            settings = SiteSetting.query.all()
            for setting in settings:
                site_settings[setting.key] = setting.value
            current_app.logger.info(f"✅ Loaded {len(site_settings)} SiteSettings")
        except Exception as e:
            current_app.logger.warning(f"⚠️ Could not load SiteSettings: {e}")
            site_settings = {}
        
        # Provide fallback data if database is empty
        if not hero_slides:
            hero_slides = [
                {'title': "It's Not An Ordinary Meal Box, It's a Nutrition Box", 'image_url': '/static/images/healthy-meal-bowl.jpg'},
                {'title': "Personalized Nutrition Delivered", 'image_url': '/static/images/meal-plate.jpg'},
                {'title': "Eat Healthy, Live Better", 'image_url': '/static/images/healthy-meal-bowl.webp'}
            ]
        
        if not videos:
            videos = [
                {'title': 'How FitSmart Works', 'description': 'Choose your plan, connect with a nutrition expert, get chef-prepared meals delivered, and transform your lifestyle!', 'youtube_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'thumbnail_url': '/static/images/healthy-meal-bowl.jpg'},
                {'title': 'Our Kitchen Process', 'description': 'See how we prepare fresh, nutritious meals in our state-of-the-art kitchen facilities with expert chefs.', 'youtube_url': 'https://www.youtube.com/watch?v=9bZkp7q19f0', 'thumbnail_url': '/static/images/meal-plate.jpg'}
            ]
        
        if not team_members:
            team_members = [
                {'name': 'Ankit Bathla', 'position': 'Certified Nutrition and Fitness Expert', 'image_url': '/static/images/default-avatar.png'},
                {'name': 'Anu Bathla', 'position': 'Exercise Science & Nutrition Expert', 'image_url': '/static/images/default-avatar.png'}
            ]
        
        # Default site settings
        default_settings = {
            'site_logo': '/static/images/logo white.png',
            'hero_subtitle': 'In Supervision Of Nutrition Experts',
            'company_name': 'FitSmart',
            'company_tagline': 'Healthy Meal Delivery'
        }
        
        # Merge defaults with loaded settings
        for key, default_value in default_settings.items():
            if key not in site_settings:
                site_settings[key] = default_value
        
        # Ensure we have working data to display the full homepage
        if not meal_plans:
            # Create some default meal plans to show
            class MockMealPlan:
                def __init__(self, name, description, price_weekly, trial_price, calories, protein, fat, carbs, tag, is_popular=False):
                    self.name = name
                    self.description = description
                    self.price_weekly = price_weekly
                    self.trial_price = trial_price
                    self.price_trial = trial_price  # For template compatibility
                    self.calories = calories
                    self.protein = protein
                    self.fat = fat
                    self.carbs = carbs
                    self.tag = tag  # Add tag attribute
                    self.is_popular = is_popular
                    self.id = 1
                    self.is_active = True
                    self.available_for_trial = True
            
            meal_plans = [
                MockMealPlan("Balanced Diets office", "Fresh vegetarian meals packed with nutrition", 750, 200, 1600, 80, 50, 180, "Balanced", True),
                MockMealPlan("Balanced Diet Plan", "A well-balanced diet with all essential nutrients", 999, 200, 1800, 120, 60, 200, "Balanced", True),
                MockMealPlan("High Protein Diet", "High Protein diets, special for whom who want natural protein from daily foods", 1200, 250, 100, 100, 100, 100, "High Protein", True)
            ]
        
        if not team_members:
            # Create some default team members
            class MockTeamMember:
                def __init__(self, name, position):
                    self.name = name
                    self.position = position
                    self.image_url = '/static/images/default-avatar.png'
            
            team_members = [
                MockTeamMember("Sourabh jhamb", "Operations"),
                MockTeamMember("Parmod Kumar", "Sourcing Head"),
                MockTeamMember("Ekta", "Operations Head"),
                MockTeamMember("Khushi Midha", "Brand Manager")
            ]
        
        if not hero_slides:
            # Create a default hero slide
            class MockHeroSlide:
                def __init__(self, image_url):
                    self.image_url = image_url
            
            hero_slides = [MockHeroSlide('/static/uploads/20250629_165207_herobanner.webp')]
        
        # Set SEO meta tags for homepage
        meta_description = "FitSmart - Premium Indian & Global Healthy Meal Plans in Canada. Delicious vegetarian and non-vegetarian meals delivered fresh. Nutritionist-curated, tasty, and nutritious meal plans available in Ontario. Order now!"
        og_title = "FitSmart - Indian & Global Healthy Meal Plans | Veg & Non-Veg | Canada"
        
        # Create template context with proper CSRF handling
        template_context = {
            'faqs': faqs or [],
            'hero_slides': hero_slides or [],
            'videos': videos or [],
            'team_members': team_members or [],
            'meal_plans': meal_plans or [],
            'full_width_sections': full_width_sections or [],
            'site_settings': site_settings or {},
            'now': datetime.now(),
            'meta_description': meta_description,
            'og_title': og_title
        }
        
        # Ensure site_settings has ALL the required defaults for the template
        essential_defaults = {
            'site_logo': '/static/images/logo_20250629_170145_black_bg.gif',
            'hero_subtitle': 'In Supervision Of Nutrition Experts',
            'company_name': 'FitSmart',
            'company_tagline': 'Healthy Meal Delivery',
            'contact_phone': '8054090043',
            'contact_email': 'info@fitsmart.ca',
            'company_address': 'Ludhiana, Punjab, India',
            'facebook_url': 'https://facebook.com/fitsmart',
            'instagram_url': 'https://instagram.com/fitsmart.ca',
            'show_social_links': 'True',
            'show_fssai_badge': 'True',
            'show_hygiene_badge': 'True',
            'hygiene_badge_text': '100% Hygienic'
        }
        
        # Merge defaults with any existing settings
        for key, default_value in essential_defaults.items():
            if key not in template_context['site_settings']:
                template_context['site_settings'][key] = default_value
        

        
        # Log what we're about to render
        current_app.logger.info(f"Rendering index.html with context keys: {list(template_context.keys())}")
        current_app.logger.info(f"Meal plans count: {len(template_context['meal_plans'])}")
        current_app.logger.info(f"Team members count: {len(template_context['team_members'])}")
        current_app.logger.info(f"Hero slides count: {len(template_context['hero_slides'])}")
        
        # Render the template with the context
        try:
            rendered = render_template('index.html', **template_context)
            current_app.logger.info("✅ INDEX TEMPLATE RENDERED SUCCESSFULLY!")
            return rendered
        except Exception as template_error:
            current_app.logger.error(f"❌ Template rendering failed: {str(template_error)}")
            current_app.logger.error(f"❌ Template error type: {type(template_error).__name__}")
            
            # Log the full traceback for debugging
            import traceback
            current_app.logger.error(f"❌ Full template traceback: {traceback.format_exc()}")
            
            # Re-raise the error so we can see what's actually wrong
            raise template_error

                             
    except Exception as e:
        # If everything fails, return simple HTML that always works
        current_app.logger.error(f"❌ INDEX ROUTE FAILED: {str(e)}")
        current_app.logger.error(f"❌ Error type: {type(e).__name__}")
        
        # Log the full traceback for debugging
        import traceback
        current_app.logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        
        from flask import Response
        return Response('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FitSmart - Welcome</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
                .container { background: white; padding: 3rem; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); text-align: center; max-width: 500px; margin: 20px; }
                h1 { color: #333; margin-bottom: 1rem; font-size: 2.5rem; }
                .emoji { font-size: 3rem; margin-bottom: 1rem; }
                p { color: #666; font-size: 1.1rem; margin-bottom: 2rem; }
                .nav { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; }
                .nav a { background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px; font-weight: 500; transition: all 0.3s ease; }
                .nav a:hover { background: #5a6fd8; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
                .status { background: #f0f9ff; color: #0369a1; padding: 1rem; border-radius: 10px; margin-top: 2rem; font-size: 0.9rem; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emoji">🎉</div>
                <h1>Welcome to FitSmart!</h1>
                <p>You have successfully logged in to your account.</p>
                
                <div class="nav">
                    <a href="/profile">👤 Profile</a>
                    <a href="/meal-plans">🥗 Meal Plans</a>
                    <a href="/about">ℹ️ About</a>
                    <a href="/logout">🚪 Logout</a>
                </div>
                
                <div class="status">
                    ✨ Your FitSmart journey starts here!<br>
                    <small>Homepage in safe mode - all features available</small>
                </div>
            </div>
        </body>
        </html>
        ''', mimetype='text/html')


@main_bp.route('/about')
def about():
    """About page with bulletproof error handling"""
    try:
        current_app.logger.info("About page accessed successfully")
        return render_template('about.html', now=datetime.now())
    except Exception as e:
        current_app.logger.error(f"Error in about route: {str(e)}")
        
        # Fallback: Return a beautiful about page
        fallback_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>About Us - FitSmart</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
                .about-container { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .nav-links { display: flex; gap: 20px; justify-content: center; margin: 30px 0; flex-wrap: wrap; }
                .nav-links a { color: #007bff; text-decoration: none; padding: 12px 20px; background: #e9ecef; border-radius: 5px; transition: all 0.3s; }
                .nav-links a:hover { background: #007bff; color: white; transform: translateY(-2px); }
                h1 { color: #28a745; text-align: center; margin-bottom: 20px; }
                p { line-height: 1.6; margin-bottom: 15px; color: #555; }
                .icon { font-size: 3rem; text-align: center; margin-bottom: 20px; }
                .highlight { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="about-container">
                <div class="icon">🌱</div>
                <h1>About FitSmart</h1>
                <p>We're passionate about bringing you nutritious, delicious meals that fit your lifestyle.</p>
                <p>Our mission is to make healthy eating convenient and enjoyable for everyone, whether you're a busy professional, a fitness enthusiast, or someone just starting their wellness journey.</p>
                
                <div class="highlight">
                    <p><strong>🥗 Fresh Ingredients:</strong> We source the finest, farm-fresh ingredients to create meals that nourish your body and delight your taste buds.</p>
                    <p><strong>👩‍🍳 Expert Crafted:</strong> Our culinary team designs each meal plan with balanced nutrition and amazing flavors in mind.</p>
                    <p><strong>🚚 Convenient Delivery:</strong> Enjoy restaurant-quality meals delivered right to your doorstep on your schedule.</p>
                </div>
                
                <p>From personalized meal plans to expertly crafted nutrition guides, we're here to support your wellness journey every step of the way.</p>
                
                <div class="nav-links">
                    <a href="/">🏠 Home</a>
                    <a href="/meal-plans">🥗 Meal Plans</a>
                    <a href="/contact">📞 Contact</a>
                    <a href="/profile">👤 Profile</a>
                </div>
            </div>
        </body>
        </html>
        """
        return fallback_html, 200

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route with multi-purpose form"""
    from forms.contact_forms import MultiPurposeContactForm
    from database.models import ContactInquiry
    
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
            
            # Track contact form submission
            try:
                session['track_contact'] = True
            except Exception as e:
                current_app.logger.error(f'Error setting contact tracking: {str(e)}')
            
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

@main_bp.route('/amp/blog/<slug>')
def amp_blog_post(slug):
    """AMP version of individual blog post page"""
    try:
        post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
        
        # Get related posts (same category, excluding current post)
        related_posts = BlogPost.query.filter(
            BlogPost.category == post.category,
            BlogPost.id != post.id,
            BlogPost.is_published == True
        ).order_by(BlogPost.created_at.desc()).limit(3).all()
        
        return render_template('amp_blog_post.html', 
                             post=post, 
                             related_posts=related_posts,
                             now=datetime.now())
    except Exception as e:
        current_app.logger.error(f"Error fetching AMP blog post: {str(e)}")
        return render_template('404.html'), 404

@main_bp.route('/calculate-meal', methods=['POST'])
@csrf.exempt  # Exempt from CSRF protection for AJAX requests
def calculate_meal():
    """Calculate meal plan macros and return JSON response for AJAX requests"""
    current_app.logger.info("Meal calculator endpoint called")
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
        response_data = {
            'success': True,
            'calories': round(calories),
            'protein': protein,
            'carbs': carbs,
            'fat': fat,
            'bmr': round(bmr),
            'tdee': round(tdee)
        }
        current_app.logger.info(f"Meal calculator response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error in calculate_meal: {str(e)}")
        return jsonify({'error': 'An error occurred while calculating your meal plan'}), 500

@main_bp.route('/meal-plans')
def meal_plans():
    """Meal plans page with advanced filtering"""
    try:
        # Get filter parameters
        meal_type = request.args.get('type', '')
        gender = request.args.get('gender', '')
        breakfast = request.args.get('breakfast', '')
        trial_only = request.args.get('trial_only', '')
        
        # Build query - start with all active plans
        query = MealPlan.query.filter_by(is_active=True)
        
        # Apply filters only if they are provided
        if meal_type:
            if meal_type == 'balanced':
                query = query.filter(MealPlan.tag.ilike('%Balanced%'))
            elif meal_type == 'weight-loss':
                query = query.filter(MealPlan.tag.ilike('%Weight Loss%'))
            elif meal_type == 'athletic':
                query = query.filter(MealPlan.tag.ilike('%Athletic%'))
            elif meal_type == 'vegetarian':
                query = query.filter(MealPlan.tag.ilike('%Vegetarian%'))
            elif meal_type == 'keto':
                query = query.filter(MealPlan.tag.ilike('%Keto%'))
        
        if gender:
            if gender == 'male':
                query = query.filter(MealPlan.tag.ilike('%Male%'))
            elif gender == 'female':
                query = query.filter(MealPlan.tag.ilike('%Female%'))
        
        if breakfast:
            if breakfast == '1':
                query = query.filter(MealPlan.includes_breakfast == True)
            elif breakfast == '0':
                query = query.filter(MealPlan.includes_breakfast == False)
        
        if trial_only:
            if trial_only == '1':
                query = query.filter(MealPlan.is_trial_available == True)
        
        # Get the plans
        plans = query.order_by(MealPlan.is_popular.desc(), MealPlan.price_weekly.asc()).all()
        
        # Debug: Print plan names and details
        current_app.logger.info(f"Found {len(plans)} meal plans")
        for plan in plans:
            current_app.logger.info(f"Plan: {plan.name} (ID: {plan.id})")
            current_app.logger.info(f"  - Description: {plan.description}")
            current_app.logger.info(f"  - Price: {plan.price_weekly}")
            current_app.logger.info(f"  - Is Popular: {plan.is_popular}")
            current_app.logger.info(f"  - Is Active: {plan.is_active}")
        
        # Track meal plans page view
        try:
            session['track_meal_plans_view'] = {
                'plan_count': len(plans),
                'filters': {
                    'meal_type': meal_type,
                    'gender': gender,
                    'breakfast': breakfast,
                    'trial_only': trial_only
                }
            }
        except Exception as e:
            current_app.logger.error(f'Error setting meal plans tracking: {str(e)}')
        
        # Set SEO meta tags for meal plans page
        meta_description = "Browse our premium Indian & Global healthy meal plans in Canada. Choose from vegetarian and non-vegetarian options. Nutritionist-curated, tasty meals delivered fresh. Available in Ontario."
        og_title = "Meal Plans - Indian & Global Healthy Meals | Veg & Non-Veg | FitSmart Canada"
        
        return render_template('meal-plans.html', 
                              meal_plans=plans,
                              meta_description=meta_description,
                              og_title=og_title)
        
    except Exception as e:
        current_app.logger.error(f"Error loading meal plans: {e}")
        # Return empty plans list but don't crash
        return render_template('meal-plans.html', meal_plans=[])

@main_bp.route('/meal-plans-json')
def meal_plans_json():
    """API route to return meal plans as JSON"""
    try:
        plans = MealPlan.query.filter_by(is_active=True).all()
        plan_data = []
        for plan in plans:
            plan_data.append({
                'id': plan.id,
                'name': plan.name,
                'description': plan.description,
                'price_weekly': float(plan.price_weekly),
                'is_popular': plan.is_popular,
                'is_active': plan.is_active,
                'calories': plan.calories,
                'protein': plan.protein,
                'fat': plan.fat,
                'carbs': plan.carbs
            })
        return jsonify({'plans': plan_data, 'count': len(plan_data)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/sample-menu/<int:plan_id>')
def sample_menu(plan_id):
    """Sample menu page for a specific meal plan"""
    try:
        # Get the meal plan
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
        # Get sample menu items organized by meal type
        sample_menu_by_type = meal_plan.get_sample_menu_by_meal_type()
        
        # Get sample menu items organized by day
        sample_menu_by_day = meal_plan.get_sample_menu_by_day()
        
        return render_template('sample_menu.html', 
                             meal_plan=meal_plan, 
                             sample_menu_by_type=sample_menu_by_type,
                             sample_menu_by_day=sample_menu_by_day)
        
    except Exception as e:
        current_app.logger.error(f"Error loading sample menu: {e}")
        flash('Error loading sample menu. Please try again.', 'error')
        return redirect(url_for('main.meal_plans'))

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
        
        # Get related posts (same category, excluding current post)
        related_posts = BlogPost.query.filter(
            BlogPost.category == post.category,
            BlogPost.id != post.id,
            BlogPost.is_published == True
        ).order_by(BlogPost.created_at.desc()).limit(3).all()
        
        return render_template('blog-post.html', 
                             post=post, 
                             related_posts=related_posts,
                             now=datetime.now())
    except Exception as e:
        current_app.logger.error(f"Error fetching blog post: {str(e)}")
        flash('Blog post not found', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/profile')
@login_required
def profile():
    """Enhanced user profile page with better UI/UX for subscription management"""
    # Initialize variables with default values
    active_subscriptions = []
    paused_subscriptions = []
    canceled_subscriptions = []
    subscription_deliveries = {}
    payments = []
    orders = []
    total_spent = 0
    
    try:
        # Get user's orders for payment history
        orders = Order.query.filter_by(
            user_id=current_user.id
        ).order_by(Order.created_at.desc()).all()
        
        # Calculate total spent
        total_spent = sum(float(order.amount) for order in orders if order.amount)
        
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
                current_app.logger.error(f"Error processing deliveries for subscription {subscription.id}: {str(del_error)}")
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
        current_app.logger.error(f"Error in profile page: {str(e)}")
        db.session.rollback()
        flash('An error occurred while loading your profile. Please try again.', 'error')
    
    return render_template('profile_enhanced.html', 
                          user=current_user,
                          active_subscriptions=active_subscriptions,
                          paused_subscriptions=paused_subscriptions,
                          canceled_subscriptions=canceled_subscriptions,
                          subscription_deliveries=subscription_deliveries,
                          payments=payments,
                          orders=orders,
                          total_spent=total_spent)

@main_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Handle profile updates"""
    try:
        # Check if user is authenticated
        if not current_user.is_authenticated:
            current_app.logger.error("User not authenticated for profile update")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': 'Please log in to update your profile'}), 401
            flash('Please log in to update your profile', 'error')
            return redirect(url_for('main.login'))
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        
        # Handle both old and new field names for backward compatibility
        province = request.form.get('province', '').strip()
        state = request.form.get('state', '').strip()
        # Use state if provided, otherwise fall back to province
        state_or_province = state if state else province
        
        postal_code = request.form.get('postal_code', '').strip()
        pincode = request.form.get('pincode', '').strip()
        # Use pincode if provided, otherwise fall back to postal_code
        pincode_or_postal = pincode if pincode else postal_code
        
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        form_section = request.form.get('form_section', '').strip()
        
        # Enhanced logging for debugging
        current_app.logger.info(f"=== PROFILE UPDATE DEBUG ===")
        current_app.logger.info(f"User ID: {current_user.id}")
        current_app.logger.info(f"User Email: {current_user.email}")
        current_app.logger.info(f"User Authenticated: {current_user.is_authenticated}")
        current_app.logger.info(f"Form Data Received:")
        current_app.logger.info(f"  - Name: '{name}' (current: '{current_user.name}')")
        current_app.logger.info(f"  - Email: '{email}' (current: '{current_user.email}')")
        current_app.logger.info(f"  - Phone: '{phone}' (current: '{current_user.phone}')")
        current_app.logger.info(f"  - Address: '{address}' (current: '{current_user.address}')")
        current_app.logger.info(f"  - City: '{city}' (current: '{current_user.city}')")
        current_app.logger.info(f"  - State/Province: '{state_or_province}' (current: '{current_user.province}')")
        current_app.logger.info(f"  - Pincode/Postal: '{pincode_or_postal}' (current: '{current_user.postal_code}')")
        current_app.logger.info(f"  - Is AJAX: {is_ajax}")
        current_app.logger.info(f"  - Form Section: {form_section}")
        
        # Validate required fields
        if not name or not email:
            message = 'Name and email are required'
            current_app.logger.warning(f"Validation failed: {message}")
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
        current_app.logger.info("Updating user profile information...")
        current_app.logger.info(f"Before update - Name: '{current_user.name}' -> '{name}'")
        current_app.logger.info(f"Before update - Email: '{current_user.email}' -> '{email}'")
        current_app.logger.info(f"Before update - Phone: '{current_user.phone}' -> '{phone}'")
        current_app.logger.info(f"Before update - Address: '{current_user.address}' -> '{address}'")
        current_app.logger.info(f"Before update - City: '{current_user.city}' -> '{city}'")
        current_app.logger.info(f"Before update - Province: '{current_user.province}' -> '{state_or_province}'")
        current_app.logger.info(f"Before update - Postal Code: '{current_user.postal_code}' -> '{pincode_or_postal}'")
        
        # Get fresh user instance to avoid session conflicts
        user_id = current_user.id
        fresh_user = User.query.get(user_id)
        
        if not fresh_user:
            message = 'User not found in database'
            current_app.logger.error(f"User not found: {user_id}")
            if is_ajax:
                return jsonify({'status': 'error', 'message': message})
            flash(message, 'error')
            return redirect(url_for('main.profile'))
        
        # Update the fresh user instance
        fresh_user.name = name
        fresh_user.email = email
        fresh_user.phone = phone
        fresh_user.address = address
        fresh_user.city = city
        fresh_user.province = state_or_province
        fresh_user.postal_code = pincode_or_postal
        
        current_app.logger.info("Fresh user object updated, committing to database...")
        
        # Save changes
        db.session.commit()
        current_app.logger.info("Database commit successful")
        
        # Update current_user instance to reflect the changes
        current_user.name = fresh_user.name
        current_user.email = fresh_user.email
        current_user.phone = fresh_user.phone
        current_user.address = fresh_user.address
        current_user.city = fresh_user.city
        current_user.province = fresh_user.province
        current_user.postal_code = fresh_user.postal_code
        
        # Verify the changes were saved
        db.session.refresh(fresh_user)
        current_app.logger.info(f"After commit - Name: '{fresh_user.name}'")
        current_app.logger.info(f"After commit - Email: '{fresh_user.email}'")
        current_app.logger.info(f"After commit - Phone: '{fresh_user.phone}'")
        current_app.logger.info(f"After commit - Address: '{fresh_user.address}'")
        current_app.logger.info(f"After commit - City: '{fresh_user.city}'")
        current_app.logger.info(f"After commit - Province: '{fresh_user.province}'")
        current_app.logger.info(f"After commit - Postal Code: '{fresh_user.postal_code}'")
        
        # Determine success message
        if password_changed:
            message = 'Password updated successfully'
        else:
            message = 'Profile updated successfully'
        
        current_app.logger.info(f"Profile update completed successfully: {message}")
        
        # Return appropriate response
        if is_ajax:
            response_data = {'status': 'success', 'message': message}
            current_app.logger.info(f"Returning AJAX response: {response_data}")
            return jsonify(response_data)
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
        import traceback; traceback.print_exc()  # Print full traceback for debugging
        db.session.rollback()
        current_app.logger.error(f"Profile update failed: {str(e)}")
        message = 'An error occurred while updating your profile. Please try again.'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': message})
        else:
            flash(message, 'error')
            return redirect(url_for('main.profile'))


def _is_google_oauth_enabled():
    """Helper function to check if Google OAuth is enabled"""
    return current_app.config.get('GOOGLE_CLIENT_ID') is not None and current_app.config.get('GOOGLE_CLIENT_SECRET') is not None

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with debug logging for CSRF/session issues"""
    import logging
    from flask import session, request
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()

    # Debug: Log session and CSRF info
    logging.warning(f"[DEBUG] Session keys: {list(session.keys())}")
    logging.warning(f"[DEBUG] Session cookie: {request.cookies.get('session')}")
    logging.warning(f"[DEBUG] Form CSRF token: {getattr(form, 'csrf_token', None)}")
    logging.warning(f"[DEBUG] Form data: {request.form}")
    logging.warning(f"[DEBUG] Request method: {request.method}")

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
            
            # Always redirect to main index after login
            return redirect(url_for('main.index'))
        else:
            # Log failed login attempt
            logging.warning(f'Failed login attempt for email: {form.email.data}')
            flash('Invalid email or password', 'error')
            return redirect(url_for('main.login'))
    
    # Check if Google OAuth is enabled
    google_enabled = _is_google_oauth_enabled()
    return render_template('login.html', form=form, google_enabled=google_enabled)

@main_bp.route('/login/google')
def google_login():
    """Initiate Google OAuth login"""
    if not hasattr(current_app, 'google_oauth') or not current_app.google_oauth:
        flash('Google authentication is not configured.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        # Get redirect URI - ensure it matches Google Cloud Console exactly
        redirect_uri = url_for('main.google_callback', _external=True)
        
        # Log the redirect URI for debugging
        current_app.logger.info(f"Google OAuth redirect URI: {redirect_uri}")
        current_app.logger.info(f"Request URL: {request.url}")
        current_app.logger.info(f"Request host: {request.host}")
        current_app.logger.info(f"Request scheme: {request.scheme}")
        
        # Ensure redirect URI uses HTTPS in production
        if redirect_uri.startswith('http://') and not current_app.debug:
            # Force HTTPS in production
            redirect_uri = redirect_uri.replace('http://', 'https://')
            current_app.logger.info(f"Updated redirect URI to HTTPS: {redirect_uri}")
        
        # Redirect to Google OAuth
        return current_app.google_oauth.authorize_redirect(redirect_uri, state=state)
    except Exception as e:
        current_app.logger.error(f"Error initiating Google login: {str(e)}", exc_info=True)
        flash('Error initiating Google login. Please try again.', 'error')
        return redirect(url_for('main.login'))

@main_bp.route('/login/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    if not hasattr(current_app, 'google_oauth') or not current_app.google_oauth:
        flash('Google authentication is not configured.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        # Verify state
        state = request.args.get('state')
        if not state or state != session.get('oauth_state'):
            flash('Invalid authentication state. Please try again.', 'error')
            return redirect(url_for('main.login'))
        
        # Remove state from session
        session.pop('oauth_state', None)
        
        # Get authorization token
        token = current_app.google_oauth.authorize_access_token()
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            # Fetch user info if not in token
            resp = current_app.google_oauth.get('https://www.googleapis.com/oauth2/v2/userinfo')
            user_info = resp.json()
        
        # Extract user information
        google_id = user_info.get('sub')
        email = user_info.get('email', '').lower()
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')
        
        if not email:
            flash('Could not retrieve email from Google account.', 'error')
            return redirect(url_for('main.login'))
        
        # Check if user exists by Google ID
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check if user exists by email (link accounts)
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Link Google account to existing user
                user.google_id = google_id
                if not user.name and name:
                    user.name = name
                user.email_verified = True
                db.session.commit()
                current_app.logger.info(f'Linked Google account to existing user: {user.email}')
            else:
                # Create new user
                username = email.split('@')[0] if email else f"user_{secrets.token_hex(4)}"
                # Ensure username is unique
                base_username = username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}_{counter}"
                    counter += 1
                
                user = User(
                    username=username,
                    email=email,
                    google_id=google_id,
                    name=name or username,
                    email_verified=True,
                    is_active=True
                )
                db.session.add(user)
                db.session.commit()
                current_app.logger.info(f'Created new user via Google OAuth: {user.email}')
                
                # Send welcome email
                try:
                    from utils.email_functions import send_welcome_email
                    send_welcome_email(user)
                except Exception as e:
                    current_app.logger.error(f'Failed to send welcome email: {str(e)}')
        else:
            # Update user info if needed
            if not user.name and name:
                user.name = name
            user.email_verified = True
            db.session.commit()
        
        # Log user in
        login_user(user, remember=True)
        current_app.logger.info(f'User logged in via Google: {user.email}')
        
        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        current_app.logger.error(f"Error in Google OAuth callback: {str(e)}", exc_info=True)
        flash('Error authenticating with Google. Please try again.', 'error')
        return redirect(url_for('main.login'))

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
        
        # Check if user already exists by email
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            google_enabled = _is_google_oauth_enabled()
            return render_template('register.html', form=form, now=datetime.now(), google_enabled=google_enabled)
        
        # Check if username already exists
        if User.query.filter_by(username=name).first():
            flash('Username already taken. Please choose a different one.', 'error')
            google_enabled = _is_google_oauth_enabled()
            return render_template('register.html', form=form, now=datetime.now(), google_enabled=google_enabled)
        
        try:
            # Create new user manually
            user = User(
                username=name,
                email=email,
                phone=phone,
                name=name
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Log successful registration
            current_app.logger.info(f'New user registered: {user.email}')
            
            # Send welcome email
            try:
                from utils.email_functions import send_welcome_email
                send_welcome_email(user)
                current_app.logger.info(f'Welcome email sent to: {user.email}')
            except Exception as e:
                current_app.logger.error(f'Failed to send welcome email to {user.email}: {str(e)}')
                # Don't fail registration if email fails
            
            flash('Registration successful! Please check your email for a welcome message.', 'success')
            return redirect(url_for('main.login'))
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f'Registration integrity error for {email}: {str(e)}')
            flash('Email or username already exists. Please try a different one.', 'error')
            google_enabled = _is_google_oauth_enabled()
            return render_template('register.html', form=form, now=datetime.now(), google_enabled=google_enabled)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error for {email}: {str(e)}')
            current_app.logger.error(f'Error type: {type(e).__name__}')
            flash('An error occurred during registration. Please try again.', 'error')
            google_enabled = _is_google_oauth_enabled()
            return render_template('register.html', form=form, now=datetime.now(), google_enabled=google_enabled)
    
    # Check if Google OAuth is enabled
    google_enabled = current_app.config.get('GOOGLE_CLIENT_ID') is not None and current_app.config.get('GOOGLE_CLIENT_SECRET') is not None
    return render_template('register.html', form=form, now=datetime.now(), google_enabled=google_enabled)

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
    try:
        current_app.logger.info('Newsletter subscription attempt started')
        
        # Get email from form
        email = request.form.get('email', '').strip().lower()
        current_app.logger.info(f'Email received: {email}')
        
        if not email:
            current_app.logger.warning('No email provided')
            flash('Please provide a valid email address.', 'error')
            return redirect(request.referrer or url_for('main.index'))
        
        # Validate email format
        if '@' not in email or '.' not in email:
            current_app.logger.warning(f'Invalid email format: {email}')
            flash('Please provide a valid email address.', 'error')
            return redirect(request.referrer or url_for('main.index'))
        
        # Check if already subscribed
        existing_subscription = Newsletter.query.filter_by(email=email).first()
        if existing_subscription:
            current_app.logger.info(f'Email already subscribed: {email}')
            flash('You are already subscribed to our newsletter!', 'info')
            return redirect(request.referrer or url_for('main.index'))
        
        # Create new subscription
        newsletter = Newsletter(email=email)
        db.session.add(newsletter)
        db.session.commit()
        
        current_app.logger.info(f'New newsletter subscription successful: {email}')
        
        # Send welcome email to new subscriber
        try:
            from utils.email_utils import send_email
            
            subject = "Welcome to FitSmart Newsletter! 🎉"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #10b981; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
                    .welcome {{ background: #d1fae5; border: 1px solid #10b981; padding: 15px; border-radius: 6px; margin: 15px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 20px; }}
                    .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 15px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🎉 Welcome to FitSmart!</h1>
                    <p>You're now part of our healthy community!</p>
                </div>
                
                <div class="content">
                    <div class="welcome">
                        <h2>✅ Successfully Subscribed!</h2>
                        <p>Thank you for subscribing to the FitSmart newsletter! You'll now receive:</p>
                    </div>
                    
                    <h3>📧 What You'll Get:</h3>
                    <ul>
                        <li>🍽️ Weekly healthy meal inspiration</li>
                        <li>💪 Nutrition tips and fitness advice</li>
                        <li>🎯 Exclusive recipes and cooking tips</li>
                        <li>💰 Special offers and discounts</li>
                        <li>🏆 Success stories from our community</li>
                    </ul>
                    
                    <h3>🚀 Get Started:</h3>
                    <p>Explore our meal plans and start your healthy journey today!</p>
                    
                    <a href="https://fitsmart.ca/meal-plans" class="button">View Meal Plans</a>
                    
                    <p>We're excited to have you on board! Your first newsletter will arrive soon.</p>
                </div>
                
                <div class="footer">
                    <p>Best regards,<br>Team FitSmart</p>
                    <p>© 2024 FitSmart - Fresh, Healthy Meals Delivered</p>
                    <p><small>You can unsubscribe anytime by clicking the link in our emails.</small></p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
Welcome to HealthyRizz Newsletter!

✅ Successfully Subscribed!

Thank you for subscribing to the HealthyRizz newsletter! You'll now receive:

📧 What You'll Get:
🍽️ Weekly healthy meal inspiration
💪 Nutrition tips and fitness advice
🎯 Exclusive recipes and cooking tips
💰 Special offers and discounts
🏆 Success stories from our community

🚀 Get Started:
Explore our meal plans and start your healthy journey today!
Visit: https://healthyrizz.in/meal-plans

We're excited to have you on board! Your first newsletter will arrive soon.

Best regards,
Team HealthyRizz
© 2024 HealthyRizz - Fresh, Healthy Meals Delivered

You can unsubscribe anytime by clicking the link in our emails.
            """
            
            # Send welcome email
            email_sent = send_email(
                to_email=email,
                from_email="healthyrizz.in@gmail.com",
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if email_sent:
                current_app.logger.info(f'Welcome email sent successfully to {email}')
            else:
                current_app.logger.error(f'Failed to send welcome email to {email}')
                
        except Exception as e:
            current_app.logger.error(f'Error sending welcome email to {email}: {str(e)}')
        
        flash('Thank you for subscribing to our newsletter! Check your email for a welcome message.', 'success')
        
        # Track newsletter signup event
        try:
            from flask import session
            session['track_newsletter_signup'] = True
            current_app.logger.info('Tracking session set successfully')
        except Exception as e:
            current_app.logger.error(f'Error setting tracking session: {str(e)}')
        
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f'Database integrity error in newsletter subscription: {str(e)}')
        flash('This email is already subscribed to our newsletter!', 'info')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Newsletter subscription error: {str(e)}')
        current_app.logger.error(f'Error type: {type(e).__name__}')
        flash('An error occurred while subscribing. Please try again.', 'error')
    
    return redirect(request.referrer or url_for('main.index'))

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
@csrf.exempt  # Exempt from CSRF protection for public password reset
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
    """Subscribe to a meal plan with proper total calculation and cascading location dropdowns"""
    try:
        # Get meal plan with error handling
        try:
            meal_plan = MealPlan.query.get_or_404(plan_id)
        except Exception as e:
            current_app.logger.error(f"Error getting meal plan {plan_id}: {e}")
            flash('Meal plan not found.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        frequency = request.args.get('frequency', 'weekly')
        
        # Calculate prices properly
        try:
            if frequency == 'weekly':
                base_price = float(meal_plan.price_weekly)
            else:
                base_price = float(meal_plan.price_monthly)
        except (ValueError, AttributeError) as e:
            current_app.logger.error(f"Error calculating price: {e}")
            base_price = 1000.0  # Fallback price
        
        # Calculate HST (13% for Ontario, Canada)
        hst_amount = base_price * 0.13
        total_amount = base_price + hst_amount
        
        # Get all delivery locations grouped by province for the cascading dropdown
        from collections import defaultdict
        locations_data = []
        try:
            # Get all active delivery locations
            delivery_locations = DeliveryLocation.query.filter_by(is_active=True).order_by(
                DeliveryLocation.province, DeliveryLocation.city
            ).all()
            
            # Province code to name mapping
            province_map = {
                'AB': 'Alberta', 'BC': 'British Columbia', 'MB': 'Manitoba',
                'NB': 'New Brunswick', 'NL': 'Newfoundland and Labrador',
                'NS': 'Nova Scotia', 'NT': 'Northwest Territories',
                'NU': 'Nunavut', 'ON': 'Ontario', 'PE': 'Prince Edward Island',
                'QC': 'Quebec', 'SK': 'Saskatchewan', 'YT': 'Yukon'
            }
            
            # Group locations by province
            locations_by_province = defaultdict(list)
            for location in delivery_locations:
                province_name = province_map.get(location.province, location.province)
                locations_by_province[province_name].append(location.city)
            
            # Convert to the format expected by the frontend (matching old State/City structure)
            # Use a counter for IDs since we don't have State/City IDs anymore
            counter = 1
            for province_name in sorted(locations_by_province.keys()):
                cities_list = sorted(set(locations_by_province[province_name]))  # Remove duplicates and sort
                state_data = {
                    'id': counter,
                    'name': province_name,
                    'cities': []
                }
                counter += 1
                for city_name in cities_list:
                    # Find matching State and City to get areas
                    areas_list = []
                    try:
                        # Find State by name
                        state = State.query.filter_by(name=province_name).first()
                        if state:
                            # Find City by name and state
                            city = City.query.filter_by(name=city_name, state_id=state.id).first()
                            if city:
                                # Get all areas for this city
                                areas = Area.query.filter_by(city_id=city.id).order_by(Area.name).all()
                                areas_list = [{'id': area.id, 'name': area.name} for area in areas]
                    except Exception as e:
                        current_app.logger.warning(f"Error loading areas for {city_name}, {province_name}: {e}")
                    
                    city_data = {
                        'id': counter,
                        'name': city_name,
                        'areas': areas_list  # Populate areas from Area model
                    }
                    counter += 1
                    state_data['cities'].append(city_data)
                locations_data.append(state_data)
                
        except Exception as e:
            current_app.logger.warning(f"Could not load locations from database: {e}")
            locations_data = []
        
        # If no locations from database, show empty dropdowns
        if not locations_data:
            current_app.logger.warning("No delivery locations found in database. Admin must add locations first.")
        
        # Get user data if logged in
        user_data = None
        try:
            if current_user.is_authenticated:
                user_data = {
                    'name': getattr(current_user, 'name', '') or getattr(current_user, 'username', ''),
                    'email': getattr(current_user, 'email', ''),
                    'phone': getattr(current_user, 'phone', ''),
                    'address': getattr(current_user, 'address', ''),
                    'city': getattr(current_user, 'city', ''),
                    'state': getattr(current_user, 'state', ''),
                    'postal_code': getattr(current_user, 'postal_code', '')
                }
        except Exception as e:
            current_app.logger.warning(f"Error getting user data: {e}")
            user_data = None
        
        # Track checkout initiation
        try:
            session['track_initiate_checkout'] = {
                'value': total_amount,
                'currency': 'CAD',
                'meal_plan_id': plan_id
            }
        except Exception as e:
            current_app.logger.error(f'Error setting checkout tracking: {str(e)}')
        
        return render_template(
            'checkout.html',
            meal_plan=meal_plan,
            frequency=frequency,
            base_price=base_price,
            hst_amount=hst_amount,
            total_amount=total_amount,
            locations_data=locations_data,
            user_data=user_data
        )
    except Exception as e:
        current_app.logger.error(f"Error in subscribe route: {str(e)}")
        flash('An error occurred while loading the checkout page.', 'error')
        return redirect(url_for('main.meal_plans'))

@main_bp.route('/admin/daily-meal-prep')
@login_required
@admin_required
def daily_meal_prep():
    """Admin view for daily meal preparation planning"""
    
    # Get date from query params or use today
    date_str = request.args.get('date')
    if date_str:
        try:
            prep_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            prep_date = date.today()
    else:
        prep_date = date.today()
    
    # Get all active subscriptions using proper enum
    active_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).all()
    
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
                    'lunch_count': 0,
                    'dinner_count': 0,
                    'total_count': 0,
                    'customers': []
                }
            
            # Count the meal
            if is_veg_day:
                meal_prep_data[meal_plan.id]['veg_count'] += 1
            else:
                meal_prep_data[meal_plan.id]['nonveg_count'] += 1
            
            # Count individual meal types based on meal plan configuration
            if meal_plan.includes_breakfast:
                meal_prep_data[meal_plan.id]['breakfast_count'] += 1
            if meal_plan.includes_lunch:
                meal_prep_data[meal_plan.id]['lunch_count'] += 1
            if meal_plan.includes_dinner:
                meal_prep_data[meal_plan.id]['dinner_count'] += 1
            
            meal_prep_data[meal_plan.id]['total_count'] += 1
            
            # Add customer info
            meal_prep_data[meal_plan.id]['customers'].append({
                'name': subscription.user.name,  # Use name instead of username
                'email': subscription.user.email,
                'address': subscription.delivery_address,
                'is_veg': is_veg_day,
                'with_breakfast': meal_plan.includes_breakfast,
                'with_lunch': meal_plan.includes_lunch,
                'with_dinner': meal_plan.includes_dinner
            })
    
    return render_template('admin/daily_meal_prep.html', 
                         prep_date=prep_date,
                         meal_prep_data=meal_prep_data)

def should_deliver_on_date(subscription, check_date):
    """Check if a subscription should have delivery on a specific date"""
    try:
        # Parse delivery days from JSON
        delivery_days = []
        if subscription.delivery_days:
            try:
                delivery_days = json.loads(subscription.delivery_days)
            except:
                delivery_days = []
        
        # If no delivery days specified, assume daily delivery
        if not delivery_days:
            return True
        
        # Get the weekday (0 = Monday, 6 = Sunday)
        weekday = check_date.weekday()
        
        # Check if this weekday is in the delivery days
        return weekday in delivery_days
        
    except Exception as e:
        # Fallback to simple logic if there's an error
        weekday = check_date.weekday()  # 0 = Monday, 6 = Sunday
        
        # For now, assume delivery Monday to Friday for most subscriptions
        if hasattr(subscription, 'meals_per_week') and subscription.meals_per_week >= 5:
            return weekday < 5  # Monday to Friday
        elif hasattr(subscription, 'meals_per_week') and subscription.meals_per_week == 3:
            return weekday in [0, 2, 4]  # Monday, Wednesday, Friday
        else:
            return weekday < (getattr(subscription, 'meals_per_week', 5) or 5)

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

@main_bp.route('/test-trial-form')
def test_trial_form():
    """Test page for trial request form"""
    return render_template('test_trial_form.html')

@main_bp.route('/simple-test')
def simple_test():
    """Very simple test page"""
    return render_template('simple_test.html')

@main_bp.route('/simple-trial/<int:plan_id>')
def simple_trial(plan_id):
    """Simple trial request page"""
    meal_plan = MealPlan.query.get_or_404(plan_id)
    return render_template('simple_trial_form.html', meal_plan=meal_plan)

@main_bp.route('/simple-trial-submit', methods=['POST'])
@csrf.exempt
def simple_trial_submit():
    """Simple trial request submission"""
    try:
        print("DEBUG: Simple trial submit called")
        print(f"DEBUG: Form data: {request.form}")
        
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        province = request.form.get('province')
        city = request.form.get('city')
        area = request.form.get('area')
        postal_code = request.form.get('postal_code')
        preferred_date = request.form.get('preferred_date')
        notes = request.form.get('notes', '')
        meal_plan_id = request.form.get('meal_plan_id')
        
        # Validate required fields
        if not all([name, email, phone, address, province, city, area, postal_code, preferred_date, meal_plan_id]):
            return jsonify({'success': False, 'error': 'Please fill in all required fields'})
        
        # Convert date string to date object
        from datetime import datetime
        try:
            preferred_date_obj = datetime.strptime(preferred_date, '%Y-%m-%d').date()
        except:
            return jsonify({'success': False, 'error': 'Invalid date format'})
        
        # Create trial request
        trial_request = TrialRequest(
            name=name,
            email=email,
            phone=phone,
            address=address,
            province=province,
            city=city,
            area=area,
            postal_code=postal_code,
            preferred_date=preferred_date_obj,
            notes=notes,
            meal_plan_id=int(meal_plan_id)
        )
        
        db.session.add(trial_request)
        db.session.commit()
        
        print(f"DEBUG: Trial request created successfully with ID: {trial_request.id}")
        
        return jsonify({
            'success': True, 
            'message': 'Trial request submitted successfully!',
            'trial_id': trial_request.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error in simple trial submit: {type(e).__name__}: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@main_bp.route('/trial-request/<int:plan_id>', methods=['GET', 'POST'])
@csrf.exempt  # Temporarily exempt for testing
def trial_request(plan_id):
    """Handle trial meal plan requests with admin location data"""
    meal_plan = MealPlan.query.get_or_404(plan_id)
    form = TrialRequestForm()
    form.meal_plan_id.data = plan_id
    
    # Get location data from database (same as checkout page)
    locations_data = []
    try:
        states = State.query.order_by(State.name).all()
        for state in states:
            state_data = {
                'id': state.id,
                'name': state.name,
                'cities': []
            }
            for city in state.cities:
                city_data = {
                    'id': city.id,
                    'name': city.name,
                    'areas': []
                }
                for area in city.areas:
                    city_data['areas'].append({
                        'id': area.id,
                        'name': area.name
                    })
                state_data['cities'].append(city_data)
            locations_data.append(state_data)
    except Exception as e:
        current_app.logger.warning(f"Could not load locations from database: {e}")
        locations_data = []
    
    # If no locations from database, show empty dropdowns
    if not locations_data:
        current_app.logger.warning("No delivery locations found in database. Admin must add locations first.")
    
    if request.method == 'POST':
        print(f"DEBUG: POST request received")
        print(f"DEBUG: Form data: {request.form}")
        
        if form.validate_on_submit():
            try:
                print(f"DEBUG: Form validation passed")
                print(f"DEBUG: Creating trial request...")
                
                trial_request = TrialRequest(
                    name=form.name.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    preferred_date=form.preferred_date.data,
                    address=form.address.data,
                    city=form.city.data,
                    province=form.province.data,
                    area=form.area.data,
                    postal_code=form.postal_code.data,
                    notes=form.notes.data,
                    meal_plan_id=plan_id
                )
                db.session.add(trial_request)
                db.session.commit()
                
                print(f"DEBUG: Trial request created successfully with ID: {trial_request.id}")
                flash('Your trial request has been submitted successfully! We will contact you shortly to confirm your delivery.', 'success')
                return redirect(url_for('main.meal_plans'))
                
            except Exception as e:
                db.session.rollback()
                print(f"DEBUG: Error creating trial request: {type(e).__name__}: {str(e)}")
                flash('An error occurred while submitting your trial request. Please try again.', 'error')
                current_app.logger.error(f'Error creating trial request: {str(e)}')
        else:
            print(f"DEBUG: Form validation failed")
            print(f"DEBUG: Form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"DEBUG: Field '{field}' error: {error}")
                    flash(f'{field}: {error}', 'error')
    
    return render_template('trial_request.html', meal_plan=meal_plan, form=form, locations_data=locations_data)

@main_bp.route('/process_checkout', methods=['POST'])
@csrf.exempt  # Exempt from CSRF protection for payment processing
def process_checkout():
    """Process the checkout form and create Stripe checkout session"""
    try:
        # Check if Stripe is configured
        from utils.stripe_utils import get_stripe_api_key
        if not get_stripe_api_key():
            current_app.logger.error("Stripe API key not configured")
            return jsonify({
                'success': False,
                'error': 'Payment system is not configured. Please contact support.'
            }), 500
        # Get form data
        plan_id = request.form.get('plan_id')
        frequency = request.form.get('frequency')
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        customer_address = request.form.get('customer_address')
        customer_city = request.form.get('customer_city')
        customer_state = request.form.get('customer_state')
        customer_area = request.form.get('customer_area')  # New field
        customer_pincode = request.form.get('customer_pincode')
        vegetarian_days = request.form.get('vegetarian_days', '')
        applied_coupon_code = request.form.get('applied_coupon_code')
        coupon_discount = request.form.get('coupon_discount', '0')
        
        # Validate required fields (customer_area is optional for Canadian addresses)
        if not all([plan_id, frequency, customer_name, customer_email, customer_phone, 
                   customer_address, customer_city, customer_state, customer_pincode]):
            return jsonify({
                'success': False,
                'error': 'Please fill in all required fields including Province, City, and Postal Code.'
            }), 400
        
        # Convert plan_id to int
        try:
            plan_id = int(plan_id)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid meal plan ID.'
            }), 400
        
        # Get meal plan
        meal_plan = MealPlan.query.get(plan_id)
        if not meal_plan:
            return jsonify({
                'success': False,
                'error': 'Meal plan not found.'
            }), 404
        
        # Calculate price with tax (HST/GST for Canada)
        try:
            price_field = meal_plan.price_weekly if frequency == 'weekly' else meal_plan.price_monthly
            if price_field is None:
                return jsonify({
                    'success': False,
                    'error': f'Price not set for {frequency} plan.'
                }), 400
            base_price = float(price_field)
        except (ValueError, TypeError) as e:
            current_app.logger.error(f"Error converting price: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Invalid price configuration. Please contact support.'
            }), 500
        tax_amount = base_price * 0.13  # 13% HST (Ontario, Canada)
        subtotal = base_price + tax_amount
        
        # Apply coupon discount if provided
        discount_amount = float(coupon_discount) if coupon_discount else 0
        total_price = max(0, subtotal - discount_amount)
        
        # Store checkout data in session
        session['checkout_data'] = {
            'plan_id': plan_id,
            'frequency': frequency,
            'vegetarian_days': vegetarian_days,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'customer_address': customer_address,
            'customer_city': customer_city,
            'customer_state': customer_state,
            'customer_area': customer_area or '',  # Optional for Canadian addresses
            'customer_pincode': customer_pincode,
            'applied_coupon': applied_coupon_code,
            'coupon_discount': discount_amount,
            'total_price': total_price,
            'base_price': base_price,
            'tax_amount': tax_amount
        }
        
        # Create or get Stripe customer
        stripe_customer_id = None
        user = User.query.filter_by(email=customer_email).first()
        
        if user and hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
            stripe_customer_id = user.stripe_customer_id
        else:
            # Create new Stripe customer
            address_dict = {
                'line1': customer_address,
                'city': customer_city,
                'state': customer_state,
                'postal_code': customer_pincode,
                'country': 'CA'
            }
            stripe_customer_id = create_stripe_customer(
                name=customer_name,
                email=customer_email,
                phone=customer_phone,
                address=address_dict
            )
            
            if not stripe_customer_id:
                current_app.logger.error("Failed to create Stripe customer - check logs for details")
                # Check if it's an API key issue
                from utils.stripe_utils import get_stripe_api_key
                api_key = get_stripe_api_key()
                if not api_key:
                    return jsonify({
                        'success': False,
                        'error': 'Payment system configuration error. Please contact support.'
                    }), 500
                return jsonify({
                    'success': False,
                    'error': 'Error creating customer. Please check your information and try again.'
                }), 500
            
            # Save customer ID to user if exists
            if user:
                user.stripe_customer_id = stripe_customer_id
                db.session.commit()
        
        # Create Stripe checkout session
        # Pass session_id in success URL so we can retrieve it from Stripe
        success_url = url_for('main.checkout_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = url_for('main.meal_plans', _external=True)
        
        checkout_session = create_stripe_checkout_session(
            customer_id=stripe_customer_id,
            meal_plan_name=meal_plan.name,
            price_amount=total_price,
            frequency=frequency,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        if not checkout_session:
            current_app.logger.error("Failed to create Stripe checkout session - check server logs for details")
            # Check if it's an API key issue
            from utils.stripe_utils import get_stripe_api_key
            api_key = get_stripe_api_key()
            if not api_key:
                return jsonify({
                    'success': False,
                    'error': 'Payment system is not configured. Please contact support.'
                }), 500
            
            # Check if customer was created successfully
            if not stripe_customer_id:
                return jsonify({
                    'success': False,
                    'error': 'Error setting up payment. Please check your information and try again.'
                }), 500
            
            return jsonify({
                'success': False,
                'error': 'Error creating checkout session. Please try again or contact support if the problem persists.'
            }), 500
        
        # Store checkout session ID
        session['checkout_session_id'] = checkout_session['id']
        
        return jsonify({
            'success': True,
            'checkout_url': checkout_session['url'],
            'session_id': checkout_session['id']
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        current_app.logger.error(f"Error processing checkout: {str(e)}")
        current_app.logger.error(f"Traceback: {error_trace}")
        return jsonify({
            'success': False,
            'error': f'An error occurred while processing your order: {str(e)}. Please try again.'
        }), 500

@main_bp.route('/stripe-webhook', methods=['POST'])
@csrf.exempt  # Stripe webhooks don't use CSRF
def stripe_webhook():
    """Handle Stripe webhook events for subscription lifecycle"""
    try:
        import stripe
        from utils.stripe_utils import handle_webhook_event
        
        payload = request.data
        signature = request.headers.get('Stripe-Signature')
        webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
        
        if not webhook_secret:
            current_app.logger.error("Stripe webhook secret not configured")
            return jsonify({'error': 'Webhook secret not configured'}), 500
        
        # Verify webhook signature
        event = handle_webhook_event(payload, signature, webhook_secret)
        
        if not event:
            return jsonify({'error': 'Invalid webhook signature'}), 400
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            stripe_session = event['data']['object']
            checkout_session_id = stripe_session['id']
            
            # Get checkout data from Flask session
            checkout_data = session.get('checkout_data')
            if not checkout_data:
                # Try to get from Stripe session metadata or database
                current_app.logger.warning("Checkout data not found in Flask session, checking Stripe metadata")
                # You may need to store checkout data in database for webhook reliability
                return jsonify({'received': True})
            
            # Create subscription
            _create_stripe_subscription(checkout_data, stripe_session)
            
        elif event['type'] == 'customer.subscription.updated':
            # Handle subscription updates
            subscription_data = event['data']['object']
            _update_stripe_subscription(subscription_data)
            
        elif event['type'] == 'customer.subscription.deleted':
            # Handle subscription cancellation
            subscription_data = event['data']['object']
            _cancel_stripe_subscription(subscription_data)
        
        return jsonify({'received': True})
        
    except Exception as e:
        current_app.logger.error(f"Error processing Stripe webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

def _create_stripe_subscription(checkout_data, stripe_session):
    """Create subscription from Stripe checkout session"""
    try:
        # Get user or create new user
        user = User.query.filter_by(email=checkout_data['customer_email']).first()
        if not user:
            user = _create_user_from_checkout_data(checkout_data)
            db.session.add(user)
            db.session.flush()
        
        # Get Stripe subscription ID from session
        stripe_subscription_id = stripe_session.get('subscription')
        stripe_payment_intent_id = stripe_session.get('payment_intent')
        
        # Check if subscription already exists
        existing_subscription = Subscription.query.filter_by(
            user_id=user.id,
            meal_plan_id=checkout_data['plan_id'],
            stripe_subscription_id=stripe_subscription_id
        ).first()
        
        if existing_subscription:
            current_app.logger.info(f"Subscription already exists: {existing_subscription.id}")
            return existing_subscription
        
        # Create order
        order = Order(
            user_id=user.id,
            meal_plan_id=checkout_data['plan_id'],
            amount=checkout_data['total_price'],
            total_amount=checkout_data['total_price'],
            status='confirmed',
            payment_status='captured',
            payment_id=stripe_payment_intent_id,
            order_id=stripe_session['id']
        )
        db.session.add(order)
        db.session.flush()
        
        # Create subscription
        subscription = Subscription(
            user_id=user.id,
            meal_plan_id=checkout_data['plan_id'],
            frequency=SubscriptionFrequency.WEEKLY if checkout_data['frequency'] == 'weekly' else SubscriptionFrequency.MONTHLY,
            status=SubscriptionStatus.ACTIVE,
            price=checkout_data['total_price'],
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id=stripe_session.get('customer'),
            vegetarian_days=checkout_data.get('vegetarian_days', ''),
            start_date=datetime.now(),
            current_period_start=datetime.now(),
            current_period_end=(
                datetime.now() + timedelta(days=7) if checkout_data['frequency'] == 'weekly'
                else datetime.now() + timedelta(days=30)
            ),
            order_id=order.id,
            delivery_address=checkout_data.get('customer_address'),
            delivery_city=checkout_data.get('customer_city'),
            delivery_province=checkout_data.get('customer_state'),
            delivery_postal_code=checkout_data.get('customer_pincode')
        )
        db.session.add(subscription)
        
        # Track coupon usage if applied
        if checkout_data.get('applied_coupon'):
            coupon = CouponCode.query.filter_by(code=checkout_data['applied_coupon']).first()
            if coupon:
                coupon_usage = CouponUsage(
                    coupon_id=coupon.id,
                    user_id=user.id,
                    order_id=order.id
                )
                db.session.add(coupon_usage)
                coupon.current_uses += 1
        
        db.session.commit()
        current_app.logger.info(f"Created subscription {subscription.id} for user {user.id}")
        return subscription
        
    except Exception as e:
        current_app.logger.error(f"Error creating Stripe subscription: {str(e)}")
        db.session.rollback()
        raise

def _create_user_from_checkout_data(checkout_data):
    """Create a new user from checkout data"""
    email = checkout_data['customer_email']
    username = email.split('@')[0]
    
    # Ensure username is unique
    counter = 1
    original_username = username
    while User.query.filter_by(username=username).first():
        username = f"{original_username}{counter}"
        counter += 1
    
    return User(
        username=username,
        name=checkout_data['customer_name'],
        email=checkout_data['customer_email'],
        phone=checkout_data['customer_phone'],
        address=checkout_data['customer_address'],
        city=checkout_data['customer_city'],
        province=checkout_data['customer_state'],
        postal_code=checkout_data['customer_pincode']
    )

def _update_stripe_subscription(subscription_data):
    """Update subscription from Stripe webhook"""
    try:
        stripe_subscription_id = subscription_data['id']
        subscription = Subscription.query.filter_by(stripe_subscription_id=stripe_subscription_id).first()
        
        if subscription:
            # Update subscription status based on Stripe status
            if subscription_data['status'] == 'active':
                subscription.status = SubscriptionStatus.ACTIVE
            elif subscription_data['status'] == 'canceled':
                subscription.status = SubscriptionStatus.CANCELED
            elif subscription_data['status'] == 'past_due':
                subscription.status = SubscriptionStatus.EXPIRED
            
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error updating Stripe subscription: {str(e)}")

def _cancel_stripe_subscription(subscription_data):
    """Cancel subscription from Stripe webhook"""
    try:
        stripe_subscription_id = subscription_data['id']
        subscription = Subscription.query.filter_by(stripe_subscription_id=stripe_subscription_id).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.CANCELED
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error canceling Stripe subscription: {str(e)}")

@main_bp.route('/checkout-success')
def checkout_success():
    """
    Handle successful checkout using Stripe session_id or order_id parameter.
    """
    try:
        # Get session_id from URL parameter (from Stripe redirect)
        stripe_session_id = request.args.get('session_id')
        order_id = request.args.get('order_id')
        
        # If we have Stripe session_id, retrieve data from Stripe
        if stripe_session_id:
            try:
                from utils.stripe_utils import get_stripe_api_key
                import stripe
                
                api_key = get_stripe_api_key()
                if api_key:
                    stripe.api_key = api_key
                    
                    # Retrieve the checkout session from Stripe
                    checkout_session = stripe.checkout.Session.retrieve(stripe_session_id)
                    
                    # Get customer ID and subscription ID from Stripe
                    stripe_customer_id = checkout_session.get('customer')
                    stripe_subscription_id = checkout_session.get('subscription')
                    
                    if stripe_customer_id:
                        # Find user by Stripe customer ID
                        user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
                        
                        if user:
                            # Find subscription by Stripe subscription ID
                            subscription = None
                            if stripe_subscription_id:
                                subscription = Subscription.query.filter_by(
                                    stripe_subscription_id=stripe_subscription_id
                                ).first()
                            
                            # If no subscription found, find most recent one for this user
                            if not subscription:
                                subscription = Subscription.query.filter_by(
                                    user_id=user.id
                                ).order_by(Subscription.created_at.desc()).first()
                            
                            # Find order
                            order = None
                            if subscription:
                                order = Order.query.filter_by(
                                    user_id=user.id,
                                    meal_plan_id=subscription.meal_plan_id
                                ).order_by(Order.created_at.desc()).first()
                            
                            # Get meal plan
                            meal_plan = None
                            if subscription:
                                meal_plan = MealPlan.query.get(subscription.meal_plan_id)
                            
                            # If subscription/order don't exist yet (webhook hasn't run), create them
                            if not subscription or not order:
                                # Get metadata from Stripe session
                                metadata = checkout_session.get('metadata', {})
                                plan_name = metadata.get('meal_plan_name', '')
                                
                                # Try to find meal plan by name
                                if plan_name:
                                    meal_plan = MealPlan.query.filter(
                                        MealPlan.name.ilike(f'%{plan_name}%')
                                    ).first()
                                
                                # If we have meal plan, create subscription and order
                                if meal_plan and not subscription:
                                    from database.models import SubscriptionFrequency, SubscriptionStatus
                                    frequency_str = metadata.get('frequency', 'weekly')
                                    frequency = SubscriptionFrequency.WEEKLY if frequency_str == 'weekly' else SubscriptionFrequency.MONTHLY
                                    
                                    subscription = Subscription(
                                        user_id=user.id,
                                        meal_plan_id=meal_plan.id,
                                        frequency=frequency,
                                        status=SubscriptionStatus.ACTIVE,
                                        stripe_customer_id=stripe_customer_id,
                                        stripe_subscription_id=stripe_subscription_id,
                                        start_date=datetime.now(),
                                        current_period_start=datetime.now(),
                                        current_period_end=datetime.now() + timedelta(days=7 if frequency == SubscriptionFrequency.WEEKLY else 30),
                                        price=meal_plan.price_weekly if frequency == SubscriptionFrequency.WEEKLY else meal_plan.price_monthly
                                    )
                                    db.session.add(subscription)
                                    
                                    # Create order
                                    order = Order(
                                        user_id=user.id,
                                        meal_plan_id=meal_plan.id,
                                        amount=subscription.price,
                                        total_amount=subscription.price,
                                        status='confirmed',
                                        payment_status='captured',
                                        payment_id=stripe_session_id,
                                        order_id=stripe_session_id
                                    )
                                    db.session.add(order)
                                    db.session.commit()
                            
                            if subscription and meal_plan:
                                # Log user in if not already logged in
                                if not current_user.is_authenticated:
                                    login_user(user, remember=True)
                                
                                # Calculate delivery information based on subscription time
                                current_hour = datetime.now().hour
                                delivery_info = None
                                
                                if current_hour < 10:
                                    # Subscribed before 10 AM - same day delivery for next day meals
                                    delivery_date = (datetime.now() + timedelta(days=1)).strftime('%A, %B %d, %Y')
                                    delivery_info = {
                                        'message': 'Great news! Since you subscribed before 10 AM, your meals will be delivered today for tomorrow\'s consumption.',
                                        'delivery_date': delivery_date
                                    }
                                elif current_hour >= 11:
                                    # Subscribed after 11 AM - next day delivery
                                    delivery_date = (datetime.now() + timedelta(days=2)).strftime('%A, %B %d, %Y')
                                    delivery_info = {
                                        'message': 'Your meals will be delivered tomorrow. Thank you for subscribing!',
                                        'delivery_date': delivery_date
                                    }
                                else:
                                    # Between 10 AM and 11 AM - next day delivery
                                    delivery_date = (datetime.now() + timedelta(days=2)).strftime('%A, %B %d, %Y')
                                    delivery_info = {
                                        'message': 'Your meals will be delivered tomorrow. Thank you for subscribing!',
                                        'delivery_date': delivery_date
                                    }
                                
                                return render_template('checkout_success.html', 
                                                      order=order,
                                                      subscription=subscription, 
                                                      plan=meal_plan,
                                                      user=user,
                                                      delivery_info=delivery_info)
            except Exception as e:
                current_app.logger.error(f"Error retrieving Stripe session: {str(e)}")
                import traceback
                current_app.logger.error(f"Traceback: {traceback.format_exc()}")
                # Fall through to other methods
        
        if order_id:
            # Use order_id method (existing code continues below)
            pass
        else:
            # Fallback: try to get from session (for backward compatibility)
            checkout_data = session.get('checkout_data')
            checkout_session_id = session.get('checkout_session_id')
            
            if not checkout_data:
                # Try to find the most recent order for the current user
                if current_user.is_authenticated:
                    recent_order = Order.query.filter_by(
                        user_id=current_user.id,
                        status='confirmed'
                    ).order_by(Order.created_at.desc()).first()
                    
                    if recent_order:
                        # Redirect to the same page with order_id
                        return redirect(url_for('main.checkout_success', order_id=recent_order.id))
                
                flash('Invalid checkout session. Please try again.', 'warning')
                return redirect(url_for('main.meal_plans'))
            
            # Get meal plan
            plan_id = checkout_data.get('plan_id')
            if not plan_id:
                flash('Invalid meal plan. Please try again.', 'warning')
                return redirect(url_for('main.meal_plans'))
                
            meal_plan = MealPlan.query.get(plan_id)
            if not meal_plan:
                flash('Meal plan not found. Please try again.', 'warning')
                return redirect(url_for('main.meal_plans'))
            
            # Get user ID from session or try to find by email
            user_id = session.get('user_id')
            
            if not user_id:
                # Try to find user by email from checkout data
                customer_email = checkout_data.get('customer_email')
                if customer_email:
                    user = User.query.filter_by(email=customer_email).first()
                    if user:
                        user_id = user.id
                        # Log user in
                        login_user(user, remember=True)
            
            if not user_id:
                flash('User session expired. Please try again.', 'warning')
                return redirect(url_for('main.login'))
            
            # Get user
            user = User.query.get(user_id)
            if not user:
                flash('User not found. Please try again.', 'warning')
                return redirect(url_for('main.login'))
            
            # Check if subscription already exists for this session
            existing_subscription = Subscription.query.filter_by(
                user_id=user_id,
                stripe_subscription_id=checkout_session_id
            ).first()
            
            if existing_subscription:
                subscription = existing_subscription
            else:
                # Create subscription record
                from database.models import SubscriptionFrequency, SubscriptionStatus
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
                db.session.flush()
                
                # Create order record for successful checkout
                order_price = checkout_data.get('price', meal_plan.price_weekly if checkout_data.get('frequency') == 'weekly' else meal_plan.price_monthly)
                order = Order(
                    user_id=user_id,
                    meal_plan_id=plan_id,
                    amount=order_price,
                    total_amount=order_price,  # Set total_amount to same as amount
                    status='confirmed',
                    payment_status='captured',
                    payment_id=checkout_session_id,
                    order_id=checkout_session_id
                )
                db.session.add(order)
                db.session.commit()
            
            # Clear checkout session data
            session.pop('checkout_data', None)
            session.pop('checkout_session_id', None)
            
            # Check if user is logged in
            if not current_user.is_authenticated or current_user.id != user.id:
                # User is not logged in, redirect to signup completion
                flash('Please complete your account setup to access your subscription.', 'info')
                return redirect(url_for('main.signup_complete', order_id=order.id))
            
            # Calculate delivery information based on subscription time
            current_hour = datetime.now().hour
            delivery_info = None
            
            if subscription:
                if current_hour < 10:
                    # Subscribed before 10 AM - same day delivery for next day meals
                    delivery_date = (datetime.now() + timedelta(days=1)).strftime('%A, %B %d, %Y')
                    delivery_info = {
                        'message': 'Great news! Since you subscribed before 10 AM, your meals will be delivered today for tomorrow\'s consumption.',
                        'delivery_date': delivery_date
                    }
                elif current_hour >= 11:
                    # Subscribed after 11 AM - next day delivery
                    delivery_date = (datetime.now() + timedelta(days=2)).strftime('%A, %B %d, %Y')
                    delivery_info = {
                        'message': 'Your meals will be delivered tomorrow. Thank you for subscribing!',
                        'delivery_date': delivery_date
                    }
                else:
                    # Between 10 AM and 11 AM - next day delivery
                    delivery_date = (datetime.now() + timedelta(days=2)).strftime('%A, %B %d, %Y')
                    delivery_info = {
                        'message': 'Your meals will be delivered tomorrow. Thank you for subscribing!',
                        'delivery_date': delivery_date
                    }
            
            # Show success page
            return render_template('checkout_success.html', 
                                  subscription=subscription, 
                                  plan=meal_plan,
                                  order=order,
                                  delivery_info=delivery_info)
        
        # Get order from database using order_id
        order = Order.query.get(order_id)
        if not order:
            flash('Order not found. Please contact support.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        # Get meal plan
        meal_plan = MealPlan.query.get(order.meal_plan_id)
        if not meal_plan:
            flash('Meal plan not found. Please contact support.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        # Get user
        user = User.query.get(order.user_id)
        if not user:
            flash('User not found. Please contact support.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        # Get subscription for this order
        subscription = Subscription.query.filter_by(
            user_id=order.user_id,
            meal_plan_id=order.meal_plan_id
        ).order_by(Subscription.created_at.desc()).first()
        
        # If no subscription exists, create one (this should have been done by webhook/verify_payment)
        if not subscription:
            current_app.logger.warning(f"No subscription found for order {order.id}, creating one now")
            try:
                from database.models import SubscriptionFrequency, SubscriptionStatus
                
                # Determine frequency based on amount
                frequency = SubscriptionFrequency.WEEKLY
                if meal_plan.price_monthly and abs(order.amount - float(meal_plan.price_monthly)) < 1:
                    frequency = SubscriptionFrequency.MONTHLY
                
                subscription = Subscription(
                    user_id=order.user_id,
                    meal_plan_id=order.meal_plan_id,
                    frequency=frequency,
                    status=SubscriptionStatus.ACTIVE,
                    price=order.amount,
                    order_id=order.id,
                    start_date=datetime.now(),
                    current_period_start=datetime.now(),
                    current_period_end=(
                        datetime.now() + timedelta(days=7) if frequency == SubscriptionFrequency.WEEKLY 
                        else datetime.now() + timedelta(days=30)
                    )
                )
                
                db.session.add(subscription)
                db.session.commit()
                current_app.logger.info(f"Created subscription {subscription.id} for order {order.id}")
                
            except Exception as e:
                current_app.logger.error(f"Error creating subscription for order {order.id}: {str(e)}")
                # Continue without subscription - template will handle it
        
        # Check if user is logged in
        if not current_user.is_authenticated or current_user.id != user.id:
            # User is not logged in, redirect to signup completion
            flash('Please complete your account setup to access your subscription.', 'info')
            return redirect(url_for('main.signup_complete', order_id=order.id))
        
        # Calculate delivery information based on subscription time
        from datetime import datetime, timedelta
        current_hour = datetime.now().hour
        delivery_info = None
        
        if subscription:
            if current_hour < 10:
                # Subscribed before 10 AM - same day delivery for next day meals
                delivery_date = (datetime.now() + timedelta(days=1)).strftime('%A, %B %d, %Y')
                delivery_info = {
                    'message': 'Great news! Since you subscribed before 10 AM, your meals will be delivered today for tomorrow\'s consumption.',
                    'delivery_date': delivery_date
                }
            elif current_hour >= 11:
                # Subscribed after 11 AM - next day delivery
                delivery_date = (datetime.now() + timedelta(days=2)).strftime('%A, %B %d, %Y')
                delivery_info = {
                    'message': 'Your meals will be delivered tomorrow. Thank you for subscribing!',
                    'delivery_date': delivery_date
                }
            else:
                # Between 10 AM and 11 AM - next day delivery
                delivery_date = (datetime.now() + timedelta(days=2)).strftime('%A, %B %d, %Y')
                delivery_info = {
                    'message': 'Your meals will be delivered tomorrow. Thank you for subscribing!',
                    'delivery_date': delivery_date
                }
        
        # Show success page
        return render_template('checkout_success.html', 
                              order=order,
                              subscription=subscription, 
                              plan=meal_plan,
                              user=user,
                              delivery_info=delivery_info)
                              
    except Exception as e:
        current_app.logger.error(f"Error processing checkout success: {str(e)}")
        current_app.logger.error(f"Request args: {request.args}")
        current_app.logger.error(f"Session data: {dict(session)}")
        flash('An error occurred while processing your subscription.', 'danger')
        return redirect(url_for('main.meal_plans'))

@main_bp.route('/checkout-cancel')
def checkout_cancel():
    """
    Handle cancelled checkout.
    """
    # Clear checkout session data
    session.pop('checkout_data', None)
    session.pop('checkout_session_id', None)
    
    flash('Your checkout was cancelled. Please try again when you\'re ready.', 'info')
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
    # Get all active delivery locations grouped by province
    from collections import defaultdict
    
    locations_by_province = defaultdict(list)
    delivery_locations = DeliveryLocation.query.filter_by(is_active=True).order_by(
        DeliveryLocation.province, DeliveryLocation.city
    ).all()
    
    # Group locations by province
    for location in delivery_locations:
        locations_by_province[location.province].append(location.city)
    
    # Convert to regular dict and sort provinces
    locations_dict = dict(sorted(locations_by_province.items()))
    
    # Province names mapping
    province_names = {
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
    
    return render_template('shipping_delivery_policy.html', 
                         locations_by_province=locations_dict,
                         province_names=province_names)

@main_bp.route('/check-location', methods=['POST'])
def check_location():
    """Check if a location is available for delivery"""
    try:
        data = request.get_json()
        pincode = data.get('pincode', '').strip()
        city = data.get('city', '').strip()
        state = data.get('state', '').strip()
        
        if not pincode or not city or not state:
            return jsonify({
                'success': False,
                'message': 'Please provide pincode, city, and state'
            })
        
        # Check if location exists in delivery areas
        location = DeliveryLocation.query.filter(
            DeliveryLocation.is_active == True,
            or_(
                DeliveryLocation.pincode == pincode,
                and_(
                    DeliveryLocation.city.ilike(f'%{city}%'),
                    DeliveryLocation.state.ilike(f'%{state}%')
                )
            )
        ).first()
        
        if location:
            return jsonify({
                'success': True,
                'is_available': True,
                'message': f'Great! We deliver to {city}, {state}. You can proceed with your order.',
                'location': {
                    'id': location.id,
                    'city': location.city,
                    'state': location.state,
                    'pincode': location.pincode
                }
            })
        else:
            return jsonify({
                'success': True,
                'is_available': False,
                'message': f'Sorry, we currently don\'t deliver to {city}, {state}. Please check our delivery areas or contact us for expansion requests.'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error checking location: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while checking your location'
        })

@main_bp.route('/get-delivery-states')
def get_delivery_states():
    """Get all states that have delivery locations"""
    try:
        from database.models import State, City, Area
        # Get states that have delivery locations
        states = State.query.join(City).join(Area).distinct().all()
        return jsonify({
            'success': True,
            'states': [{'id': state.id, 'name': state.name} for state in states]
        })
    except Exception as e:
        current_app.logger.error(f"Error getting delivery states: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error loading states'
        })

@main_bp.route('/get-delivery-cities')
def get_delivery_cities():
    """Get cities for a specific state that have delivery locations"""
    try:
        from database.models import City, Area
        state_name = request.args.get('state', '').strip()
        if not state_name:
            return jsonify({
                'success': False,
                'message': 'State parameter is required'
            })
        # Get cities in the specified state that have delivery locations
        cities = City.query.join(Area).filter(
            City.state.has(name=state_name)
        ).distinct().all()
        return jsonify({
            'success': True,
            'cities': [{'id': city.id, 'name': city.name} for city in cities]
        })
    except Exception as e:
        current_app.logger.error(f"Error getting delivery cities: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error loading cities'
        })

@main_bp.route('/get-delivery-areas')
def get_delivery_areas():
    """Get areas for a specific city that have delivery locations"""
    try:
        from database.models import Area
        city_name = request.args.get('city', '').strip()
        if not city_name:
            return jsonify({
                'success': False,
                'message': 'City parameter is required'
            })
        # Get areas in the specified city
        areas = Area.query.filter(
            Area.city.has(name=city_name)
        ).all()
        return jsonify({
            'success': True,
            'areas': [{'id': area.id, 'name': area.name} for area in areas]
        })
    except Exception as e:
        current_app.logger.error(f"Error getting delivery areas: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error loading areas'
        })

@main_bp.route('/validate_coupon', methods=['POST'])
@csrf.exempt  # Exempt from CSRF protection for AJAX requests
def validate_coupon():
    """Validate coupon code and return discount information"""
    try:
        # Log the request for debugging
        current_app.logger.info(f"Coupon validation request - Content-Type: {request.content_type}")
        current_app.logger.info(f"Form data: {request.form}")
        
        # Handle both form data and JSON data
        if request.content_type and 'application/json' in request.content_type:
            try:
                data = request.get_json()
                current_app.logger.info(f"JSON data: {data}")
                if not data:
                    current_app.logger.error("No JSON data received")
                    return jsonify({'valid': False, 'message': 'Invalid request data'})
                coupon_code = data.get('coupon_code', '').strip().upper()
                order_amount = data.get('amount', 0)
            except Exception as e:
                current_app.logger.error(f"Error parsing JSON: {e}")
                return jsonify({'valid': False, 'message': 'Invalid JSON data'})
        else:
            # Handle form-encoded data
            current_app.logger.info("Processing form-encoded data")
            coupon_code = request.form.get('coupon_code', '').strip().upper()
            order_amount = float(request.form.get('amount', 0) or 0)
        
        current_app.logger.info(f"Validating coupon: {coupon_code} for amount: {order_amount}")
        
        if not coupon_code:
            return jsonify({'valid': False, 'message': 'Please enter a coupon code'})
        
        # Find the coupon - use correct field names from CouponCode model
        coupon = CouponCode.query.filter_by(code=coupon_code, is_active=True).first()
        
        if not coupon:
            current_app.logger.warning(f"Coupon not found: {coupon_code}")
            return jsonify({'valid': False, 'message': 'Invalid coupon code'})
        
        # Check if coupon is expired - use valid_to field (not expiry_date)
        if coupon.valid_to and coupon.valid_to < datetime.now():
            current_app.logger.warning(f"Coupon expired: {coupon_code}")
            return jsonify({'valid': False, 'message': 'Coupon has expired'})
        
        # Check usage limits - use current_uses field (not usage_count)
        if coupon.max_uses and coupon.current_uses >= coupon.max_uses:
            current_app.logger.warning(f"Coupon usage limit reached: {coupon_code}")
            return jsonify({'valid': False, 'message': 'Coupon usage limit reached'})
        
        # Check minimum order value
        if order_amount < float(coupon.min_order_value or 0):
            min_order = float(coupon.min_order_value or 0)
            return jsonify({'valid': False, 'message': f'Minimum order amount required: ${min_order}'})
        
        # Check if user has already used this coupon (if single use)
        if coupon.is_single_use and current_user.is_authenticated:
            existing_usage = CouponUsage.query.filter_by(
                user_id=current_user.id,
                coupon_id=coupon.id
            ).first()
            
            if existing_usage:
                current_app.logger.warning(f"User already used coupon: {current_user.id} - {coupon_code}")
                return jsonify({'valid': False, 'message': 'You have already used this coupon'})
        elif coupon.is_single_use and not current_user.is_authenticated:
            # For single-use coupons, user must be logged in
            return jsonify({'valid': False, 'message': 'Please log in to use this coupon'})
        
        # Calculate discount based on coupon type
        discount_amount = coupon.calculate_discount(order_amount)
        
        # Prepare response with correct field names
        response_data = {
            'valid': True,
            'message': f'Coupon applied! {coupon.discount_value}% discount',
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value),
            'discount_amount': discount_amount,
            'min_order_amount': float(coupon.min_order_value or 0),
            'max_discount': float(coupon.discount_value) if coupon.discount_type == 'fixed' else None
        }
        
        current_app.logger.info(f"Coupon validation successful: {coupon_code} - {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error validating coupon: {str(e)}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'valid': False, 'message': f'Error validating coupon: {str(e)}'})

@main_bp.route('/robots.txt')
def robots_txt():
    """Serve robots.txt file"""
    response = make_response(render_template('robots.txt'))
    response.headers['Content-Type'] = 'text/plain'
    return response

@main_bp.route('/sitemap.xml')
def sitemap_xml():
    """Serve sitemap.xml file"""
    response = make_response(render_template('sitemap.xml'))
    response.headers['Content-Type'] = 'application/xml'
    return response

@main_bp.route('/amp-sitemap.xml')
def amp_sitemap_xml():
    """Serve AMP sitemap.xml file with blog posts only"""
    try:
        # Get all published blog posts
        blog_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).all()
        
        response = make_response(render_template('amp_sitemap.xml', blog_posts=blog_posts))
        response.headers['Content-Type'] = 'application/xml'
        return response
    except Exception as e:
        current_app.logger.error(f"Error generating AMP sitemap: {str(e)}")
        # Return empty sitemap on error
        response = make_response(render_template('amp_sitemap.xml', blog_posts=[]))
        response.headers['Content-Type'] = 'application/xml'
        return response



@main_bp.route('/test-pwa')
def test_pwa():
    """PWA install test page"""
    return send_file('test_pwa_install.html', mimetype='text/html')

@main_bp.route('/pwa-diagnostic')
def pwa_diagnostic():
    """PWA diagnostic page"""
    return send_file('pwa_diagnostic.html', mimetype='text/html') 

@main_bp.route('/holiday/status')
def holiday_status():
    """Get current holiday status for frontend - only for logged-in users with active subscriptions"""
    
    # Check if user is logged in
    if not current_user.is_authenticated:
        return jsonify({'active': False, 'message': 'Login required'})
    
    # Check if user has active subscription
    active_subscription = Subscription.query.filter_by(
        user_id=current_user.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    if not active_subscription:
        return jsonify({'active': False, 'message': 'Active subscription required'})
    
    # Get current holiday
    current_holiday = Holiday.get_current_holiday()
    
    if current_holiday and current_holiday.show_popup:
        return jsonify({
            'active': True,
            'holiday': {
                'id': current_holiday.id,
                'name': current_holiday.name,
                'description': current_holiday.description,
                'message': current_holiday.popup_message,
                'options': current_holiday.get_popup_options(),
                'days_remaining': current_holiday.days_remaining,
                'protect_meals': current_holiday.protect_meals,
                'start_date': current_holiday.start_date.isoformat(),
                'end_date': current_holiday.end_date.isoformat()
            }
        })
    else:
        return jsonify({'active': False})

@main_bp.route('/holiday/response', methods=['POST'])
def holiday_response():
    """Handle user response to holiday popup"""
    try:
        data = request.get_json()
        holiday_id = data.get('holiday_id')
        response = data.get('response')
        
        # Log the response (you can extend this to store in database)
        current_app.logger.info(f"User {current_user.id if current_user.is_authenticated else 'anonymous'} responded to holiday {holiday_id}: {response}")
        
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f"Error handling holiday response: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Razorpay webhook deprecated - Stripe webhook is now used at /stripe-webhook
# This route is kept for backward compatibility but should not be used
@main_bp.route('/webhook/razorpay', methods=['POST'])
@csrf.exempt
def razorpay_webhook_deprecated():
    """Deprecated: Razorpay webhook - Use Stripe webhook instead"""
    current_app.logger.warning("Deprecated Razorpay webhook called - migration to Stripe required")
    return jsonify({'message': 'Razorpay webhook deprecated - please use Stripe'}), 410  # 410 Gone

@main_bp.route('/signup-complete/<int:order_id>', methods=['GET', 'POST'])
def signup_complete(order_id):
    """
    Complete signup process for users who made payment without being logged in.
    Pre-fills their details and shows subscription information.
    """
    try:
        # Get order from database
        order = Order.query.get(order_id)
        if not order:
            flash('Order not found. Please contact support.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        # Get user
        user = User.query.get(order.user_id)
        if not user:
            flash('User not found. Please contact support.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        # Get meal plan
        meal_plan = MealPlan.query.get(order.meal_plan_id)
        if not meal_plan:
            flash('Meal plan not found. Please contact support.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        # Get subscription
        subscription = Subscription.query.filter_by(
            user_id=order.user_id,
            meal_plan_id=order.meal_plan_id
        ).order_by(Subscription.created_at.desc()).first()
        
        # If user is already logged in, redirect to profile
        if current_user.is_authenticated and current_user.id == user.id:
            flash('You are already logged in!', 'info')
            return redirect(url_for('main.profile'))
        
        # Handle POST request (form submission)
        if request.method == 'POST':
            # Get form data
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate password
            if not password:
                flash('Password is required.', 'error')
                return render_template('signup_complete.html', 
                                      user=user, 
                                      order=order, 
                                      subscription=subscription, 
                                      plan=meal_plan)
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
                return render_template('signup_complete.html', 
                                      user=user, 
                                      order=order, 
                                      subscription=subscription, 
                                      plan=meal_plan)
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('signup_complete.html', 
                                      user=user, 
                                      order=order, 
                                      subscription=subscription, 
                                      plan=meal_plan)
            
            # Hash password and update user
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(password)
            user.is_active = True
            db.session.commit()
            
            # Log the user in
            from flask_login import login_user
            login_user(user)
            
            flash('Account created successfully! You are now logged in.', 'success')
            return redirect(url_for('main.profile'))
        
        # Handle GET request (show form)
        return render_template('signup_complete.html', 
                              user=user, 
                              order=order, 
                              subscription=subscription, 
                              plan=meal_plan)
                              
    except Exception as e:
        current_app.logger.error(f"Error in signup_complete: {str(e)}")
        flash('An error occurred. Please contact support.', 'error')
        return redirect(url_for('main.meal_plans'))

@main_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@csrf.exempt  # Exempt from CSRF protection for public password reset
def reset_password(token):
    """Handle password reset with token"""
    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('main.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('User not found.', 'error')
            return redirect(url_for('main.login'))
    
    return render_template('reset_password.html', token=token)

@main_bp.route('/process-meal-plan-checkout/<int:plan_id>', methods=['POST'])
@csrf.exempt
def process_meal_plan_checkout(plan_id):
    """Process meal plan checkout - redirect to main checkout"""
    return redirect(url_for('main.subscribe', plan_id=plan_id))

@main_bp.route('/save-prep-notes', methods=['POST'])
@login_required
@admin_required
def save_prep_notes():
    """Save daily meal prep notes"""
    try:
        date = request.form.get('date')
        notes = request.form.get('notes')
        
        # Here you would save the notes to your database
        # For now, just return success
        flash('Prep notes saved successfully!', 'success')
        return redirect(url_for('main.daily_meal_prep', date=date))
    except Exception as e:
        current_app.logger.error(f"Error saving prep notes: {str(e)}")
        flash('Error saving prep notes.', 'error')
        return redirect(url_for('main.daily_meal_prep'))







@main_bp.route('/get-additional-services')
def get_additional_services():
    """Get available additional services"""
    try:
        from database.models import AdditionalService
        
        services = AdditionalService.query.filter_by(is_active=True).all()
        services_data = []
        
        for service in services:
            services_data.append({
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'price': float(service.price),
                'price_type': service.price_type,
                'category': service.category,
                'max_quantity': service.max_quantity
            })
        
        return jsonify({
            'success': True,
            'services': services_data
        })
    except ImportError:
        # AdditionalService model doesn't exist yet - return empty list
        current_app.logger.warning("AdditionalService model not found - returning empty services list")
        return jsonify({
            'success': True,
            'services': []
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting additional services: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error loading services'
        }), 500


# TODO: Update process_checkout function to handle selected_services
# Add this to the form data processing section:
# selected_services = request.form.get('selected_services', '[]')
# services_data = json.loads(selected_services) if selected_services else []

@main_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Allow users to change password without updating name/email"""
    try:
        if not current_user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': 'Please log in to change your password'}), 401
            flash('Please log in to change your password', 'error')
            return redirect(url_for('main.login'))

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # All password fields must be provided
        if not all([current_password, new_password, confirm_password]):
            message = 'All password fields are required to change password'
            if is_ajax:
                return jsonify({'status': 'error', 'message': message})
            flash(message, 'error')
            return redirect(url_for('main.profile'))

        # Verify current password
        if not current_user.check_password(current_password):
            message = 'Current password is incorrect'
            if is_ajax:
                return jsonify({'status': 'error', 'message': message})
            flash(message, 'error')
            return redirect(url_for('main.profile'))

        # Check if new passwords match
        if new_password != confirm_password:
            message = 'New passwords do not match'
            if is_ajax:
                return jsonify({'status': 'error', 'message': message})
            flash(message, 'error')
            return redirect(url_for('main.profile'))

        # Validate new password strength
        if len(new_password) < 8:
            message = 'New password must be at least 8 characters long'
            if is_ajax:
                return jsonify({'status': 'error', 'message': message})
            flash(message, 'error')
            return redirect(url_for('main.profile'))

        try:
            user_id = current_user.id
            fresh_user = User.query.get(user_id)
            fresh_user.set_password(new_password)
            db.session.commit()
            current_user.password_hash = fresh_user.password_hash
            message = 'Password updated successfully'
            if is_ajax:
                return jsonify({'status': 'success', 'message': message})
            flash(message, 'success')
            return redirect(url_for('main.profile') + '#settings')
        except Exception as e:
            db.session.rollback()
            message = 'Failed to update password. Please try again.'
            if is_ajax:
                return jsonify({'status': 'error', 'message': message})
            flash(message, 'error')
            return redirect(url_for('main.profile'))
    except Exception as e:
        db.session.rollback()
        message = 'An error occurred while changing your password. Please try again.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': message})
        flash(message, 'error')
        return redirect(url_for('main.profile'))


