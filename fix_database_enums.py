#!/usr/bin/env python3
"""
Script to fix database enum issues and create test data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database.models import User, Order, Subscription, MealPlan, SubscriptionStatus, SubscriptionFrequency
from datetime import datetime, timedelta
from sqlalchemy import text

def fix_database_enums():
    """Fix existing enum values in database"""
    print("🔧 Fixing database enum values...")
    
    with app.app_context():
        try:
            # Fix subscription status values
            print("   - Fixing subscription status values...")
            db.session.execute(text("UPDATE subscriptions SET status = 'ACTIVE' WHERE status = 'active'"))
            db.session.execute(text("UPDATE subscriptions SET status = 'PAUSED' WHERE status = 'paused'"))
            db.session.execute(text("UPDATE subscriptions SET status = 'CANCELED' WHERE status = 'cancelled' OR status = 'canceled'"))
            db.session.execute(text("UPDATE subscriptions SET status = 'EXPIRED' WHERE status = 'expired'"))
            
            # Fix subscription frequency values
            print("   - Fixing subscription frequency values...")
            db.session.execute(text("UPDATE subscriptions SET frequency = 'WEEKLY' WHERE frequency = 'weekly'"))
            db.session.execute(text("UPDATE subscriptions SET frequency = 'MONTHLY' WHERE frequency = 'monthly'"))
            
            db.session.commit()
            print("✅ Database enum values fixed successfully")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing database: {str(e)}")
            return False

def create_comprehensive_test_data():
    """Create comprehensive test data for admin user"""
    print("\n🛠️ Creating comprehensive test data...")
    
    with app.app_context():
        try:
            # Get admin user
            admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
            if not admin_user:
                print("❌ Admin user not found")
                return False
            
            print(f"✅ Found admin user: {admin_user.email}")
            
            # Get meal plans
            meal_plans = MealPlan.query.all()
            if not meal_plans:
                print("❌ No meal plans found")
                return False
            
            print(f"✅ Found {len(meal_plans)} meal plans")
            
            # Create test orders for the last 3 months
            test_orders = []
            base_date = datetime.now()
            
            for i in range(12):  # Create 12 orders over 3 months
                days_ago = (i * 7) + (i * 2)  # Vary the dates
                meal_plan = meal_plans[i % len(meal_plans)]
                
                order_data = {
                    'user_id': admin_user.id,
                    'meal_plan_id': meal_plan.id,
                    'amount': round(meal_plan.price_weekly + (i * 50), 2),
                    'status': 'confirmed',
                    'payment_status': 'completed' if i < 10 else 'pending',
                    'payment_id': f'pay_test_{i+1:03d}',
                    'order_id': f'order_test_{i+1:03d}',
                    'delivery_address': f'{admin_user.address}, {admin_user.city}',
                    'created_at': base_date - timedelta(days=days_ago),
                    'updated_at': base_date - timedelta(days=days_ago)
                }
                
                order = Order(**order_data)
                db.session.add(order)
                test_orders.append(order)
                print(f"   - Created order #{i+1}: ₹{order_data['amount']} ({order_data['payment_status']})")
            
            # Create test subscriptions
            subscriptions_data = [
                {
                    'user_id': admin_user.id,
                    'meal_plan_id': meal_plans[0].id,
                    'status': SubscriptionStatus.ACTIVE,
                    'frequency': SubscriptionFrequency.WEEKLY,
                    'price': meal_plans[0].price_weekly,
                    'start_date': base_date - timedelta(days=60),
                    'current_period_start': base_date - timedelta(days=7),
                    'current_period_end': base_date + timedelta(days=7),
                    'delivery_address': f'{admin_user.address}',
                    'delivery_city': admin_user.city,
                    'delivery_province': admin_user.province,
                    'delivery_postal_code': admin_user.postal_code
                },
                {
                    'user_id': admin_user.id,
                    'meal_plan_id': meal_plans[1].id if len(meal_plans) > 1 else meal_plans[0].id,
                    'status': SubscriptionStatus.PAUSED,
                    'frequency': SubscriptionFrequency.MONTHLY,
                    'price': meal_plans[1].price_monthly if len(meal_plans) > 1 else meal_plans[0].price_monthly,
                    'start_date': base_date - timedelta(days=90),
                    'current_period_start': base_date - timedelta(days=30),
                    'current_period_end': base_date + timedelta(days=30),
                    'delivery_address': f'{admin_user.address}',
                    'delivery_city': admin_user.city,
                    'delivery_province': admin_user.province,
                    'delivery_postal_code': admin_user.postal_code
                }
            ]
            
            created_subscriptions = []
            for i, sub_data in enumerate(subscriptions_data):
                subscription = Subscription(**sub_data)
                db.session.add(subscription)
                created_subscriptions.append(subscription)
                print(f"   - Created subscription #{i+1}: {subscription.status.value} ({subscription.frequency.value})")
            
            # Commit all changes
            db.session.commit()
            print(f"✅ Successfully created {len(test_orders)} orders and {len(created_subscriptions)} subscriptions")
            
            # Link some orders to subscriptions
            if test_orders and created_subscriptions:
                for i, order in enumerate(test_orders[:6]):  # Link first 6 orders to subscriptions
                    subscription = created_subscriptions[i % len(created_subscriptions)]
                    order.subscriptions = [subscription]
                
                db.session.commit()
                print("✅ Linked orders to subscriptions")
            
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
        orders = Order.query.all()
        print(f"📊 Total orders in database: {len(orders)}")
        
        admin_orders = Order.query.filter_by(user_id=1).all()
        print(f"📊 Orders for admin user: {len(admin_orders)}")
        
        completed_orders = Order.query.filter_by(payment_status='completed').all()
        print(f"💰 Completed orders: {len(completed_orders)}")
        
        total_revenue = sum(order.amount for order in completed_orders)
        print(f"💰 Total revenue: ₹{total_revenue}")
        
        # Check subscriptions
        subscriptions = Subscription.query.all()
        print(f"📦 Total subscriptions: {len(subscriptions)}")
        
        active_subs = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).all()
        print(f"📦 Active subscriptions: {len(active_subs)}")

def main():
    """Main function"""
    print("🚀 Database Enum Fixer & Test Data Creator")
    print("=" * 60)
    
    # Step 1: Fix database enum values
    if not fix_database_enums():
        print("❌ Failed to fix database enums")
        return
    
    # Step 2: Create comprehensive test data
    if create_comprehensive_test_data():
        # Step 3: Verify data
        verify_data()
        print("\n✅ All operations completed successfully!")
        print("Now check the profile page to see all orders and subscriptions.")
    else:
        print("\n❌ Failed to create test data")

if __name__ == "__main__":
    main() 