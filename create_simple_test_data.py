#!/usr/bin/env python3
"""
Simple script to create test data that works with production database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database.models import User, Order, Subscription, MealPlan, SubscriptionStatus, SubscriptionFrequency
from datetime import datetime, timedelta
from sqlalchemy import text

def create_simple_test_data():
    """Create simple test data for admin user"""
    print("🛠️ Creating simple test data...")
    
    with app.app_context():
        try:
            # Get admin user
            admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
            if not admin_user:
                print("❌ Admin user not found")
                return False
            
            print(f"✅ Found admin user: {admin_user.email} (ID: {admin_user.id})")
            
            # Get meal plans
            meal_plans = MealPlan.query.all()
            if not meal_plans:
                print("❌ No meal plans found")
                return False
            
            print(f"✅ Found {len(meal_plans)} meal plans")
            
            # Create simple test orders
            orders_created = 0
            for i in range(5):  # Create 5 simple orders
                meal_plan = meal_plans[i % len(meal_plans)]
                days_ago = (i + 1) * 7  # 7, 14, 21, 28, 35 days ago
                
                order = Order(
                    user_id=admin_user.id,
                    meal_plan_id=meal_plan.id,
                    amount=float(meal_plan.price_weekly) + (i * 100),
                    status='confirmed',
                    payment_status='completed',
                    payment_id=f'pay_simple_{i+1:03d}',
                    order_id=f'order_simple_{i+1:03d}',
                    delivery_address=f'{admin_user.address}, {admin_user.city}',
                    created_at=datetime.now() - timedelta(days=days_ago),
                    updated_at=datetime.now() - timedelta(days=days_ago)
                )
                
                db.session.add(order)
                orders_created += 1
                print(f"   - Created order #{i+1}: ₹{order.amount} ({meal_plan.name})")
            
            # Create simple subscription
            subscription = Subscription(
                user_id=admin_user.id,
                meal_plan_id=meal_plans[0].id,
                status=SubscriptionStatus.ACTIVE,
                frequency=SubscriptionFrequency.WEEKLY,
                price=meal_plans[0].price_weekly,
                start_date=datetime.now() - timedelta(days=30),
                current_period_start=datetime.now() - timedelta(days=7),
                current_period_end=datetime.now() + timedelta(days=7),
                delivery_address=admin_user.address,
                delivery_city=admin_user.city,
                delivery_province=admin_user.province,
                delivery_postal_code=admin_user.postal_code
            )
            
            db.session.add(subscription)
            print(f"   - Created subscription: {subscription.status.value}")
            
            # Commit all changes
            db.session.commit()
            print(f"✅ Successfully created {orders_created} orders and 1 subscription")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating test data: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return False

def verify_data():
    """Verify the created data"""
    print("\n🔍 Verifying created data...")
    
    with app.app_context():
        # Check orders
        orders = Order.query.filter_by(user_id=1).all()
        print(f"📊 Orders for admin user: {len(orders)}")
        
        total_amount = sum(order.amount for order in orders if order.payment_status == 'completed')
        print(f"💰 Total spent: ₹{total_amount}")
        
        # Check subscriptions
        subscriptions = Subscription.query.filter_by(user_id=1).all()
        print(f"📦 Subscriptions for admin user: {len(subscriptions)}")

if __name__ == "__main__":
    print("🚀 Simple Test Data Creator")
    print("=" * 50)
    
    if create_simple_test_data():
        verify_data()
        print("\n✅ Simple test data created successfully!")
        print("Now check the profile page to see the orders and subscriptions.")
    else:
        print("\n❌ Failed to create test data") 