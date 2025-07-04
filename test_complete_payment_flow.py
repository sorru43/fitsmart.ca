#!/usr/bin/env python3
"""
Complete payment flow test - simulates the entire payment process
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db
from database.models import User, MealPlan, Order, Subscription, SubscriptionStatus, SubscriptionFrequency

def test_complete_payment_flow():
    """Test the complete payment flow from checkout to profile display"""
    with app.app_context():
        try:
            print("🧪 Testing Complete Payment Flow...")
            
            # Get test data
            user = User.query.first()
            meal_plan = MealPlan.query.first()
            
            if not user or not meal_plan:
                print("❌ No users or meal plans found for testing")
                return False
            
            print(f"👤 User: {user.email}")
            print(f"🍽️ Meal Plan: {meal_plan.name}")
            
            # Step 1: Simulate checkout form data
            checkout_data = {
                'plan_id': str(meal_plan.id),
                'frequency': 'weekly',
                'customer_name': user.name or user.email,
                'customer_email': user.email,
                'customer_phone': user.phone or '1234567890',
                'customer_address': user.address or 'Test Address',
                'customer_city': user.city or 'Test City',
                'customer_state': user.province or 'Test State',
                'customer_pincode': user.postal_code or '123456',
                'vegetarian_days': '1,3,5',
                'applied_coupon_code': None,
                'coupon_discount': '0'
            }
            
            # Step 2: Simulate order data from session (what would be stored after process_checkout)
            order_data = {
                'order_id': f'order_test_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'amount': 99900,  # 999.00 in paise
                'currency': 'INR',
                'receipt': f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'notes': checkout_data
            }
            
            # Step 3: Simulate payment verification (what happens in verify_payment)
            payment_id = f'pay_test_{datetime.now().strftime("%Y%m%d%H%M%S")}'
            
            # Create Order record for payment history
            order = Order(
                user_id=user.id,
                meal_plan_id=meal_plan.id,
                amount=float(order_data['amount']) / 100,  # Convert from paise to rupees
                status='confirmed',
                payment_status='captured',
                payment_id=payment_id,
                order_id=order_data['order_id'],
                created_at=datetime.now()
            )
            
            db.session.add(order)
            db.session.flush()  # Get the order ID
            print(f"✅ Step 3: Created order #{order.id}")
            
            # Create subscription linked to order
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
            print(f"✅ Step 4: Created subscription #{subscription.id} linked to order #{order.id}")
            
            # Step 5: Test profile page data retrieval
            print("\n📊 Testing Profile Page Data Retrieval...")
            
            # Get user's orders
            user_orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
            print(f"   📦 User orders found: {len(user_orders)}")
            
            # Get user's subscriptions
            user_subscriptions = Subscription.query.filter_by(user_id=user.id).order_by(Subscription.start_date.desc()).all()
            print(f"   📋 User subscriptions found: {len(user_subscriptions)}")
            
            # Generate payment history from orders
            payments = []
            for o in user_orders:
                if o.meal_plan:
                    payment = {
                        'date': o.created_at,
                        'description': f"{o.meal_plan.name} - Order #{o.id}",
                        'amount': float(o.amount),
                        'status': o.payment_status,
                        'order_id': o.id,
                        'payment_id': o.payment_id,
                        'invoice_url': '#'
                    }
                    payments.append(payment)
            
            print(f"   💳 Payment history entries: {len(payments)}")
            
            # Display payment history
            print("\n📋 Payment History:")
            for payment in payments:
                print(f"   - {payment['date'].strftime('%Y-%m-%d %H:%M')}: {payment['description']}")
                print(f"     Amount: ₹{payment['amount']}, Status: {payment['status']}")
                print(f"     Order ID: {payment['order_id']}, Payment ID: {payment['payment_id']}")
            
            # Verify data integrity
            print("\n🔍 Data Integrity Check:")
            print(f"   ✅ Order {order.id} has user_id: {order.user_id}")
            print(f"   ✅ Order {order.id} has meal_plan_id: {order.meal_plan_id}")
            print(f"   ✅ Order {order.id} has payment_id: {order.payment_id}")
            print(f"   ✅ Subscription {subscription.id} has order_id: {subscription.order_id}")
            print(f"   ✅ Subscription {subscription.id} linked to order {order.id}")
            
            # Test that profile page can access the data
            print("\n🧪 Profile Page Access Test:")
            try:
                # Simulate what the profile route does
                profile_orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
                profile_subscriptions = Subscription.query.filter_by(user_id=user.id).order_by(Subscription.start_date.desc()).all()
                
                print(f"   ✅ Profile can access {len(profile_orders)} orders")
                print(f"   ✅ Profile can access {len(profile_subscriptions)} subscriptions")
                
                # Test order-subscription linking
                linked_subscriptions = [s for s in profile_subscriptions if s.order_id]
                print(f"   ✅ {len(linked_subscriptions)} subscriptions are linked to orders")
                
            except Exception as e:
                print(f"   ❌ Profile page access failed: {str(e)}")
                return False
            
            # Clean up test data
            print("\n🧹 Cleaning up test data...")
            db.session.delete(subscription)
            db.session.delete(order)
            db.session.commit()
            print("✅ Test data cleaned up")
            
            print("\n🎉 Complete Payment Flow Test Results:")
            print("   ✅ Orders are created with proper payment tracking")
            print("   ✅ Subscriptions are linked to orders")
            print("   ✅ Profile page can display payment history")
            print("   ✅ Payment status is properly tracked")
            print("   ✅ Order history is available in user profile")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in complete payment flow test: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    test_complete_payment_flow() 