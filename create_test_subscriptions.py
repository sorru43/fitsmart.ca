#!/usr/bin/env python3
"""
Script to create test subscriptions for production testing
"""

from app import create_app
from database.models import Subscription, SubscriptionStatus, SubscriptionFrequency, User, MealPlan, Order
from datetime import datetime, timedelta
import json

def create_test_subscriptions():
    """Create test subscriptions for production testing"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Creating Test Subscriptions for Production")
        print("=" * 50)
        
        # Get or create test user
        test_user = User.query.filter_by(email='admin@healthyrizz.in').first()
        if not test_user:
            print("❌ Test user 'admin@healthyrizz.in' not found!")
            print("   Please create a user first or update the email in this script.")
            return False
        
        print(f"✅ Using test user: {test_user.name} ({test_user.email})")
        
        # Get meal plans
        meal_plans = MealPlan.query.filter_by(is_active=True).all()
        if not meal_plans:
            print("❌ No active meal plans found!")
            return False
        
        print(f"📦 Found {len(meal_plans)} active meal plans")
        
        # Create test subscriptions
        subscriptions_created = 0
        
        for i, meal_plan in enumerate(meal_plans[:3], 1):  # Create max 3 subscriptions
            # Check if subscription already exists for this user and meal plan
            existing_subscription = Subscription.query.filter_by(
                user_id=test_user.id,
                meal_plan_id=meal_plan.id
            ).first()
            
            if existing_subscription:
                print(f"⏭️  Subscription already exists for {meal_plan.name}")
                continue
            
            # Create order first
            order = Order(
                user_id=test_user.id,
                meal_plan_id=meal_plan.id,
                amount=float(meal_plan.price_weekly),
                status='confirmed',
                payment_status='captured',
                payment_id=f'test_payment_{datetime.now().strftime("%Y%m%d%H%M%S")}_{i}',
                order_id=f'test_order_{datetime.now().strftime("%Y%m%d%H%M%S")}_{i}'
            )
            
            # Create subscription
            frequency = SubscriptionFrequency.WEEKLY if i % 2 == 0 else SubscriptionFrequency.MONTHLY
            
            subscription = Subscription(
                user_id=test_user.id,
                meal_plan_id=meal_plan.id,
                frequency=frequency,
                status=SubscriptionStatus.ACTIVE,
                price=float(meal_plan.price_weekly),
                order_id=order.id,
                start_date=datetime.now(),
                current_period_start=datetime.now(),
                current_period_end=(
                    datetime.now() + timedelta(days=7) if frequency == SubscriptionFrequency.WEEKLY 
                    else datetime.now() + timedelta(days=30)
                ),
                # Set delivery days to weekdays (Monday-Friday)
                delivery_days="0,1,2,3,4",
                # Add delivery address
                delivery_address=test_user.address or "123 Test Street",
                delivery_city=test_user.city or "Toronto",
                delivery_province=test_user.state or "ON",
                delivery_postal_code=test_user.postal_code or "M5V 3A8"
            )
            
            # Add to database
            from database.models import db
            db.session.add(order)
            db.session.add(subscription)
            
            subscriptions_created += 1
            print(f"✅ Created subscription #{i}: {meal_plan.name} ({frequency.value})")
        
        if subscriptions_created > 0:
            try:
                db.session.commit()
                print(f"\n🎉 Successfully created {subscriptions_created} test subscriptions!")
                print(f"   You should now see daily orders in the admin panel.")
            except Exception as e:
                print(f"❌ Error committing to database: {str(e)}")
                db.session.rollback()
                return False
        else:
            print(f"\n⏭️  No new subscriptions created (all already exist)")
        
        # Verify subscriptions
        active_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).all()
        print(f"\n📊 Total active subscriptions: {len(active_subscriptions)}")
        
        for sub in active_subscriptions:
            user = User.query.get(sub.user_id)
            meal_plan = MealPlan.query.get(sub.meal_plan_id)
            print(f"   - {user.name}: {meal_plan.name} ({sub.frequency.value}) - {sub.status.value}")
        
        return True

def verify_daily_orders():
    """Verify that daily orders can be generated"""
    app = create_app()
    
    with app.app_context():
        print(f"\n🔍 Verifying Daily Orders Generation")
        print("=" * 40)
        
        try:
            from utils.report_utils import get_daily_orders
            today = datetime.now().date()
            daily_orders = get_daily_orders(today)
            
            print(f"📅 Daily orders for {today}: {len(daily_orders)}")
            
            if daily_orders:
                print(f"✅ Daily orders are working!")
                for i, order in enumerate(daily_orders[:3], 1):
                    print(f"   {i}. {order.get('user_name', 'N/A')} - {order.get('meal_plan_name', 'N/A')}")
            else:
                print(f"❌ No daily orders generated")
                
        except Exception as e:
            print(f"❌ Error generating daily orders: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    print("🚀 Test Subscription Creation Script")
    print("=" * 40)
    
    success1 = create_test_subscriptions()
    success2 = verify_daily_orders()
    
    if success1 and success2:
        print(f"\n✅ Script completed successfully!")
        print(f"\n📝 Next Steps:")
        print(f"   1. Check the admin panel for daily orders")
        print(f"   2. Verify subscriptions are visible in admin")
        print(f"   3. Test the daily meal prep functionality")
    else:
        print(f"\n❌ Some operations failed. Check the errors above.") 