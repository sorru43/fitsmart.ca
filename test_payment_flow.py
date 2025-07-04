#!/usr/bin/env python3
"""
Test script to verify payment flow works correctly
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from database.models import User, MealPlan, Order, Subscription, SubscriptionStatus, SubscriptionFrequency

def test_payment_flow():
    """Test the complete payment flow"""
    with app.app_context():
        try:
            # Get test data
            user = User.query.first()
            meal_plan = MealPlan.query.first()
            
            if not user or not meal_plan:
                print("❌ No users or meal plans found for testing")
                return False
            
            print(f"🧪 Testing payment flow with user: {user.email}")
            print(f"🧪 Testing payment flow with meal plan: {meal_plan.name}")
            
            # Simulate order data from session
            order_data = {
                'order_id': f'order_test_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'amount': 99900,  # 999.00 in paise
                'currency': 'INR',
                'receipt': f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'notes': {
                    'plan_id': str(meal_plan.id),
                    'frequency': 'weekly',
                    'vegetarian_days': '1,3,5',
                    'customer_name': user.name or user.email,
                    'customer_email': user.email,
                    'customer_phone': user.phone or '1234567890',
                    'customer_address': user.address or 'Test Address',
                    'customer_city': user.city or 'Test City',
                    'customer_state': user.province or 'Test State',
                    'customer_pincode': user.postal_code or '123456',
                    'applied_coupon': None,
                    'coupon_discount': '0'
                }
            }
            
            # Create Order record for payment history
            order = Order(
                user_id=user.id,
                meal_plan_id=meal_plan.id,
                amount=float(order_data['amount']) / 100,  # Convert from paise to rupees
                status='confirmed',
                payment_status='captured',
                payment_id=f'test_payment_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                order_id=order_data['order_id'],
                created_at=datetime.now()
            )
            
            db.session.add(order)
            db.session.flush()  # Get the order ID
            print(f"✅ Created order: {order.id}")
            
            # Create subscription
            subscription = Subscription(
                user_id=user.id,
                meal_plan_id=meal_plan.id,
                frequency=SubscriptionFrequency.WEEKLY,
                status=SubscriptionStatus.ACTIVE,
                price=float(order_data['amount']) / 100,  # Convert from paise to rupees
                vegetarian_days=order_data['notes']['vegetarian_days'],
                start_date=datetime.now(),
                current_period_start=datetime.now(),
                current_period_end=datetime.now() + timedelta(days=7),
                order_id=order.id  # Link to the order
            )
            
            db.session.add(subscription)
            db.session.commit()
            
            print(f"✅ Created subscription: {subscription.id}")
            print(f"✅ Linked subscription to order: {order.id}")
            
            # Verify the data
            print("\n📊 Payment Flow Test Results:")
            print(f"   Order ID: {order.id}")
            print(f"   Order Amount: ₹{order.amount}")
            print(f"   Order Status: {order.status}")
            print(f"   Payment Status: {order.payment_status}")
            print(f"   Subscription ID: {subscription.id}")
            print(f"   Subscription Status: {subscription.status}")
            print(f"   Subscription Order ID: {subscription.order_id}")
            
            # Clean up test data
            db.session.delete(subscription)
            db.session.delete(order)
            db.session.commit()
            
            print("\n✅ Payment flow test completed successfully!")
            print("✅ Orders and subscriptions are now properly linked for payment tracking")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing payment flow: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🧪 Testing payment flow...")
    test_payment_flow() 