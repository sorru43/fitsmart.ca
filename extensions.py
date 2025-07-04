"""
Flask extensions for the application
"""
import os
import warnings
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

# Configure limiter - use memory storage for development, Redis for production
def create_limiter():
    # Check if we're in production (REDIS_URL is set and accessible)
    redis_url = os.environ.get('REDIS_URL')
    
    # Check for production environment (multiple ways)
    is_production = (
        os.environ.get('FLASK_ENV') == 'production' or
        os.environ.get('FLASK_DEBUG') == '0' or
        os.environ.get('FLASK_DEBUG') == 'False' or
        os.environ.get('DEBUG') == 'False' or
        os.environ.get('DEBUG') == '0'
    )
    
    # For now, always use memory storage to avoid Redis dependency
    try:
        return Limiter(
            key_func=get_remote_address,
            storage_uri="memory://"
        )
    except Exception as e:
        print(f"Warning: Rate limiter initialization failed ({e}), using dummy limiter")
        # For development, create a dummy limiter that doesn't actually limit
        class DummyLimiter:
            def __init__(self, app=None):
                self.app = app
                if app is not None:
                    self.init_app(app)
            
            def init_app(self, app):
                pass
            
            def limit(self, *args, **kwargs):
                def decorator(f):
                    return f
                return decorator
        
        return DummyLimiter()

limiter = create_limiter()

csrf = CSRFProtect()

# Configure login manager
login_manager.login_view = 'main.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
login_manager.refresh_view = 'main.login'
login_manager.needs_refresh_message = 'Please login again to confirm your identity.'
login_manager.needs_refresh_message_category = 'warning'
login_manager.session_protection = 'strong' 