import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "healthyrizz.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
    SESSION_FILE_THRESHOLD = 500
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', '1800'))
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_USE_SIGNER = True
    
    # CSRF configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', SECRET_KEY)
    WTF_CSRF_TIME_LIMIT = 7200  # 2 hours (increased from 1 hour)
    WTF_CSRF_SSL_STRICT = os.getenv('WTF_CSRF_SSL_STRICT', 'False').lower() == 'true'
    WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token']
    WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    WTF_CSRF_FIELD_NAME = 'csrf_token'
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_EXEMPT_VIEWS = []
    WTF_CSRF_EXEMPT_BLUEPRINTS = []
    WTF_CSRF_SSL_STRICT = False  # Set to True in production
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
    
    # Razorpay configuration
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
    RAZORPAY_WEBHOOK_SECRET = os.getenv('RAZORPAY_WEBHOOK_SECRET')  # For webhook verification
    
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
    
    # Indian specific settings
    CURRENCY = 'INR'
    CURRENCY_SYMBOL = '₹'
    DATE_FORMAT = '%d/%m/%Y'
    TIME_FORMAT = '%I:%M %p'  # 12-hour format with AM/PM
    PHONE_REGEX = r'^[6-9]\d{9}$'  # Indian mobile number format
    PINCODE_REGEX = r'^\d{6}$'  # Indian pincode format 
