#!/usr/bin/env python3
"""
Comprehensive script to add test purchases for admin and check payment history/subscription data
"""

from app import create_app
from database.models import User, Order, MealPlan, Subscription, SubscriptionStatus, SubscriptionFrequency
from datetime import datetime, timedelta
import random

def create_test_purchases():
    """Create comprehensive test purchases for admin user"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Creating Comprehensive Test Purchases for Admin")
        print("=" * 60)
        
        # Get admin user and meal plans
        admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
        meal_plans = MealPlan.query.all()
        
        if not admin_user:
            print("❌ Admin user not found")
            return False
            
        if not meal_plans:
            print("❌ No meal plans found")
            return False
            
        print(f"✅ Using admin user: {admin_user.email} (ID: {admin_user.id})")
        print(f"✅ Found {len(meal_plans)} meal plans")
        
        # Check current data
        current_orders = Order.query.filter_by(user_id=admin_user.id).all()
        current_subscriptions = Subscription.query.filter_by(user_id=admin_user.id).all()
        
        print(f"📦 Current orders: {len(current_orders)}")
        print(f"📦 Current subscriptions: {len(current_subscriptions)}")
        
        try:
            from app import db
            
            # Create multiple test purchases with different scenarios
            test_purchases = [
                {
                    'meal_plan': meal_plans[0],  # First meal plan
                    'amount': meal_plans[0].price_weekly,
                    'frequency': 'weekly',
                    'status': 'confirmed',
                    'payment_status': 'captured',
                    'days_ago': 30,  # Old purchase
                    'subscription_status': 'cancelled'
                },
                {
                    'meal_plan': meal_plans[1],  # Second meal plan
                    'amount': meal_plans[1].price_monthly,
                    'frequency': 'monthly',
                    'status': 'confirmed',
                    'payment_status': 'captured',
                    'days_ago': 15,  # Recent purchase
                    'subscription_status': 'active'
                },
                {
                    'meal_plan': meal_plans[2],  # Third meal plan
                    'amount': meal_plans[2].price_weekly,
                    'frequency': 'weekly',
                    'status': 'confirmed',
                    'payment_status': 'captured',
                    'days_ago': 7,  # Very recent
                    'subscription_status': 'active'
                },
                {
                    'meal_plan': meal_plans[0],  # Repeat first meal plan
                    'amount': meal_plans[0].price_weekly,
                    'frequency': 'weekly',
                    'status': 'confirmed',
                    'payment_status': 'captured',
                    'days_ago': 3,  # Very recent
                    'subscription_status': 'paused'
                },
                {
                    'meal_plan': meal_plans[3],  # Fourth meal plan
                    'amount': meal_plans[3].price_monthly,
                    'frequency': 'monthly',
                    'status': 'pending',
                    'payment_status': 'pending',
                    'days_ago': 1,  # Today
                    'subscription_status': None  # No subscription for pending payment
                }
            ]
            
            created_orders = []
            created_subscriptions = []
            
            for i, purchase in enumerate(test_purchases, 1):
                # Create order
                order_date = datetime.now() - timedelta(days=purchase['days_ago'])
                
                order = Order(
                    user_id=admin_user.id,
                    meal_plan_id=purchase['meal_plan'].id,
                    amount=purchase['amount'],
                    status=purchase['status'],
                    payment_status=purchase['payment_status'],
                    payment_id=f'admin_test_payment_{i}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    order_id=f'admin_test_order_{i}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    created_at=order_date
                )
                
                db.session.add(order)
                db.session.flush()  # Get the order ID
                created_orders.append(order)
                
                # Create subscription if payment is captured
                if purchase['payment_status'] == 'captured' and purchase['subscription_status']:
                    # Map status string to enum
                    status_mapping = {
                        'active': SubscriptionStatus.ACTIVE,
                        'paused': SubscriptionStatus.PAUSED,
                        'cancelled': SubscriptionStatus.CANCELED,
                        'canceled': SubscriptionStatus.CANCELED
                    }
                    
                    subscription = Subscription(
                        user_id=admin_user.id,
                        meal_plan_id=purchase['meal_plan'].id,
                        frequency=SubscriptionFrequency.WEEKLY if purchase['frequency'] == 'weekly' else SubscriptionFrequency.MONTHLY,
                        status=status_mapping.get(purchase['subscription_status']),
                        price=purchase['amount'],
                        vegetarian_days='',
                        start_date=order_date,
                        current_period_start=order_date,
                        current_period_end=order_date + timedelta(days=7 if purchase['frequency'] == 'weekly' else 30),
                        created_at=order_date
                    )
                    
                    db.session.add(subscription)
                    created_subscriptions.append(subscription)
                
                print(f"✅ Created purchase {i}: {purchase['meal_plan'].name} - ₹{purchase['amount']} - {purchase['status']}")
            
            db.session.commit()
            
            print(f"\n🎉 Successfully created {len(created_orders)} orders and {len(created_subscriptions)} subscriptions")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating test purchases: {str(e)}")
            db.session.rollback()
            return False

def check_payment_history():
    """Check payment history and subscription data"""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Checking Payment History and Subscription Data")
        print("=" * 50)
        
        admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
        if not admin_user:
            print("❌ Admin user not found")
            return False
        
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
        
        # Show recent orders with details
        print(f"\n📋 Recent Orders (last 5):")
        for order in orders[:5]:
            meal_plan = MealPlan.query.get(order.meal_plan_id)
            meal_plan_name = meal_plan.name if meal_plan else 'N/A'
            
            print(f"  Order #{order.id}: {meal_plan_name} - ₹{order.amount} - {order.status} - {order.payment_status}")
        
        # Show subscription details
        print(f"\n📋 Subscription Details:")
        for sub in subscriptions[:5]:
            meal_plan = MealPlan.query.get(sub.meal_plan_id)
            meal_plan_name = meal_plan.name if meal_plan else 'N/A'
            
            print(f"  Subscription #{sub.id}: {meal_plan_name} - ₹{sub.price} - {sub.status.value} - {sub.frequency.value}")
        
        return True

def test_profile_route_data():
    """Test the profile route data processing"""
    app = create_app()
    
    with app.app_context():
        print("\n🧪 Testing Profile Route Data Processing")
        print("=" * 45)
        
        admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
        if not admin_user:
            print("❌ Admin user not found")
            return False
        
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
            
            return True
            
        except Exception as e:
            print(f"❌ Error in profile route data processing: {str(e)}")
            return False

if __name__ == "__main__":
    print("🚀 Admin Purchase and Payment History Test")
    print("=" * 60)
    
    # Create test purchases
    success1 = create_test_purchases()
    
    # Check payment history
    success2 = check_payment_history()
    
    # Test profile route data
    success3 = test_profile_route_data()
    
    if success1 and success2 and success3:
        print("\n✅ All tests passed! Admin now has comprehensive purchase history.")
        print("\n🎉 What was created:")
        print("   ✅ 5 test orders with different statuses")
        print("   ✅ 4 subscriptions with different statuses (active, paused, cancelled)")
        print("   ✅ Payment history with captured and pending payments")
        print("   ✅ Profile route data processing verified")
    else:
        print("\n❌ Some tests failed. Check the errors above.") 