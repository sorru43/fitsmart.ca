#!/usr/bin/env python3
"""
Script to check the actual Order model structure in production
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database.models import Order
from sqlalchemy import inspect

def check_order_model():
    """Check the actual Order model structure"""
    print("🔍 Checking Order model structure...")
    
    with app.app_context():
        try:
            # Get the table structure
            inspector = inspect(db.engine)
            columns = inspector.get_columns('order')
            
            print(f"📊 Order table columns:")
            for column in columns:
                print(f"   - {column['name']}: {column['type']} (nullable: {column['nullable']})")
            
            # Try to get an existing order to see the structure
            existing_order = Order.query.first()
            if existing_order:
                print(f"\n📋 Sample existing order:")
                print(f"   - ID: {existing_order.id}")
                print(f"   - Amount: {existing_order.amount}")
                print(f"   - Status: {existing_order.status}")
                print(f"   - Payment Status: {existing_order.payment_status}")
                print(f"   - Created: {existing_order.created_at}")
                
                # Check if user relationship exists
                if hasattr(existing_order, 'user') and existing_order.user:
                    print(f"   - User: {existing_order.user.email}")
                
                # Check if meal_plan relationship exists
                if hasattr(existing_order, 'meal_plan') and existing_order.meal_plan:
                    print(f"   - Meal Plan: {existing_order.meal_plan.name}")
            else:
                print(f"\n📋 No existing orders found")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking Order model: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return False

if __name__ == "__main__":
    print("🚀 Order Model Structure Checker")
    print("=" * 50)
    check_order_model() 