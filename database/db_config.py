"""
Database configuration module for the application.
This module automatically detects and configures the database connection
based on available environment variables.
"""

import os

# Import the existing SQLAlchemy instance from models.py
from database.models import db

def configure_database(app):
    """
    Configure the database connection for the Flask application
    based on available environment variables.
    
    Args:
        app: Flask application instance
    """
    # Check for database URL first
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        # Build PostgreSQL URL from individual environment variables if DATABASE_URL is not set
        pg_host = os.environ.get('PGHOST')
        pg_user = os.environ.get('PGUSER')
        pg_password = os.environ.get('PGPASSWORD')
        pg_db = os.environ.get('PGDATABASE')
        pg_port = os.environ.get('PGPORT')
        
        if pg_host and pg_user and pg_password and pg_db:
            database_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
            print(f"Built DATABASE_URL from individual PostgreSQL environment variables")
    
    # If DATABASE_URL exists and starts with 'postgres://', replace with 'postgresql://'
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        print(f"Converted 'postgres://' to 'postgresql://' for SQLAlchemy compatibility")
    
    # Configure the application
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }
    
    # Initialize the database with the app
    db.init_app(app)
    
    return True