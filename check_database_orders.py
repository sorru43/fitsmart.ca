#!/usr/bin/env python3
"""
Script to check database for orders and create test data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database.models import User, Order, Subscription, MealPlan
from datetime import datetime, timedelta

def check_database_orders():
    """Check for existing orders in the database"""
    print("🔍 Checking database for orders...")
    
    with app.app_context():
        # Check total orders
        total_orders = Order.query.count()
        print(f"📊 Total orders in database: {total_orders}")
        
        # Check orders by user
        users_with_orders = db.session.query(Order.user_id, User.email, db.func.count(Order.id)).join(User).group_by(Order.user_id, User.email).all()
        
        print(f"👥 Users with orders: {len(users_with_orders)}")
        for user_id, email, order_count in users_with_orders:
            print(f"   - {email}: {order_count} orders")
        
        # Check recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        print(f"\n📋 Recent orders (last 5):")
        for order in recent_orders:
            print(f"   - Order #{order.id}: ₹{order.amount} ({order.payment_status}) - {order.created_at}")
        
        # Check subscriptions
        total_subscriptions = Subscription.query.count()
        print(f"\n📦 Total subscriptions: {total_subscriptions}")
        
        # Check meal plans
        meal_plans = MealPlan.query.all()
        print(f"🍽️ Available meal plans: {len(meal_plans)}")
        for plan in meal_plans:
            print(f"   - {plan.name}: ₹{plan.price_weekly}/week")
        
        return total_orders, users_with_orders

def create_test_orders():
    """Create test orders for the admin user"""
    print("\n🛠️ Creating test orders...")
    
    with app.app_context():
        # Get admin user
        admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
        if not admin_user:
            print("❌ Admin user not found")
            return False
        
        # Get a meal plan
        meal_plan = MealPlan.query.first()
        if not meal_plan:
            print("❌ No meal plans found")
            return False
        
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
        
        # Create test subscription
        subscription = Subscription(
            user_id=admin_user.id,
            meal_plan_id=meal_plan.id,
            status='active',
            frequency='weekly',
            price=999.00,
            start_date=datetime.now() - timedelta(days=30),
            current_period_start=datetime.now() - timedelta(days=7),
            current_period_end=datetime.now() + timedelta(days=7)
        )
        db.session.add(subscription)
        
        try:
            db.session.commit()
            print(f"✅ Created {len(created_orders)} test orders and 1 subscription")
            
            # Link subscription to the first order
            if created_orders:
                created_orders[0].subscriptions = [subscription]
                db.session.commit()
                print("✅ Linked subscription to first order")
            
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating test data: {str(e)}")
            return False

def main():
    """Main function"""
    print("🚀 Database Order Checker")
    print("=" * 50)
    
    # Check existing orders
    total_orders, users_with_orders = check_database_orders()
    
    if total_orders == 0:
        print("\n⚠️ No orders found in database")
        response = input("Create test orders for admin user? (y/n): ")
        if response.lower() == 'y':
            if create_test_orders():
                print("\n✅ Test data created successfully!")
                print("Now check the profile page to see the orders.")
            else:
                print("\n❌ Failed to create test data")
        else:
            print("Skipping test data creation")
    else:
        print(f"\n✅ Found {total_orders} orders in database")
        print("Profile page should show these orders.")

if __name__ == "__main__":
    main() 