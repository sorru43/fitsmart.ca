import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Server configuration for URL generation
    SERVER_NAME = None  # Allow any hostname for VPS
    APPLICATION_ROOT = os.getenv('APPLICATION_ROOT', '/')
    PREFERRED_URL_SCHEME = os.getenv('PREFERRED_URL_SCHEME', 'http')

    # Basic Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'fitsmart-super-secret-key-2024-change-in-production')
    DEBUG = False  # Production mode
    VERSION = os.getenv('VERSION', '1.0.0')  # For cache busting
    
    # Database configuration
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "fitsmart.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }
    
    # Session configuration - Using Flask's built-in sessions instead of Flask-Session
    # SESSION_TYPE = 'filesystem'  # Commented out to disable Flask-Session
    # SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
    # SESSION_FILE_THRESHOLD = 500
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', '1800'))
    SESSION_REFRESH_EACH_REQUEST = False
    SESSION_USE_SIGNER = True
    
    # CSRF configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', SECRET_KEY)
    WTF_CSRF_TIME_LIMIT = 7200  # 2 hours
    WTF_CSRF_SSL_STRICT = os.getenv('WTF_CSRF_SSL_STRICT', 'False').lower() == 'true'
    WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token', 'X-XSRF-TOKEN']
    WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    WTF_CSRF_FIELD_NAME = 'csrf_token'
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_EXEMPT_VIEWS = []
    WTF_CSRF_EXEMPT_BLUEPRINTS = []
    
    # Mail configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
    
    # Stripe configuration (Primary payment gateway for Canadian market)
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')  # For webhook verification
    
    # Google OAuth configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    
    # Razorpay configuration (Deprecated - kept for backward compatibility)
    # Note: Razorpay is primarily for Indian market. Use Stripe for Canadian market.
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
    RAZORPAY_WEBHOOK_SECRET = os.getenv('RAZORPAY_WEBHOOK_SECRET', '')
    
    # AI Posting Agent configuration
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    AI_POSTING_FREQUENCY = os.getenv('AI_POSTING_FREQUENCY', 'daily')  # daily, weekly, biweekly, monthly
    AI_CONTENT_TYPES = os.getenv('AI_CONTENT_TYPES', 'blog_post,meal_plan_showcase').split(',')
    AI_AUTO_POSTING_ENABLED = os.getenv('AI_AUTO_POSTING_ENABLED', 'False').lower() == 'true'
    
    # Rate limiting
    RATELIMIT_DEFAULT = "500 per day, 100 per hour, 20 per minute"
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_STORAGE_OPTIONS = {
        'socket_timeout': 5,
        'socket_connect_timeout': 5,
        'retry_on_timeout': True
    }
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Login manager configuration
    LOGIN_VIEW = 'main.login'
    LOGIN_MESSAGE = 'Please log in to access this page.'
    LOGIN_MESSAGE_CATEGORY = 'info'
    REFRESH_VIEW = 'main.login'
    NEEDS_REFRESH_MESSAGE = 'Please login again to confirm your identity.'
    NEEDS_REFRESH_MESSAGE_CATEGORY = 'warning'
    SESSION_PROTECTION = 'strong'
    
    # Canadian specific settings
    CURRENCY = 'CAD'
    CURRENCY_SYMBOL = '$'
    DATE_FORMAT = '%Y-%m-%d'
    TIME_FORMAT = '%I:%M %p'  # 12-hour format with AM/PM
    PHONE_REGEX = r'^\+?1?\d{10}$'  # Canadian/US mobile number format
    PINCODE_REGEX = r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$'  # Canadian postal code format
    
    # Timezone configuration - Eastern Time (ET)
    TIMEZONE = 'America/Toronto'
    TIMEZONE_OFFSET = '-05:00'  # EST is UTC-5:00 (or EDT UTC-4:00)
    
    # Delivery Model Configuration (Canada)
    # Meals are delivered in the evening (one day before) for next-day consumption
    # Example: Meals for Wednesday are delivered Tuesday evening
    DELIVERY_MODEL = 'evening_before'  # 'evening_before' or 'same_day'
    DELIVERY_EVENING_START = '18:00'  # 6:00 PM - Start of evening delivery window
    DELIVERY_EVENING_END = '22:00'    # 10:00 PM - End of evening delivery window
    # Skip meal cutoff: Must skip by same day (meal consumption date) at 10:00 AM
    # Example: To skip Wednesday meals, must skip by Wednesday 10:00 AM
    # After 10 AM: Can mark for donation/no delivery to save delivery resources
    SKIP_MEAL_CUTOFF_TIME = '10:00'  # 10:00 AM cutoff time (same day)
    SKIP_MEAL_CUTOFF_DAYS_BEFORE = 0  # 0 = same day cutoff


# CSRF Configuration
WTF_CSRF_ENABLED = False