"""
Main application setup for Flask and SQLAlchemy
"""
import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory, make_response
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from extensions import db, migrate, login_manager, mail, limiter, csrf
from datetime import timedelta, datetime
# from flask_session import Session  # Commented out - using Flask's built-in sessions
from database.models import User, SiteSetting, Banner, Subscription, Order, MealPlan, Delivery, Newsletter, CouponCode, DeliveryLocation
from flask_wtf.csrf import CSRFError
from routes.main_routes import main_bp
from routes.admin_routes import admin_bp
from routes.admin_orders import admin_orders_bp
from routes_pwa import pwa_bp  # Import PWA blueprint
from commands import init_app as init_commands
from config import Config
from utils.filters import timeago, multiply_decimal
from utils.email_utils import send_email
import razorpay
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

# Load environment variables
load_dotenv()

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'
    
    # Add user loader
    @login_manager.user_loader
    def load_user(user_id):
        with app.app_context():
            return User.query.get(int(user_id))
    
    # Configure logging - reduce for production
    if app.config.get('DEBUG', False):
        logging.basicConfig(level=logging.INFO)  # Changed from DEBUG to INFO
    else:
        logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Changed from DEBUG to INFO
    
    # Initialize OAuth (Google) - after logger is configured
    try:
        from utils.google_oauth import init_oauth
        oauth, google = init_oauth(app)
        app.oauth = oauth
        app.google_oauth = google
        logger.info("Google OAuth initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize OAuth: {e}")
        app.oauth = None
        app.google_oauth = None
    
    # Add template context processor for current datetime in IST
    @app.context_processor
    def inject_now():
        try:
            from utils.timezone_utils import get_current_ist_time
            return {'now': get_current_ist_time()}
        except ImportError:
            # Fallback to UTC if timezone utils not available
            return {'now': datetime.utcnow()}

    @app.context_processor
    def inject_site_settings():
        """Inject all site settings into the template context"""
        try:
            settings = SiteSetting.query.all()
            # Convert to a dictionary for easy access in templates
            settings_dict = {setting.key: setting.value for setting in settings}
            
            # Add essential defaults if they don't exist
            essential_defaults = {
                'site_logo': '/static/images/logo white.png',
                'hero_subtitle': 'In Supervision Of Nutrition Experts',
                'company_name': 'FitSmart',
                'company_tagline': 'Healthy Meal Delivery',
                'contact_phone': '+1 (647) 573-2429',
                'contact_email': 'info@fitsmart.ca',
                'company_address': 'Canada',
                'facebook_url': 'https://facebook.com/fitsmart',
                'instagram_url': 'https://instagram.com/fitsmart.ca',
                'show_social_links': 'True',
                'show_fssai_badge': 'True',
                'show_hygiene_badge': 'True',
                'hygiene_badge_text': '100% Hygienic'
            }
            
            # Merge defaults with loaded settings
            for key, default_value in essential_defaults.items():
                if key not in settings_dict:
                    settings_dict[key] = default_value
            
            return {'site_settings': settings_dict}
        except Exception as e:
            # Log the error if the database isn't ready
            app.logger.error(f"Could not inject site settings: {e}")
            # Return essential defaults even if database fails
            return {'site_settings': {
                'site_logo': '/static/images/logo white.png',
                'hero_subtitle': 'In Supervision Of Nutrition Experts',
                'company_name': 'FitSmart',
                'company_tagline': 'Healthy Meal Delivery',
                'contact_phone': '+1 (647) 573-2429',
                'contact_email': 'info@fitsmart.ca',
                'company_address': 'Canada',
                'facebook_url': 'https://facebook.com/fitsmart',
                'instagram_url': 'https://instagram.com/fitsmart.ca',
                'show_social_links': 'True',
                'show_fssai_badge': 'True',
                'show_hygiene_badge': 'True',
                'hygiene_badge_text': '100% Hygienic'
            }}

    @app.context_processor
    def inject_active_banner():
        """Inject active banner into template context"""
        try:
            banner = Banner.get_active_banner()
            app.logger.debug(f"Active banner found: {banner.message if banner else 'None'}")
            return {'banner': banner}
        except Exception as e:
            app.logger.error(f"Error fetching active banner: {str(e)}")
            return {'banner': None}

    @app.context_processor
    def inject_csrf_token():
        """Inject CSRF token function into template context"""
        try:
            from flask_wtf.csrf import generate_csrf
            return {'csrf_token': generate_csrf}
        except Exception as e:
            app.logger.error(f"Error injecting CSRF token: {str(e)}")
            return {'csrf_token': lambda: 'dummy-csrf-token'}

    # Add custom filters
    app.jinja_env.filters['timeago'] = timeago
    app.jinja_env.filters['multiply_decimal'] = multiply_decimal

    # CSRF error handler
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('csrf_error.html', reason=e.description), 400
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(admin_orders_bp)
    
    # Import and register subscription management routes
    try:
        from routes.subscription_management_routes import subscription_mgmt_bp
        app.register_blueprint(subscription_mgmt_bp, url_prefix='/subscription')
    except ImportError:
        pass  # Skip if file doesn't exist yet
    
    # Import and register WhatsApp routes
    try:
        from routes.whatsapp_routes import whatsapp_bp
        app.register_blueprint(whatsapp_bp)
    except ImportError:
        pass  # Skip if file doesn't exist yet
    
    # Import and register WhatsApp admin routes
    try:
        from routes.admin_whatsapp_routes import admin_whatsapp_bp
        app.register_blueprint(admin_whatsapp_bp)
        logger.info(f"Registered blueprint: {admin_whatsapp_bp.name}")
    except Exception as e:
        logger.warning(f"Could not register admin_whatsapp blueprint: {e}")
        pass  # Skip if file doesn't exist or has errors
    
    # Import and register Email Campaign routes
    from routes.email_campaign_routes import email_campaign_bp
    app.register_blueprint(email_campaign_bp)
    
    app.register_blueprint(pwa_bp)  # Register PWA blueprint

    # Add direct favicon route as fallback
    @app.route('/favicon.ico')
    def favicon_fallback():
        """Serve favicon from static folder"""
        return send_from_directory('static', 'favicon.ico')

    @app.route('/service-worker.js')
    def service_worker():
        """Serve the service worker file"""
        response = make_response(send_from_directory('static/js', 'service-worker.js'))
        response.headers['Content-Type'] = 'application/javascript'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    @app.route('/manifest.json')
    def manifest():
        """Serve the manifest file"""
        response = make_response(send_from_directory('static', 'manifest.json'))
        response.headers['Content-Type'] = 'application/json'
        return response
    
    @app.route('/clear-service-worker')
    def clear_service_worker():
        """Serve the service worker clearing helper page"""
        return send_from_directory('.', 'force_clear_service_worker.html')
    
    @app.route('/clear-cache')
    def clear_cache():
        """Serve the cache clearing page"""
        return send_from_directory('.', 'clear-cache.html')
    
    # Register commands
    init_commands(app)

    # Stripe is initialized in utils/stripe_utils.py using environment variables

    def send_order_confirmation_email(subscription):
        """Send order confirmation email"""
        try:
            # Use the generic send_email function
            subject = "Order Confirmation - FitSmart"
            html_content = f"""
            <html>
            <body>
                <h2>Order Confirmation</h2>
                <p>Your order has been confirmed successfully!</p>
                <p>Subscription ID: {subscription.id}</p>
                <p>Status: {subscription.status}</p>
            </body>
            </html>
            """
            
            return send_email(
                to_email=subscription.user.email,
                from_email='no-reply@fitsmart.ca',
                subject=subject,
                html_content=html_content
            )
        except Exception as e:
            app.logger.error(f"Failed to send order confirmation email: {str(e)}")
            return False

    def send_payment_failure_email(subscription):
        """Send payment failure notification email"""
        try:
            # Use the generic send_email function
            subject = "Payment Failed - FitSmart"
            html_content = f"""
            <html>
            <body>
                <h2>Payment Failed</h2>
                <p>We're sorry, but your payment has failed.</p>
                <p>Subscription ID: {subscription.id}</p>
                <p>Please try again or contact support.</p>
            </body>
            </html>
            """
            
            return send_email(
                to_email=subscription.user.email,
                from_email='no-reply@fitsmart.ca',
                subject=subject,
                html_content=html_content
            )
        except Exception as e:
            app.logger.error(f"Failed to send payment failure email: {str(e)}")
            return False

    # Stripe webhook is handled in routes/main_routes.py

    @app.route('/profile/deliveries')
    @login_required
    def deliveries():
        user = current_user
        # Get user's active subscriptions
        subscriptions = Subscription.query.filter_by(user_id=user.id, status=SubscriptionStatus.ACTIVE).all()
        
        # Get all deliveries for these subscriptions
        deliveries = []
        for subscription in subscriptions:
            subscription_deliveries = Delivery.query.filter_by(subscription_id=subscription.id).order_by(Delivery.delivery_date.desc()).all()
            deliveries.extend(subscription_deliveries)
        
        return render_template('profile/deliveries.html', deliveries=deliveries)

    @app.route('/cart-checkout')
    @login_required
    def cart_checkout():
        user = current_user
        # Get user's cart items (if any)
        cart_items = []  # This would be implemented based on your cart system
        
        # Get available delivery locations
        states = DeliveryLocation.query.with_entities(DeliveryLocation.state).distinct().all()
        states = [state[0] for state in states if state[0]]
        
        return render_template('checkout.html', cart_items=cart_items, states=states)

    # Newsletter subscription route moved to main_routes.py

    @app.route('/checkout-success')
    def checkout_success():
        return render_template('checkout_success.html')

    @app.route('/checkout-cancel')
    def checkout_cancel():
        return render_template('checkout_cancel.html')



    @app.route('/order-confirmation/<int:order_id>')
    @login_required
    def order_confirmation(order_id):
        order = Order.query.get_or_404(order_id)
        if order.user_id != current_user.id:
            flash('You do not have permission to view this order.', 'error')
            return redirect(url_for('main.index'))
        return render_template('order_confirmation.html', order=order)
    
    # Add error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(401)
    def unauthorized(error):
        return redirect(url_for('main.index'))

    # Security headers middleware - FIX FOR PAYMENT BLOCKING
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Fixed CSP to allow CSS and other resources properly
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://www.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.tailwindcss.com https://fonts.gstatic.com https://unpkg.com https://cdn.jsdelivr.net; img-src 'self' data: https: blob:; connect-src 'self' https://api.stripe.com https://www.googleapis.com https://*.googleapis.com https://*.firebaseio.com https://*.firebaseapp.com; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com https://fonts.googleapis.com; object-src 'none'; media-src 'self'; frame-src 'self' https://js.stripe.com;"
        
        # Add cache control for static files to prevent caching issues
        if request.path.startswith('/static/'):
            # Add cache-busting parameter for CSS and JS files
            if request.path.endswith(('.css', '.js')):
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            else:
                # For other static files, allow caching but with shorter duration
                response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour
        
        return response

    # Password reset helper functions
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
            subject="Password Reset Request - FitSmart",
            sender=app.config.get("MAIL_DEFAULT_SENDER", "noreply@fitsmart.ca"),
            recipients=[to_email]
        )
        msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email.
'''
        with app.app_context():
            mail.send(msg)

    # @app.route('/reset-password/<token>', methods=['GET', 'POST'])
    # def reset_password(token):
    #     try:
    #         email = verify_password_reset_token(token)
    #         if not email:
    #             flash('The password reset link is invalid or has expired. Please request a new password reset.', 'error')
    #             return redirect(url_for('main.forgot_password'))
    #         
    #         if request.method == 'POST':
    #             password = request.form.get('password')
    #             confirm_password = request.form.get('confirm_password')
    #             
    #             if password != confirm_password:
    #                 flash('Passwords do not match.', 'error')
    #                 return render_template('reset_password.html', token=token)
    #             
    #             user = User.query.filter_by(email=email).first()
    #             if user:
    #                 user.set_password(password)
    #                 db.session.commit()
    #                 flash('Your password has been reset successfully.', 'success')
    #                 return redirect(url_for('main.login'))
    #             else:
    #                 flash('User not found.', 'error')
    #                 return redirect(url_for('main.login'))
    #         
    #         return render_template('reset_password.html', token=token)
    #     except Exception as e:
    #         app.logger.error(f"Error in reset_password route: {str(e)}")
    #         flash('An error occurred while resetting your password. Please try again.', 'error')
    #         return redirect(url_for('main.forgot_password'))

    # @app.route('/reset-password', methods=['GET', 'POST'])
    # def reset_password_no_token():
    #     """Handle access to reset-password without a token"""
    #     flash('Please use the forgot password link to request a password reset.', 'info')
    #     return redirect(url_for('main.forgot_password'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


