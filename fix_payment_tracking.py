#!/usr/bin/env python3
"""
Script to fix payment tracking by updating database schema
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from database.models import Order, Subscription

def update_database_schema():
    """Update database schema for payment tracking"""
    with app.app_context():
        try:
            # Check if order_id column exists in subscription table
            inspector = db.inspect(db.engine)
            subscription_columns = [col['name'] for col in inspector.get_columns('subscriptions')]
            
            if 'order_id' not in subscription_columns:
                print("Adding order_id column to subscriptions table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE subscriptions ADD COLUMN order_id INTEGER REFERENCES "order"(id)'))
                    conn.commit()
                print("✅ Added order_id column to subscriptions table")
            else:
                print("✅ order_id column already exists in subscriptions table")
            
            # Check if payment tracking columns exist in order table
            order_columns = [col['name'] for col in inspector.get_columns('order')]
            
            if 'payment_id' not in order_columns:
                print("Adding payment tracking columns to order table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE "order" ADD COLUMN payment_id VARCHAR(100)'))
                    conn.execute(db.text('ALTER TABLE "order" ADD COLUMN order_id VARCHAR(100)'))
                    conn.execute(db.text('ALTER TABLE "order" ADD COLUMN payment_status VARCHAR(20) DEFAULT \'pending\''))
                    conn.execute(db.text('ALTER TABLE "order" ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
                    conn.commit()
                print("✅ Added payment tracking columns to order table")
            else:
                print("✅ Payment tracking columns already exist in order table")
            
            # Update existing orders to have proper user_id and meal_plan_id if they don't exist
            if 'user_id' not in order_columns:
                print("Adding user_id column to order table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE "order" ADD COLUMN user_id INTEGER REFERENCES user(id)'))
                    conn.commit()
                print("✅ Added user_id column to order table")
            
            if 'meal_plan_id' not in order_columns:
                print("Adding meal_plan_id column to order table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE "order" ADD COLUMN meal_plan_id INTEGER REFERENCES meal_plan(id)'))
                    conn.commit()
                print("✅ Added meal_plan_id column to order table")
            
            print("✅ Database schema updated successfully!")
            
        except Exception as e:
            print(f"❌ Error updating database schema: {str(e)}")
            return False
        
        return True

def create_test_order():
    """Create a test order to verify the schema works"""
    with app.app_context():
        try:
            # Get first user and meal plan
            from database.models import User, MealPlan
            
            user = User.query.first()
            meal_plan = MealPlan.query.first()
            
            if not user or not meal_plan:
                print("❌ No users or meal plans found for testing")
                return False
            
            # Create test order
            test_order = Order(
                user_id=user.id,
                meal_plan_id=meal_plan.id,
                amount=999.99,
                status='confirmed',
                payment_status='captured',
                payment_id='test_payment_123',
                order_id='test_order_456',
                created_at=datetime.now()
            )
            
            db.session.add(test_order)
            db.session.commit()
            
            print(f"✅ Created test order: {test_order.id}")
            
            # Clean up test order
            db.session.delete(test_order)
            db.session.commit()
            print("✅ Cleaned up test order")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating test order: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🔧 Fixing payment tracking database schema...")
    
    if update_database_schema():
        print("🧪 Testing schema with sample data...")
        if create_test_order():
            print("✅ Payment tracking database schema is ready!")
        else:
            print("❌ Schema test failed")
    else:
        print("❌ Failed to update database schema") 