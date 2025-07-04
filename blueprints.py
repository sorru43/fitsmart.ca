"""
Register all blueprints for the application
"""
from flask import Flask
from routes.main_routes import main_bp
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp

def register_blueprints(app: Flask):
    """Register all blueprints with the Flask application"""
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    
    # Import and register other blueprints here
    # from routes.main_routes import main  # Remove this line
    # app.register_blueprint(main)  # Remove this line 