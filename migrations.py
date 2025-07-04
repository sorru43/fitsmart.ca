"""
Database migration script for HealthyRizz meal delivery application.
This script ensures database tables exist and adds new columns needed for Stripe integration.
"""

import os
import logging
import sys
from sqlalchemy import text, inspect

# Set up proper logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except ImportError:
    logger.warning("python-dotenv not installed. Environment variables may not be properly loaded.")

# Explicitly set SQLALCHEMY_DATABASE_URI from DATABASE_URL if available
database_url = os.environ.get('DATABASE_URL')
if database_url:
    os.environ['SQLALCHEMY_DATABASE_URI'] = database_url
    logger.info(f"Set SQLALCHEMY_DATABASE_URI from DATABASE_URL")
else:
    # Check if we have individual PostgreSQL environment variables
    pg_host = os.environ.get('PGHOST')
    pg_user = os.environ.get('PGUSER')
    pg_password = os.environ.get('PGPASSWORD')
    pg_db = os.environ.get('PGDATABASE')
    pg_port = os.environ.get('PGPORT', '5432')
    
    if pg_host and pg_user and pg_password and pg_db:
        database_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        os.environ['SQLALCHEMY_DATABASE_URI'] = database_url
        logger.info("Set SQLALCHEMY_DATABASE_URI from individual PostgreSQL environment variables")
    else:
        logger.error("No database connection information found in environment variables!")
        logger.error("Please set DATABASE_URL or the PostgreSQL environment variables.")
        sys.exit(1)

# Import app after setting environment variables
from app import db, create_app

# Create app instance
app = create_app()

def ensure_tables_exist():
    """Create database tables if they don't exist"""
    try:
        with app.app_context():
            # Import all models to ensure they're registered with SQLAlchemy
            try:
                import models
                logger.info("Successfully imported models")
            except ImportError as e:
                logger.error(f"Error importing models: {str(e)}")
                logger.error("This is critical - models must be imported to create tables")
                return False
            
            # Check database connection
            try:
                # Test the connection
                db.engine.connect()
                logger.info("Successfully connected to database")
            except Exception as conn_err:
                logger.error(f"Failed to connect to database: {str(conn_err)}")
                logger.error("Check your DATABASE_URL or PostgreSQL environment variables")
                return False
            
            # Check if tables exist
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            logger.info(f"Existing tables: {existing_tables}")
            
            # Create tables if they don't exist
            if not existing_tables:
                logger.info("No tables found. Creating database tables...")
                db.create_all()
                
                # Verify tables were created
                inspector = inspect(db.engine)
                new_tables = inspector.get_table_names()
                if new_tables:
                    logger.info(f"✅ Created tables: {new_tables}")
                else:
                    logger.error("Failed to create tables!")
                    return False
            else:
                logger.info("✅ Database tables already exist")
                
            return True
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def add_stripe_customer_id_column():
    """Add stripe_customer_id column to User table"""
    try:
        # Check if the column already exists
        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('user')]
        
        if 'stripe_customer_id' in columns:
            logger.info("✅ stripe_customer_id column already exists in User table")
            return True
            
        logger.info("Adding stripe_customer_id column to User table...")
        with db.engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(100) NULL"
            ))
        logger.info("✅ Added stripe_customer_id column to User table")
        return True
    except Exception as e:
        logger.error(f"❌ Error adding stripe_customer_id column: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def add_vegetarian_days_column():
    """Add vegetarian_days column to subscriptions table"""
    try:
        # Check if the column already exists
        inspector = inspect(db.engine)
        if 'subscriptions' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('subscriptions')]
            
            if 'vegetarian_days' in columns:
                logger.info("✅ vegetarian_days column already exists in Subscription table")
                return True
        
        logger.info("Adding vegetarian_days column to Subscription table...")
        with db.engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS vegetarian_days VARCHAR(20) DEFAULT ''"
            ))
        logger.info("✅ Added vegetarian_days column to Subscription table")
        return True
    except Exception as e:
        logger.error(f"❌ Error adding vegetarian_days column: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
        
def add_price_trial_column():
    """Add price_trial column to subscriptions table for trial meal pricing"""
    try:
        # Check if the column already exists
        inspector = inspect(db.engine)
        if 'subscriptions' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('subscriptions')]
            
            if 'price_trial' in columns:
                logger.info("✅ price_trial column already exists in Subscription table")
                return True
        
        logger.info("Adding price_trial column to Subscription table...")
        with db.engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS price_trial NUMERIC(10, 2) NULL"
            ))
        logger.info("✅ Added price_trial column to Subscription table")
        return True
    except Exception as e:
        logger.error(f"❌ Error adding price_trial column: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def add_message_column_to_service_request():
    """Add message column to service_request table"""
    try:
        # Check if the column already exists
        inspector = inspect(db.engine)
        if 'service_request' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('service_request')]
            
            if 'message' in columns:
                logger.info("✅ message column already exists in ServiceRequest table")
                return True
        
        logger.info("Adding message column to ServiceRequest table...")
        with db.engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE service_request ADD COLUMN IF NOT EXISTS message TEXT NULL"
            ))
        logger.info("✅ Added message column to ServiceRequest table")
        return True
    except Exception as e:
        logger.error(f"❌ Error adding message column: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def run_migrations():
    """Run all migrations"""
    with app.app_context():
        logger.info("Starting database migrations...")
        
        # First ensure tables exist
        if ensure_tables_exist():
            # Then add columns
            add_stripe_customer_id_column()
            add_vegetarian_days_column()
            add_price_trial_column()
            add_message_column_to_service_request()
            
            # Report success
            logger.info("Database migrations completed!")
            return True
        else:
            logger.warning("⚠️ Skipping column migrations due to table creation failure")
            logger.error("Database migrations incomplete - table creation failed!")
            return False

if __name__ == "__main__":
    run_migrations()
