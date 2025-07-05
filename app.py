"""
Main application setup for Flask and SQLAlchemy
"""
import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from dotenv import load_dotenv
from extensions import db, migrate, login_manager, mail, limiter, csrf
from datetime import timedelta, datetime
# from flask_session import Session  # Commented out - using Flask's built-in sessions
from database.models import User, SiteSetting, Banner, Subscription, Order
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
    
    # Add template context processor for current datetime
    @app.context_processor
    def inject_now():
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
    app.register_blueprint(pwa_bp)  # Register PWA blueprint
    
    # Add direct favicon route as fallback
    @app.route('/favicon.ico')
    def favicon_fallback():
        """Direct favicon route as fallback"""
        import os
        from flask import send_file
        favicon_path = os.path.join(app.root_path, 'static', 'favicon.ico')
        if os.path.exists(favicon_path):
            return send_file(favicon_path, mimetype='image/x-icon')
        else:
            # Return a simple 404 response
            return '', 404
    
    # Register commands
    init_commands(app)

    # Initialize Razorpay client
    razorpay_client = razorpay.Client(
        auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET'])
    )

    def send_order_confirmation_email(subscription):
        """Send order confirmation email"""
        try:
            # Use the generic send_email function
            subject = "Order Confirmation - HealthyRizz"
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
                from_email='no-reply@healthyrizz.in',
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
            subject = "Payment Failed - HealthyRizz"
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
                from_email='no-reply@healthyrizz.in',
                subject=subject,
                html_content=html_content
            )
        except Exception as e:
            app.logger.error(f"Failed to send payment failure email: {str(e)}")
            return False

    @app.route('/razorpay-webhook', methods=['POST'])
    @csrf.exempt
    def razorpay_webhook():
        """Handle Razorpay webhook events for payment status updates"""
        try:
            # Get webhook data
            webhook_data = request.get_json()
            if not webhook_data:
                app.logger.error('Webhook: No JSON data received')
                return jsonify({'error': 'No JSON data received'}), 400
            
            # Verify webhook signature
            signature = request.headers.get('X-Razorpay-Signature')
            if not signature:
                app.logger.error('Webhook: No signature found in headers')
                return jsonify({'error': 'No signature found'}), 400
                
            # Verify webhook signature
            try:
                razorpay_client.utility.verify_webhook_signature(
                    request.data,
                    signature,
                    app.config['RAZORPAY_WEBHOOK_SECRET']
                )
            except Exception as sig_error:
                app.logger.error(f'Webhook: Signature verification failed: {str(sig_error)}')
                return jsonify({'error': 'Invalid signature'}), 400
            
            # Handle different webhook events
            event_type = webhook_data.get('event')
            app.logger.info(f'Webhook: Received event: {event_type}')
            
            if event_type == 'payment.captured':
                payment_id = webhook_data['payload']['payment']['entity']['id']
                order_id = webhook_data['payload']['payment']['entity']['order_id']
                
                app.logger.info(f'Webhook: Payment captured - Payment ID: {payment_id}, Order ID: {order_id}')
                
                # Update subscription status
                subscription = Subscription.query.filter_by(payment_id=payment_id).first()
                if subscription:
                    subscription.status = 'active'
                    subscription.payment_status = 'captured'
                    subscription.updated_at = datetime.utcnow()
                    db.session.commit()
                    
                    app.logger.info(f'Webhook: Subscription {subscription.id} activated')
                    
                    # Send confirmation email
                    try:
                        send_order_confirmation_email(subscription)
                    except Exception as email_error:
                        app.logger.error(f'Webhook: Failed to send confirmation email: {str(email_error)}')
                else:
                    app.logger.warning(f'Webhook: No subscription found for payment ID: {payment_id}')
            
            elif event_type == 'payment.failed':
                payment_id = webhook_data['payload']['payment']['entity']['id']
                
                app.logger.info(f'Webhook: Payment failed - Payment ID: {payment_id}')
                
                # Update subscription status
                subscription = Subscription.query.filter_by(payment_id=payment_id).first()
                if subscription:
                    subscription.status = 'failed'
                    subscription.payment_status = 'failed'
                    subscription.updated_at = datetime.utcnow()
                    db.session.commit()
                    
                    app.logger.info(f'Webhook: Subscription {subscription.id} marked as failed')
                    
                    # Send failure notification
                    try:
                        send_payment_failure_email(subscription)
                    except Exception as email_error:
                        app.logger.error(f'Webhook: Failed to send failure email: {str(email_error)}')
                else:
                    app.logger.warning(f'Webhook: No subscription found for failed payment ID: {payment_id}')
            
            elif event_type == 'order.paid':
                order_id = webhook_data['payload']['order']['entity']['id']
                app.logger.info(f'Webhook: Order paid - Order ID: {order_id}')
                
                # Handle order.paid event if needed
                # This is typically handled by payment.captured, but good to have as backup
            
            else:
                app.logger.info(f'Webhook: Unhandled event type: {event_type}')
            
            return jsonify({'status': 'success'})
            
        except Exception as e:
            app.logger.error(f'Webhook error: {str(e)}')
            return jsonify({'error': 'Internal server error'}), 500

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
            subject="Password Reset Request - HealthyRizz",
            sender=app.config.get("MAIL_DEFAULT_SENDER", "noreply@healthyrizz.in"),
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
