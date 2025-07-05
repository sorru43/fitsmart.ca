from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.models import db, User, MealPlan, Order, Subscription, BlogPost, DeliveryLocation, State, City, Area, CouponCode, CouponUsage
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
from utils.email_utils import send_password_reset_email, send_contact_notification
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
                {'title': 'How HealthyRizz Works', 'description': 'Choose your plan, connect with a nutrition expert, get chef-prepared meals delivered, and transform your lifestyle!', 'youtube_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'thumbnail_url': '/static/images/healthy-meal-bowl.jpg'},
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
            'company_name': 'HealthyRizz',
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
                def __init__(self, name, description, price_weekly, trial_price, calories, protein, fat, carbs, is_popular=False):
                    self.name = name
                    self.description = description
                    self.price_weekly = price_weekly
                    self.trial_price = trial_price
                    self.calories = calories
                    self.protein = protein
                    self.fat = fat
                    self.carbs = carbs
                    self.is_popular = is_popular
                    self.id = 1
                    self.is_active = True
                    self.available_for_trial = True
            
            meal_plans = [
                MockMealPlan("Balanced Diets office", "Fresh vegetarian meals packed with nutrition", 750, 200, 1600, 80, 50, 180, True),
                MockMealPlan("Balanced Diet Plan", "A well-balanced diet with all essential nutrients", 999, 200, 1800, 120, 60, 200, True),
                MockMealPlan("High Protein Diet", "High Protein diets, special for whom who want natural protein from daily foods", 1200, 250, 100, 100, 100, 100, True)
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
        
        # Create template context with proper CSRF handling
        template_context = {
            'faqs': faqs or [],
            'hero_slides': hero_slides or [],
            'videos': videos or [],
            'team_members': team_members or [],
            'meal_plans': meal_plans or [],
            'full_width_sections': full_width_sections or [],
            'site_settings': site_settings or {},
            'now': datetime.now()
        }
        
        # Ensure site_settings has ALL the required defaults for the template
        essential_defaults = {
            'site_logo': '/static/images/logo_20250629_170145_black_bg.gif',
            'hero_subtitle': 'In Supervision Of Nutrition Experts',
            'company_name': 'HealthyRizz',
            'company_tagline': 'Healthy Meal Delivery',
            'contact_phone': '8054090043',
            'contact_email': 'healthyrizz.in@gmail.com',
            'company_address': 'Ludhiana, Punjab, India',
            'facebook_url': 'https://facebook.com/healthyrizz',
            'instagram_url': 'https://instagram.com/healthyrizz.india',
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
            <title>HealthyRizz - Welcome</title>
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
                <h1>Welcome to HealthyRizz!</h1>
                <p>You have successfully logged in to your account.</p>
                
                <div class="nav">
                    <a href="/profile">👤 Profile</a>
                    <a href="/meal-plans">🥗 Meal Plans</a>
                    <a href="/about">ℹ️ About</a>
                    <a href="/logout">🚪 Logout</a>
                </div>
                
                <div class="status">
                    ✨ Your HealthyRizz journey starts here!<br>
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
            <title>About Us - HealthyRizz</title>
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
                <h1>About HealthyRizz</h1>
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
    from contact_forms import MultiPurposeContactForm
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
    """Meal plans page with bulletproof error handling"""
    try:
        plan_type = request.args.get('type')
        breakfast = request.args.get('breakfast')
        trial_only = request.args.get('trial_only')
        search = request.args.get('search')
        
        # Start with all active plans - with error handling
        try:
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
        except Exception as db_error:
            current_app.logger.warning(f"Database query failed: {db_error}")
            plans = []
        
        current_app.logger.info(f"Meal plans loaded successfully: {len(plans)} plans")
        
        return render_template('meal_plans.html', 
                             plan_type=plan_type, 
                             plans=plans,
                             now=datetime.now())
                             
    except Exception as e:
        current_app.logger.error(f"Error in meal_plans route: {str(e)}")
        
        # Fallback: Return a beautiful error page with working navigation
        fallback_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Meal Plans - HealthyRizz</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
                .error-container { background: white; border-radius: 8px; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .nav-links { display: flex; gap: 20px; justify-content: center; margin: 30px 0; flex-wrap: wrap; }
                .nav-links a { color: #007bff; text-decoration: none; padding: 12px 20px; background: #e9ecef; border-radius: 5px; transition: all 0.3s; }
                .nav-links a:hover { background: #007bff; color: white; transform: translateY(-2px); }
                h1 { color: #28a745; margin-bottom: 20px; }
                .icon { font-size: 3rem; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="icon">🥗</div>
                <h1>Our Meal Plans</h1>
                <p>We're currently updating our meal plan database to serve you better.</p>
                <p>Please check back soon for our delicious and nutritious meal options!</p>
                <div class="nav-links">
                    <a href="/">🏠 Home</a>
                    <a href="/about">📖 About</a>
                    <a href="/contact">📞 Contact</a>
                    <a href="/profile">👤 Profile</a>
                </div>
            </div>
        </body>
        </html>
        """
        return fallback_html, 200

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
    """User profile page with enhanced order and payment history"""
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
        
        # Get user's order history (all orders) - SIMPLIFIED QUERY
        try:
            orders = Order.query.filter(
                Order.user_id == current_user.id
            ).order_by(Order.created_at.desc()).all()
            current_app.logger.info(f"Found {len(orders)} orders for user {current_user.id}")
        except Exception as order_error:
            current_app.logger.error(f"Error querying orders: {str(order_error)}")
            orders = []
        
        # Get recent orders (last 10) with meal plan info
        recent_orders = []
        for order in orders[:10]:
            try:
                # Try to get meal plan name safely
                meal_plan_name = 'N/A'
                if hasattr(order, 'meal_plan') and order.meal_plan:
                    meal_plan_name = order.meal_plan.name
                elif hasattr(order, 'meal_plan_id') and order.meal_plan_id:
                    # Try to get meal plan by ID
                    meal_plan = MealPlan.query.get(order.meal_plan_id)
                    if meal_plan:
                        meal_plan_name = meal_plan.name
            except Exception as e:
                current_app.logger.warning(f"Error getting meal plan name for order {order.id}: {str(e)}")
                meal_plan_name = 'N/A'
                
            order_data = {
                'id': order.id,
                'amount': order.amount,
                'status': order.status,
                'payment_status': order.payment_status,
                'created_at': order.created_at,
                'meal_plan_name': meal_plan_name
            }
            recent_orders.append(order_data)
        
        # Get payment history from orders
        payment_history = []
        for order in orders:
            if order.payment_status and order.payment_id:
                try:
                    payment_history.append({
                        'order_id': order.id,
                        'payment_id': order.payment_id,
                        'amount': order.amount,
                        'status': order.payment_status,
                        'date': order.created_at,
                        'subscription_id': None,
                        'meal_plan_name': 'N/A'
                    })
                except Exception as e:
                    current_app.logger.warning(f"Error processing payment history for order {order.id}: {str(e)}")
        
        # Calculate total spent
        total_spent = sum(order.amount for order in orders if order.payment_status == 'completed')
        
        # Get subscription statistics
        total_subscriptions = len(active_subscriptions) + len(paused_subscriptions) + len(canceled_subscriptions)
        
        # Remove delivery processing completely to avoid JSON error
        subscription_deliveries = {}
        
        current_app.logger.info(f"Profile data loaded successfully for {current_user.email}")
        current_app.logger.info(f"Found {len(orders)} orders, {len(payment_history)} payments, {total_subscriptions} subscriptions")
        
        return render_template('profile.html', 
                             user=current_user,
                             active_subscriptions=active_subscriptions,
                             paused_subscriptions=paused_subscriptions,
                             canceled_subscriptions=canceled_subscriptions,
                             subscription_deliveries=subscription_deliveries,
                             orders=recent_orders,
                             payment_history=payment_history,
                             total_spent=total_spent,
                             total_subscriptions=total_subscriptions,
                             now=datetime.now())
                             
    except Exception as e:
        current_app.logger.error(f"Error in profile route: {str(e)}")
        current_app.logger.error(f"Error type: {type(e).__name__}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Return a working profile page with tabs even if there's an error
        return render_template('profile_working.html', 
                             user=current_user,
                             orders=[],
                             payment_history=[],
                             total_spent=0,
                             total_subscriptions=0,
                             now=datetime.now())

@main_bp.route('/profile/update', methods=['POST'])
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
    try:
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please provide a valid email address.', 'error')
            return redirect(url_for('main.index'))
        
        # Check if already subscribed
        existing_subscription = Newsletter.query.filter_by(email=email).first()
        if existing_subscription:
            flash('You are already subscribed to our newsletter!', 'info')
            return redirect(url_for('main.index'))
        
        # Create new subscription
        newsletter = Newsletter(email=email)
        db.session.add(newsletter)
        db.session.commit()
        
        current_app.logger.info(f'New newsletter subscription: {email}')
        flash('Thank you for subscribing to our newsletter!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Newsletter subscription error: {str(e)}')
        flash('An error occurred while subscribing. Please try again.', 'error')
    
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
    
    # Get frequency from URL params or default to weekly
    frequency = request.args.get('frequency', 'weekly')
    
    # Calculate prices with GST
    base_price = float(meal_plan.price_weekly if frequency == 'weekly' else meal_plan.price_monthly)
    gst_rate = 0.05
    gst_amount = base_price * gst_rate
    total_price = base_price + gst_amount

    # Always calculate both weekly and monthly GST/total for template
    weekly_gst = float(meal_plan.price_weekly) * gst_rate
    weekly_total = float(meal_plan.price_weekly) + weekly_gst
    monthly_gst = float(meal_plan.price_monthly) * gst_rate
    monthly_total = float(meal_plan.price_monthly) + monthly_gst

    # Create form for checkout
    form = CheckoutForm()

    # Get current user data for pre-filling if logged in
    user_data = None
    if current_user.is_authenticated:
        user_data = {
            'name': current_user.name or current_user.username,
            'email': current_user.email,
            'phone': current_user.phone,
            'address': current_user.address,
            'city': current_user.city,
            'state': current_user.state,
            'postal_code': current_user.postal_code
        }

    return render_template('checkout.html', 
                         meal_plan=meal_plan,
                         form=form,
                         frequency=frequency,
                         with_breakfast=with_breakfast,
                         base_price=base_price,
                         gst_amount=gst_amount,
                         total_price=total_price,
                         weekly_gst=weekly_gst,
                         weekly_total=weekly_total,
                         monthly_gst=monthly_gst,
                         monthly_total=monthly_total,
                         user_data=user_data)

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
                'name': subscription.user.name,  # Use name instead of username
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
        applied_coupon_code = request.form.get('applied_coupon_code')
        coupon_discount = request.form.get('coupon_discount', '0')
        
        # Validate required fields
        if not all([plan_id, frequency, customer_name, customer_email, customer_phone, 
                   customer_address, customer_city, customer_state, customer_pincode]):
            return jsonify({
                'success': False,
                'error': 'Please fill in all required fields.'
            }), 400
        
        # Get meal plan
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
        # Calculate price with GST
        base_price = float(meal_plan.price_weekly if frequency == 'weekly' else meal_plan.price_monthly)
        gst_amount = base_price * 0.05  # 5% GST
        subtotal = base_price + gst_amount
        
        # Apply coupon discount if provided
        discount_amount = float(coupon_discount) if coupon_discount else 0
        total_price = max(0, subtotal - discount_amount)
        
        # Check if we're in development mode with test keys
        razorpay_key = get_razorpay_key()
        if razorpay_key == 'rzp_test_default_key_id':
            # Development mode - return mock response
            logger.info("Development mode detected - returning mock Razorpay response")
            return jsonify({
                'success': True,
                'key': razorpay_key,
                'order_id': f'order_test_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'amount': int(total_price * 100),
                'currency': 'INR',
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
                'customer_pincode': customer_pincode,
                'applied_coupon': applied_coupon_code,
                'coupon_discount': str(discount_amount)
            }
        )
        
        if not order_data:
            logger.error("Failed to create Razorpay order")
            return jsonify({
                'success': False,
                'error': 'Error creating payment order. Please try again.'
            }), 500
        
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
            'success': True,
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
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your order. Please try again.'
        }), 500

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
        
        # Check if we're in development mode
        if razorpay_order_id.startswith('order_test_'):
            logger.info("Development mode detected - skipping payment verification")
            # Create mock subscription for development
            try:
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
                db.session.flush()  # Get subscription ID
                
                # Create order record for ALL successful payments (development mode)
                order = Order(
                    user_id=user.id,
                    meal_plan_id=order_data['notes']['plan_id'],
                    amount=float(order_data['amount']) / 100,
                    status='confirmed',
                    payment_status='captured',
                    payment_id=f'test_payment_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    order_id=razorpay_order_id
                )
                db.session.add(order)
                db.session.flush()  # Get order ID
                
                # Link subscription to order
                subscription.order_id = order.id
                
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
                
                flash('Your subscription has been created successfully! (Development Mode)', 'success')
                return redirect(url_for('main.checkout_success', order_id=order.id))
                
            except Exception as e:
                logger.error(f"Error creating development subscription: {str(e)}")
                db.session.rollback()
                flash('An error occurred while creating your subscription. Please contact support.', 'error')
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
        db.session.flush()  # Get subscription ID
        
        # Create order record for ALL successful payments (not just coupon usage)
        order = Order(
            user_id=user.id,
            meal_plan_id=order_data['notes']['plan_id'],
            amount=float(order_data['amount']) / 100,
            status='confirmed',
            payment_status='captured',
            payment_id=razorpay_payment_id,
            order_id=razorpay_order_id
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Link subscription to order
        subscription.order_id = order.id
        db.session.flush()
        
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
        return redirect(url_for('main.checkout_success', order_id=order.id))
        
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        flash('An error occurred while processing your payment. Please contact support.', 'error')
        return redirect(url_for('main.meal_plans'))

@main_bp.route('/checkout-success')
def checkout_success():
    """
    Handle successful checkout using order_id parameter.
    """
    try:
        # Get order_id from URL parameter
        order_id = request.args.get('order_id')
        
        if not order_id:
            # Fallback: try to get from session (for backward compatibility)
            checkout_data = session.get('checkout_data')
            checkout_session_id = session.get('checkout_session_id')
            
            # Also check for razorpay_order session data
            razorpay_order = session.get('razorpay_order')
            
            if not checkout_data and not razorpay_order:
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
            
            # Get user ID from session
            user_id = session.get('user_id')
            
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
                order = Order(
                    user_id=user_id,
                    meal_plan_id=plan_id,
                    amount=checkout_data.get('price', meal_plan.get_price_weekly()),
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
            
            # Show success page
            return render_template('checkout_success.html', 
                                  subscription=subscription, 
                                  plan=meal_plan,
                                  order=order)
        
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
        
        # Show success page
        return render_template('checkout_success.html', 
                              order=order,
                              subscription=subscription, 
                              plan=meal_plan,
                              user=user)
                              
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
    return render_template('shipping_delivery_policy.html')

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
def validate_coupon():
    """Validate coupon code and return discount information"""
    try:
        # Log the request for debugging
        current_app.logger.info(f"Coupon validation request: {request.get_json()}")
        
        data = request.get_json()
        if not data:
            current_app.logger.error("No JSON data received")
            return jsonify({'valid': False, 'message': 'Invalid request data'})
        
        coupon_code = data.get('coupon_code', '').strip().upper()
        order_amount = data.get('amount', 0)
        
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
            return jsonify({'valid': False, 'message': f'Minimum order amount required: ₹{min_order}'})
        
        # Check if user has already used this coupon (if single use)
        if coupon.is_single_use and current_user.is_authenticated:
            existing_usage = CouponUsage.query.filter_by(
                user_id=current_user.id,
                coupon_id=coupon.id
            ).first()
            
            if existing_usage:
                current_app.logger.warning(f"User already used coupon: {current_user.id} - {coupon_code}")
                return jsonify({'valid': False, 'message': 'You have already used this coupon'})
        
        # Calculate discount based on coupon type
        discount_amount = coupon.calculate_discount(order_amount)
        
        # Prepare response with correct field names
        response_data = {
            'valid': True,
            'message': f'Coupon applied! {coupon.discount_value}% discount',
            'discount_percentage': float(coupon.discount_value) if coupon.discount_type == 'percent' else None,
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
        return jsonify({'valid': False, 'message': 'Error validating coupon'})

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

@main_bp.route('/webhook/razorpay', methods=['POST'])
def razorpay_webhook():
    import hmac
    import hashlib
    import json
    from flask import current_app

    # Set your webhook secret here (store securely in production!)
    webhook_secret = 'javnWRC_mZFz6ub'
    payload = request.data
    signature = request.headers.get('X-Razorpay-Signature')

    # Verify signature
    expected_signature = hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        current_app.logger.warning("Razorpay webhook signature mismatch!")
        return "Invalid signature", 400

    event = request.get_json()
    event_type = event.get('event')
    payload_data = event.get('payload', {})

    # Handle payment captured event
    if event_type == 'payment.captured':
        payment_entity = payload_data.get('payment', {}).get('entity', {})
        razorpay_order_id = payment_entity.get('order_id')
        payment_id = payment_entity.get('id')
        amount = payment_entity.get('amount') / 100  # Convert to rupees

        # Find your order in DB
        order = Order.query.filter_by(order_id=razorpay_order_id).first()
        if order:
            # Idempotency: Only update if not already captured
            if order.payment_status != 'captured':
                order.payment_status = 'captured'
                order.payment_id = payment_id
                order.status = 'confirmed'
                
                # Create subscription for this order
                from database.models import Subscription, SubscriptionStatus, SubscriptionFrequency
                
                # Check if subscription already exists for this order
                existing_subscription = Subscription.query.filter_by(
                    user_id=order.user_id,
                    meal_plan_id=order.meal_plan_id,
                    order_id=order.id
                ).first()
                
                if not existing_subscription:
                    # Get meal plan to determine frequency and price
                    meal_plan = MealPlan.query.get(order.meal_plan_id)
                    if meal_plan:
                        # Determine frequency based on amount (you may need to adjust this logic)
                        # For now, assume weekly if amount matches weekly price, otherwise monthly
                        frequency = SubscriptionFrequency.WEEKLY
                        if meal_plan.price_monthly and abs(order.amount - float(meal_plan.price_monthly)) < 1:
                            frequency = SubscriptionFrequency.MONTHLY
                        
                        # Create subscription
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
                        current_app.logger.info(f"Created subscription {subscription.id} for order {order.id}")
                    else:
                        current_app.logger.error(f"Meal plan not found for order {order.id}")
                else:
                    current_app.logger.info(f"Subscription already exists for order {order.id}")
                
                db.session.commit()
                current_app.logger.info(f"Order {order.id} marked as paid and subscription created via webhook.")
            else:
                current_app.logger.info(f"Order {order.id} already marked as paid.")
        else:
            current_app.logger.warning(f"No order found for Razorpay order_id {razorpay_order_id}")

    # You can handle other event types similarly
    current_app.logger.info(f"Webhook event received: {event_type}")
    return "OK", 200

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
