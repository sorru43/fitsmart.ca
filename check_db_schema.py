#!/usr/bin/env python3
"""
Script to check current database schema
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db

def check_schema():
    """Check current database schema"""
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            
            print("📋 Current Database Schema:")
            print("=" * 50)
            
            # Check order table
            if inspector.has_table('order'):
                order_columns = inspector.get_columns('order')
                print("\n📦 Order Table Columns:")
                for col in order_columns:
                    print(f"   - {col['name']}: {col['type']}")
            else:
                print("\n❌ Order table does not exist!")
            
            # Check subscriptions table
            if inspector.has_table('subscriptions'):
                subscription_columns = inspector.get_columns('subscriptions')
                print("\n📋 Subscriptions Table Columns:")
                for col in subscription_columns:
                    print(f"   - {col['name']}: {col['type']}")
            else:
                print("\n❌ Subscriptions table does not exist!")
            
            # Check user table
            if inspector.has_table('user'):
                user_columns = inspector.get_columns('user')
                print("\n👤 User Table Columns:")
                for col in user_columns:
                    print(f"   - {col['name']}: {col['type']}")
            else:
                print("\n❌ User table does not exist!")
            
            # Check meal_plan table
            if inspector.has_table('meal_plan'):
                meal_plan_columns = inspector.get_columns('meal_plan')
                print("\n🍽️ Meal Plan Table Columns:")
                for col in meal_plan_columns:
                    print(f"   - {col['name']}: {col['type']}")
            else:
                print("\n❌ Meal plan table does not exist!")
            
        except Exception as e:
            print(f"❌ Error checking schema: {str(e)}")

if __name__ == '__main__':
    check_schema() 