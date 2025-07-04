"""
Script to add the price_trial column to the MealPlan table.
"""
import os
import sys
from app import create_app, db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add price_trial column to the meal_plan table"""
    # Create the Flask app with context
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'meal_plan' 
                AND column_name = 'price_trial'
            """)).fetchone()
            
            if result:
                logger.info("price_trial column already exists in meal_plan table")
                return
            
            # Add the price_trial column to the table
            db.session.execute(db.text("""
                ALTER TABLE meal_plan 
                ADD COLUMN price_trial NUMERIC(10, 2) DEFAULT 14.99
            """))
            
            # Make sure all existing meal plans have the default price
            db.session.execute(db.text("""
                UPDATE meal_plan
                SET price_trial = 14.99
                WHERE price_trial IS NULL
            """))
            
            db.session.commit()
            logger.info("Successfully added price_trial column to meal_plan table")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding price_trial column: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    run_migration()