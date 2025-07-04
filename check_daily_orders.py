#!/usr/bin/env python3
"""
Script to check daily orders and active subscriptions for debugging admin orders page
"""

from app import create_app
from database.models import Subscription, SubscriptionStatus, User, MealPlan, SkippedDelivery, Delivery, DeliveryStatus
from datetime import datetime, date
import json

def check_daily_orders():
    """Check daily orders and active subscriptions for today"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking Daily Orders and Active Subscriptions")
        print("=" * 60)
        
        today = datetime.now().date()
        print(f"📅 Today's date: {today}")
        print(f"📅 Today's weekday: {today.weekday()} (0=Monday, 6=Sunday)")
        
        # Get all active subscriptions
        active_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).all()
        print(f"\n📦 Total active subscriptions: {len(active_subscriptions)}")
        
        if not active_subscriptions:
            print("❌ No active subscriptions found!")
            print("\n💡 This is why no daily orders are showing in admin.")
            print("   Check if subscriptions are paused, cancelled, or expired.")
            return False
        
        # Check each subscription
        orders_for_today = []
        skipped_subscriptions = []
        
        for i, subscription in enumerate(active_subscriptions, 1):
            print(f"\n📋 Subscription #{i}:")
            print(f"   ID: {subscription.id}")
            
            # Get user and meal plan info
            user = subscription.user
            meal_plan = subscription.meal_plan
            
            print(f"   User: {user.name} ({user.email})")
            print(f"   Meal Plan: {meal_plan.name}")
            print(f"   Status: {subscription.status.value}")
            print(f"   Frequency: {subscription.frequency.value}")
            
            # Check delivery days
            delivery_days = []
            if subscription.delivery_days:
                try:
                    delivery_days = json.loads(subscription.delivery_days)
                except:
                    delivery_days = []
            
            print(f"   Delivery Days: {delivery_days}")
            print(f"   Should deliver today: {today.weekday() in delivery_days if delivery_days else 'Yes (no delivery days specified)'}")
            
            # Check if delivery is skipped
            skipped_delivery = SkippedDelivery.query.filter_by(
                subscription_id=subscription.id,
                delivery_date=today
            ).first()
            
            if skipped_delivery:
                print(f"   ❌ DELIVERY SKIPPED for today")
                skipped_subscriptions.append(subscription)
                continue
            
            # Check if should deliver today
            should_deliver = True
            if delivery_days:
                should_deliver = today.weekday() in delivery_days
            
            if not should_deliver:
                print(f"   ⏸️ No delivery scheduled for today (weekday {today.weekday()} not in delivery days)")
                continue
            
            # Check existing delivery record
            existing_delivery = Delivery.query.filter_by(
                subscription_id=subscription.id,
                delivery_date=today
            ).first()
            
            delivery_status = existing_delivery.status.value if existing_delivery else 'PENDING'
            print(f"   ✅ WILL DELIVER TODAY - Status: {delivery_status}")
            
            # Create order info
            order_info = {
                'subscription_id': subscription.id,
                'user_name': user.name,
                'user_email': user.email,
                'user_phone': user.phone,
                'meal_plan_name': meal_plan.name,
                'delivery_address': subscription.delivery_address,
                'delivery_city': subscription.delivery_city,
                'delivery_province': subscription.delivery_province,
                'delivery_postal_code': subscription.delivery_postal_code,
                'delivery_status': delivery_status,
                'delivery_id': existing_delivery.id if existing_delivery else None
            }
            
            orders_for_today.append(order_info)
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   Total active subscriptions: {len(active_subscriptions)}")
        print(f"   Orders for today: {len(orders_for_today)}")
        print(f"   Skipped deliveries: {len(skipped_subscriptions)}")
        
        if orders_for_today:
            print(f"\n✅ Orders that should appear in admin today:")
            for i, order in enumerate(orders_for_today, 1):
                print(f"   {i}. {order['user_name']} - {order['meal_plan_name']} - {order['delivery_status']}")
        else:
            print(f"\n❌ No orders for today!")
            print(f"   This explains why the admin orders page is empty.")
        
        # Check get_daily_orders function
        print(f"\n🧪 Testing get_daily_orders function:")
        try:
            from utils.report_utils import get_daily_orders
            daily_orders = get_daily_orders(today)
            print(f"   get_daily_orders returned: {len(daily_orders)} orders")
            
            if daily_orders:
                print(f"   First order: {daily_orders[0].get('user_name', 'N/A')} - {daily_orders[0].get('meal_plan_name', 'N/A')}")
            else:
                print(f"   No orders returned by get_daily_orders")
        except Exception as e:
            print(f"   ❌ Error calling get_daily_orders: {str(e)}")
        
        return True

def check_subscription_data():
    """Check subscription data quality"""
    app = create_app()
    
    with app.app_context():
        print(f"\n🔍 Checking Subscription Data Quality")
        print("=" * 50)
        
        # Check for subscriptions with missing delivery info
        subscriptions_without_delivery_days = Subscription.query.filter(
            Subscription.delivery_days.is_(None) | (Subscription.delivery_days == '')
        ).all()
        
        print(f"📦 Subscriptions without delivery_days: {len(subscriptions_without_delivery_days)}")
        
        # Check for subscriptions with missing address info
        subscriptions_without_address = Subscription.query.filter(
            (Subscription.delivery_address.is_(None) | (Subscription.delivery_address == '')) |
            (Subscription.delivery_city.is_(None) | (Subscription.delivery_city == ''))
        ).all()
        
        print(f"📦 Subscriptions without delivery address: {len(subscriptions_without_address)}")
        
        # Check subscription statuses
        status_counts = {}
        for status in SubscriptionStatus:
            count = Subscription.query.filter_by(status=status).count()
            status_counts[status.value] = count
        
        print(f"\n📊 Subscription Status Breakdown:")
        for status, count in status_counts.items():
            print(f"   {status}: {count}")
        
        return True

def check_delivery_records():
    """Check delivery records for today"""
    app = create_app()
    
    with app.app_context():
        print(f"\n🔍 Checking Delivery Records for Today")
        print("=" * 50)
        
        today = datetime.now().date()
        
        # Check all delivery records for today
        today_deliveries = Delivery.query.filter_by(delivery_date=today).all()
        print(f"📦 Total delivery records for today: {len(today_deliveries)}")
        
        if today_deliveries:
            print(f"\n📋 Delivery Records:")
            for delivery in today_deliveries:
                subscription = Subscription.query.get(delivery.subscription_id)
                user = User.query.get(delivery.user_id)
                
                print(f"   Delivery #{delivery.id}: {user.name if user else 'N/A'} - {delivery.status.value}")
        
        # Check skipped deliveries
        skipped_deliveries = SkippedDelivery.query.filter_by(delivery_date=today).all()
        print(f"\n⏸️ Skipped deliveries for today: {len(skipped_deliveries)}")
        
        if skipped_deliveries:
            print(f"📋 Skipped Deliveries:")
            for skipped in skipped_deliveries:
                subscription = Subscription.query.get(skipped.subscription_id)
                user = User.query.get(subscription.user_id) if subscription else None
                
                print(f"   Subscription #{skipped.subscription_id}: {user.name if user else 'N/A'} - Date: {skipped.delivery_date}")
        
        return True

if __name__ == "__main__":
    print("🚀 Daily Orders Debug Script")
    print("=" * 40)
    
    success1 = check_daily_orders()
    success2 = check_subscription_data()
    success3 = check_delivery_records()
    
    if success1 and success2 and success3:
        print(f"\n✅ Debug script completed successfully!")
        print(f"\n📝 Next Steps:")
        print(f"   1. Check if there are active subscriptions")
        print(f"   2. Verify delivery_days configuration")
        print(f"   3. Check for skipped deliveries")
        print(f"   4. Ensure server date/time is correct")
    else:
        print(f"\n❌ Some checks failed. Check the errors above.") 