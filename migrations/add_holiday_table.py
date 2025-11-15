#!/usr/bin/env python3
"""
Migration script to add Holiday table
"""
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.models import db, Holiday

def add_holiday_table():
    """Add Holiday table to database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the holiday table
            db.create_all()
            
            # Check if table was created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'holiday' in tables:
                print("✅ Holiday table created successfully!")
                
                # Create a sample holiday for testing
                sample_holiday = Holiday(
                    name="Sample Holiday",
                    description="This is a sample holiday for testing purposes",
                    start_date=datetime.now().date(),
                    end_date=(datetime.now().date() + timedelta(days=7)),
                    is_active=True,
                    protect_meals=True,
                    show_popup=True,
                    popup_message="We're on holiday! Your meals are protected during this period.",
                    popup_options='["I understand", "Remind me later", "Contact support"]'
                )
                
                db.session.add(sample_holiday)
                db.session.commit()
                
                print("✅ Sample holiday created for testing!")
                return True
            else:
                print("❌ Holiday table was not created!")
                return False
                
        except Exception as e:
            print(f"❌ Error creating holiday table: {str(e)}")
            return False

if __name__ == "__main__":
    from datetime import timedelta
    add_holiday_table()
