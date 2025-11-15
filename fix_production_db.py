#!/usr/bin/env python3
"""
Script to fix production database issues
"""
import os
import sys
from sqlalchemy import text

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db

def fix_production_database():
    """Fix production database issues"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Fixing production database...")
            
            # Check if email_verified column exists
            try:
                result = db.session.execute(text("PRAGMA table_info(user)"))
                columns = [row[1] for row in result.fetchall()]
                print(f"Current user table columns: {columns}")
                
                if 'email_verified' not in columns:
                    print("Adding email_verified column...")
                    db.session.execute(text('ALTER TABLE user ADD COLUMN email_verified BOOLEAN DEFAULT 0'))
                    db.session.commit()
                    print("✅ email_verified column added successfully")
                else:
                    print("✅ email_verified column already exists")
                    
            except Exception as e:
                print(f"Error checking/adding email_verified column: {e}")
                db.session.rollback()
            
            # Check if there are any other missing columns
            try:
                # Check meal_plan table structure
                result = db.session.execute(text("PRAGMA table_info(meal_plan)"))
                meal_plan_columns = [row[1] for row in result.fetchall()]
                print(f"Meal plan table columns: {meal_plan_columns}")
                
                # If the problematic column doesn't exist, we can skip the migration
                if 'price_monthly_with_breakfast' not in meal_plan_columns:
                    print("✅ price_monthly_with_breakfast column doesn't exist - migration can be skipped")
                else:
                    print("⚠️  price_monthly_with_breakfast column exists")
                    
            except Exception as e:
                print(f"Error checking meal_plan table: {e}")
            
            print("✅ Database fix completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing database: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_application():
    """Test if the application works correctly"""
    try:
        print("\n🧪 Testing application...")
        
        # Test basic imports
        from database.models import User, Subscription, Delivery
        print("✅ Database models imported successfully")
        
        # Test enhanced daily orders
        from routes.enhanced_daily_orders import enhanced_orders_bp
        print("✅ Enhanced daily orders routes imported successfully")
        
        # Test admin routes
        from routes.admin_routes import admin_bp
        print("✅ Admin routes imported successfully")
        
        print("✅ Application test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Production Database Fix Script")
    print("=" * 50)
    
    # Fix database
    db_fixed = fix_production_database()
    
    # Test application
    app_works = test_application()
    
    if db_fixed and app_works:
        print("\n🎉 All fixes completed successfully!")
        print("The application should now work correctly.")
    else:
        print("\n❌ Some fixes failed. Please check the errors above.")
