import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ProductionConfig:
    """Production configuration for VPS Linux deployment"""
    
    # Basic Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required for production")
    
    DEBUG = False
    TESTING = False
    
    # Database configuration - PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required for production")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 20,
        "max_overflow": 30,
        "pool_timeout": 30,
        "pool_reset_on_return": "commit"
    }
    
    # Session configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_REFRESH_EACH_REQUEST = False
    SESSION_USE_SIGNER = True
    
    # CSRF configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', SECRET_KEY)
    WTF_CSRF_TIME_LIMIT = 7200  # 2 hours
    WTF_CSRF_SSL_STRICT = True
    WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token', 'X-XSRF-TOKEN']
    WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    WTF_CSRF_FIELD_NAME = 'csrf_token'
    WTF_CSRF_CHECK_DEFAULT = True
    
    # Mail configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
    MAIL_MAX_EMAILS = 100
    MAIL_ASCII_ATTACHMENTS = False
    MAIL_SUPPRESS_SEND = False
    
    # Stripe configuration (Primary payment gateway for Canadian market)
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    # Razorpay configuration (Deprecated - kept for backward compatibility)
    # Note: Razorpay is primarily for Indian market. Use Stripe for Canadian market.
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
    RAZORPAY_WEBHOOK_SECRET = os.getenv('RAZORPAY_WEBHOOK_SECRET', '')
    
    # Rate limiting - More restrictive for production
    RATELIMIT_DEFAULT = "1000 per day, 200 per hour, 30 per minute"
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_STORAGE_OPTIONS = {
        'socket_timeout': 5,
        'socket_connect_timeout': 5,
        'retry_on_timeout': True,
        'max_connections': 20
    }
    
    # File upload configuration
    UPLOAD_FOLDER = '/var/www/fitsmart/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Login manager configuration
    LOGIN_VIEW = 'main.login'
    LOGIN_MESSAGE = 'Please log in to access this page.'
    LOGIN_MESSAGE_CATEGORY = 'info'
    REFRESH_VIEW = 'main.login'
    NEEDS_REFRESH_MESSAGE = 'Please login again to confirm your identity.'
    NEEDS_REFRESH_MESSAGE_CATEGORY = 'warning'
    SESSION_PROTECTION = 'strong'
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self' https://api.stripe.com; frame-src https://js.stripe.com;"
    }
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/fitsmart/app.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Cache configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'fitsmart_'
    
    # Performance settings
    COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    
    # Canadian specific settings
    CURRENCY = 'CAD'
    CURRENCY_SYMBOL = '$'
    DATE_FORMAT = '%Y-%m-%d'
    TIME_FORMAT = '%I:%M %p'
    PHONE_REGEX = r'^\+?1?\d{10}$'
    PINCODE_REGEX = r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$'
    
    # Production specific settings
    PREFERRED_URL_SCHEME = 'https'
    SERVER_NAME = os.getenv('SERVER_NAME')
    
    # Backup configuration
    BACKUP_DIR = '/var/backups/fitsmart'
    BACKUP_RETENTION_DAYS = 30
    
    # Monitoring
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    SENTRY_ENVIRONMENT = 'production'
    SENTRY_TRACES_SAMPLE_RATE = 0.1
    
    # SSL/TLS settings
    SSL_REDIRECT = True
    SSL_REDIRECT_PERMANENT = True
    
    # Database backup
    DB_BACKUP_ENABLED = True
    DB_BACKUP_SCHEDULE = '0 2 * * *'  # Daily at 2 AM
    
    # Email rate limiting
    EMAIL_RATE_LIMIT = 100  # emails per hour
    EMAIL_RATE_LIMIT_WINDOW = 3600  # 1 hour
    
    # File cleanup
    CLEANUP_OLD_FILES = True
    CLEANUP_DAYS = 90  # Remove files older than 90 days
    
    # Health check
    HEALTH_CHECK_ENABLED = True
    HEALTH_CHECK_INTERVAL = 300  # 5 minutes 