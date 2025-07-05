#!/usr/bin/env python3
"""
Script to create test data for the admin user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database.models import User, Order, Subscription, MealPlan, SubscriptionStatus, SubscriptionFrequency
from datetime import datetime, timedelta

def create_test_data():
    """Create test orders and subscription for admin user"""
    print("🛠️ Creating test data for admin user...")
    
    with app.app_context():
        try:
            # Get admin user
            admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
            if not admin_user:
                print("❌ Admin user not found")
                return False
            
            print(f"✅ Found admin user: {admin_user.email}")
            
            # Get a meal plan
            meal_plan = MealPlan.query.first()
            if not meal_plan:
                print("❌ No meal plans found")
                return False
            
            print(f"✅ Using meal plan: {meal_plan.name}")
            
            # Create test orders
            test_orders = [
                {
                    'amount': 999.00,
                    'status': 'confirmed',
                    'payment_status': 'completed',
                    'payment_id': 'pay_test_001',
                    'order_id': 'order_test_001',
                    'created_at': datetime.now() - timedelta(days=30)
                },
                {
                    'amount': 1499.00,
                    'status': 'confirmed',
                    'payment_status': 'completed',
                    'payment_id': 'pay_test_002',
                    'order_id': 'order_test_002',
                    'created_at': datetime.now() - timedelta(days=15)
                },
                {
                    'amount': 799.00,
                    'status': 'confirmed',
                    'payment_status': 'completed',
                    'payment_id': 'pay_test_003',
                    'order_id': 'order_test_003',
                    'created_at': datetime.now() - timedelta(days=7)
                }
            ]
            
            created_orders = []
            for i, order_data in enumerate(test_orders):
                order = Order(
                    user_id=admin_user.id,
                    meal_plan_id=meal_plan.id,
                    **order_data
                )
                db.session.add(order)
                created_orders.append(order)
                print(f"   - Created order #{i+1}: ₹{order_data['amount']}")
            
            # Create test subscription
            subscription = Subscription(
                user_id=admin_user.id,
                meal_plan_id=meal_plan.id,
                status=SubscriptionStatus.ACTIVE,
                frequency=SubscriptionFrequency.WEEKLY,
                price=999.00,
                start_date=datetime.now() - timedelta(days=30),
                current_period_start=datetime.now() - timedelta(days=7),
                current_period_end=datetime.now() + timedelta(days=7)
            )
            db.session.add(subscription)
            print(f"   - Created subscription: {subscription.status.value}")
            
            # Commit all changes
            db.session.commit()
            print(f"✅ Successfully created {len(created_orders)} orders and 1 subscription")
            
            # Link subscription to the first order
            if created_orders:
                created_orders[0].subscriptions = [subscription]
                db.session.commit()
                print("✅ Linked subscription to first order")
            
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
        for order in orders:
            print(f"   - Order #{order.id}: ₹{order.amount} ({order.payment_status})")
        
        # Check subscriptions
        subscriptions = Subscription.query.filter_by(user_id=1).all()
        print(f"📦 Subscriptions for admin user: {len(subscriptions)}")
        for sub in subscriptions:
            print(f"   - Subscription #{sub.id}: {sub.status} ({sub.frequency})")

if __name__ == "__main__":
    print("🚀 Test Data Creator")
    print("=" * 50)
    
    if create_test_data():
        verify_data()
        print("\n✅ Test data created successfully!")
        print("Now check the profile page to see the orders and subscriptions.")
    else:
        print("\n❌ Failed to create test data") 