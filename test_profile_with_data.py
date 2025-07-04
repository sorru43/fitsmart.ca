#!/usr/bin/env python3
"""
Test script to verify profile functionality with test data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database.models import User, Order, Subscription, MealPlan, SubscriptionStatus
from datetime import datetime

def test_profile_functionality():
    """Test the profile functionality with test data"""
    print("🧪 Testing profile functionality with test data...")
    
    with app.app_context():
        try:
            # Get admin user
            admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
            if not admin_user:
                print("❌ Admin user not found")
                return False
            
            print(f"✅ Found admin user: {admin_user.email}")
            
            # Simulate the profile route logic
            print("\n🔍 Testing profile route logic...")
            
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
            
            # Get user's order history (all orders)
            orders = Order.query.filter(
                Order.user_id == admin_user.id
            ).order_by(Order.created_at.desc()).all()
            
            # Get recent orders (last 10) with meal plan info
            recent_orders = []
            for order in orders[:10]:
                order_data = {
                    'id': order.id,
                    'amount': order.amount,
                    'status': order.status,
                    'payment_status': order.payment_status,
                    'created_at': order.created_at,
                    'meal_plan_name': order.meal_plan.name if order.meal_plan else 'N/A'
                }
                recent_orders.append(order_data)
            
            # Get payment history from orders
            payment_history = []
            for order in orders:
                if order.payment_status and order.payment_id:
                    # Get subscription info if available
                    subscription_info = None
                    if order.subscriptions:
                        subscription = order.subscriptions[0]  # Get first subscription
                        subscription_info = {
                            'id': subscription.id,
                            'meal_plan_name': subscription.meal_plan.name if subscription.meal_plan else 'N/A'
                        }
                    
                    payment_history.append({
                        'order_id': order.id,
                        'payment_id': order.payment_id,
                        'amount': order.amount,
                        'status': order.payment_status,
                        'date': order.created_at,
                        'subscription_id': subscription_info['id'] if subscription_info else None,
                        'meal_plan_name': subscription_info['meal_plan_name'] if subscription_info else 'N/A'
                    })
            
            # Calculate total spent
            total_spent = sum(order.amount for order in orders if order.payment_status == 'completed')
            
            # Get subscription statistics
            total_subscriptions = len(active_subscriptions) + len(paused_subscriptions) + len(canceled_subscriptions)
            
            # Print results
            print(f"📊 Profile Data Summary:")
            print(f"   - Active subscriptions: {len(active_subscriptions)}")
            print(f"   - Paused subscriptions: {len(paused_subscriptions)}")
            print(f"   - Canceled subscriptions: {len(canceled_subscriptions)}")
            print(f"   - Total subscriptions: {total_subscriptions}")
            print(f"   - Total orders: {len(orders)}")
            print(f"   - Recent orders: {len(recent_orders)}")
            print(f"   - Payment history entries: {len(payment_history)}")
            print(f"   - Total spent: ₹{total_spent}")
            
            # Show some sample data
            if recent_orders:
                print(f"\n📋 Sample Recent Orders:")
                for i, order in enumerate(recent_orders[:3]):
                    print(f"   {i+1}. Order #{order['id']}: ₹{order['amount']} ({order['payment_status']}) - {order['meal_plan_name']}")
            
            if payment_history:
                print(f"\n💳 Sample Payment History:")
                for i, payment in enumerate(payment_history[:3]):
                    print(f"   {i+1}. Payment {payment['payment_id']}: ₹{payment['amount']} ({payment['status']})")
            
            if active_subscriptions:
                print(f"\n📦 Active Subscriptions:")
                for i, sub in enumerate(active_subscriptions):
                    print(f"   {i+1}. Subscription #{sub.id}: {sub.meal_plan.name} ({sub.frequency.value}) - ₹{sub.price}")
            
            # Check if data is sufficient for profile display
            if len(orders) > 0 and len(payment_history) > 0:
                print(f"\n✅ Profile functionality test PASSED!")
                print(f"   - User has {len(orders)} orders and {len(payment_history)} payment records")
                print(f"   - Profile page should display transaction history correctly")
                return True
            else:
                print(f"\n⚠️ Profile functionality test INCOMPLETE!")
                print(f"   - User has {len(orders)} orders and {len(payment_history)} payment records")
                print(f"   - More test data may be needed")
                return False
            
        except Exception as e:
            print(f"❌ Error testing profile functionality: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return False

def main():
    """Main function"""
    print("🚀 Profile Functionality Test")
    print("=" * 50)
    
    if test_profile_functionality():
        print("\n🎉 Profile functionality is working correctly!")
        print("The profile page should now show all transaction data.")
    else:
        print("\n❌ Profile functionality test failed or incomplete")

if __name__ == "__main__":
    main() 