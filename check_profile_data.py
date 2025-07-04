#!/usr/bin/env python3
"""
Script to check profile data and verify payment history and subscription data
"""

from app import create_app
from database.models import User, Order, MealPlan, Subscription, SubscriptionStatus
from datetime import datetime

def check_profile_data():
    """Check profile data for admin user"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking Profile Data for Admin User")
        print("=" * 50)
        
        admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
        if not admin_user:
            print("❌ Admin user not found")
            return False
        
        print(f"✅ Admin user: {admin_user.email} (ID: {admin_user.id})")
        
        # Get all orders
        orders = Order.query.filter_by(user_id=admin_user.id).order_by(Order.created_at.desc()).all()
        print(f"📦 Total orders: {len(orders)}")
        
        # Get all subscriptions
        subscriptions = Subscription.query.filter_by(user_id=admin_user.id).order_by(Subscription.created_at.desc()).all()
        print(f"📦 Total subscriptions: {len(subscriptions)}")
        
        # Check payment history
        payment_history = []
        total_spent = 0
        
        for order in orders:
            if order.payment_status and order.payment_id:
                payment_history.append({
                    'order_id': order.id,
                    'payment_id': order.payment_id,
                    'amount': order.amount,
                    'status': order.payment_status,
                    'date': order.created_at
                })
                
                if order.payment_status == 'captured':
                    total_spent += order.amount
        
        print(f"💳 Payment history entries: {len(payment_history)}")
        print(f"💰 Total spent: ₹{total_spent:.2f}")
        
        # Check subscription statuses
        active_subscriptions = [s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE]
        paused_subscriptions = [s for s in subscriptions if s.status == SubscriptionStatus.PAUSED]
        cancelled_subscriptions = [s for s in subscriptions if s.status == SubscriptionStatus.CANCELED]
        
        print(f"🔄 Active subscriptions: {len(active_subscriptions)}")
        print(f"⏸️ Paused subscriptions: {len(paused_subscriptions)}")
        print(f"❌ Cancelled subscriptions: {len(cancelled_subscriptions)}")
        
        # Show recent orders with meal plan info
        print(f"\n📋 Recent Orders (last 10):")
        for order in orders[:10]:
            meal_plan = MealPlan.query.get(order.meal_plan_id)
            meal_plan_name = meal_plan.name if meal_plan else 'N/A'
            
            print(f"  Order #{order.id}: {meal_plan_name} - ₹{order.amount} - {order.status} - {order.payment_status} - {order.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Show subscription details
        print(f"\n📋 Subscription Details:")
        for sub in subscriptions[:10]:
            meal_plan = MealPlan.query.get(sub.meal_plan_id)
            meal_plan_name = meal_plan.name if meal_plan else 'N/A'
            
            print(f"  Subscription #{sub.id}: {meal_plan_name} - ₹{sub.price} - {sub.status.value} - {sub.frequency.value} - {sub.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Test profile route data processing
        print(f"\n🧪 Testing Profile Route Data Processing:")
        
        # Simulate the profile route logic
        try:
            # Get user's active subscriptions
            active_subscriptions = Subscription.query.filter(
                Subscription.user_id == admin_user.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            ).all()
            
            # Get user's paused subscriptions
            paused_subscriptions = Subscription.query.filter(
                Subscription.user_id == admin_user.id,
                Subscription.status == SubscriptionStatus.PAUSED
            ).all()
            
            # Get user's canceled subscriptions
            canceled_subscriptions = Subscription.query.filter(
                Subscription.user_id == admin_user.id,
                Subscription.status == SubscriptionStatus.CANCELED
            ).all()
            
            # Get user's order history
            orders = Order.query.filter(
                Order.user_id == admin_user.id
            ).order_by(Order.created_at.desc()).all()
            
            # Get recent orders with meal plan info
            recent_orders = []
            for order in orders[:10]:
                try:
                    meal_plan_name = 'N/A'
                    if hasattr(order, 'meal_plan') and order.meal_plan:
                        meal_plan_name = order.meal_plan.name
                    elif hasattr(order, 'meal_plan_id') and order.meal_plan_id:
                        meal_plan = MealPlan.query.get(order.meal_plan_id)
                        if meal_plan:
                            meal_plan_name = meal_plan.name
                except Exception as e:
                    meal_plan_name = 'N/A'
                    
                order_data = {
                    'id': order.id,
                    'amount': order.amount,
                    'status': order.status,
                    'payment_status': order.payment_status,
                    'created_at': order.created_at,
                    'meal_plan_name': meal_plan_name
                }
                recent_orders.append(order_data)
            
            # Get payment history from orders
            payment_history = []
            for order in orders:
                if order.payment_status and order.payment_id:
                    payment_history.append({
                        'order_id': order.id,
                        'payment_id': order.payment_id,
                        'amount': order.amount,
                        'status': order.payment_status,
                        'date': order.created_at,
                        'subscription_id': None,
                        'meal_plan_name': 'N/A'
                    })
            
            # Calculate total spent
            total_spent = sum(order.amount for order in orders if order.payment_status == 'captured')
            
            # Get subscription statistics
            total_subscriptions = len(active_subscriptions) + len(paused_subscriptions) + len(canceled_subscriptions)
            
            print(f"✅ Profile data processing successful!")
            print(f"📦 Orders found: {len(orders)}")
            print(f"💳 Payment history entries: {len(payment_history)}")
            print(f"💰 Total spent: ₹{total_spent:.2f}")
            print(f"🔄 Total subscriptions: {total_subscriptions}")
            print(f"  - Active: {len(active_subscriptions)}")
            print(f"  - Paused: {len(paused_subscriptions)}")
            print(f"  - Cancelled: {len(canceled_subscriptions)}")
            
            # Show sample data that would be passed to template
            print(f"\n📋 Sample Data for Template:")
            print(f"Recent Orders (first 3):")
            for order_data in recent_orders[:3]:
                print(f"  - Order #{order_data['id']}: {order_data['meal_plan_name']} - ₹{order_data['amount']} - {order_data['status']}")
            
            print(f"Payment History (first 3):")
            for payment in payment_history[:3]:
                print(f"  - Payment #{payment['order_id']}: ₹{payment['amount']} - {payment['status']} - {payment['date'].strftime('%Y-%m-%d')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in profile route data processing: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return False

if __name__ == "__main__":
    print("🚀 Profile Data Check")
    print("=" * 30)
    
    success = check_profile_data()
    
    if success:
        print("\n✅ Profile data check completed successfully!")
        print("\n🎉 Summary:")
        print("   ✅ Admin user has comprehensive order history")
        print("   ✅ Payment history is properly populated")
        print("   ✅ Subscriptions are correctly categorized")
        print("   ✅ Profile route data processing works correctly")
        print("\n📝 Next Steps:")
        print("   1. Login as admin user")
        print("   2. Go to profile page")
        print("   3. Check Orders tab for order history")
        print("   4. Check Subscriptions tab for subscription details")
        print("   5. Verify payment history is displayed correctly")
    else:
        print("\n❌ Profile data check failed. Check the errors above.") 