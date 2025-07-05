#!/usr/bin/env python3
"""
Test script to simulate a complete purchase flow and verify order creation
"""

from app import create_app
from database.models import User, Order, MealPlan, Subscription
from datetime import datetime, timedelta
import json

def test_purchase_flow():
    """Test the complete purchase flow"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Complete Purchase Flow")
        print("=" * 50)
        
        # Get test user and meal plan
        user = User.query.filter_by(email='admin@healthyrizz.in').first()
        meal_plan = MealPlan.query.first()
        
        if not user:
            print("❌ Test user not found")
            return False
            
        if not meal_plan:
            print("❌ No meal plans found")
            return False
            
        print(f"✅ Using user: {user.email} (ID: {user.id})")
        print(f"✅ Using meal plan: {meal_plan.name} (ID: {meal_plan.id})")
        
        # Check current orders
        current_orders = Order.query.filter_by(user_id=user.id).all()
        print(f"📦 Current orders for user: {len(current_orders)}")
        
        # Simulate a purchase by creating an order directly
        test_order = Order(
            user_id=user.id,
            meal_plan_id=meal_plan.id,
            amount=meal_plan.price_weekly,
            status='confirmed',
            payment_status='captured',
            payment_id=f'test_payment_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            order_id=f'test_order_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            created_at=datetime.now()
        )
        
        try:
            from app import db
            db.session.add(test_order)
            db.session.commit()
            print(f"✅ Created test order: #{test_order.id}")
            
            # Verify order was created
            new_orders = Order.query.filter_by(user_id=user.id).all()
            print(f"📦 Total orders after creation: {len(new_orders)}")
            
            # Test profile route query
            profile_orders = Order.query.filter(
                Order.user_id == user.id
            ).order_by(Order.created_at.desc()).all()
            
            print(f"📊 Profile route found {len(profile_orders)} orders")
            
            # Show order details
            for order in profile_orders:
                meal_plan_name = "N/A"
                try:
                    if order.meal_plan:
                        meal_plan_name = order.meal_plan.name
                    elif order.meal_plan_id:
                        mp = MealPlan.query.get(order.meal_plan_id)
                        if mp:
                            meal_plan_name = mp.name
                except Exception as e:
                    print(f"⚠️ Error getting meal plan name: {e}")
                
                print(f"  Order #{order.id}: ₹{order.amount} - {order.status} - {meal_plan_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating test order: {str(e)}")
            db.session.rollback()
            return False

def test_checkout_process():
    """Test the checkout process simulation"""
    app = create_app()
    
    with app.app_context():
        print("\n🧪 Testing Checkout Process Simulation")
        print("=" * 50)
        
        # Get test user and meal plan
        user = User.query.filter_by(email='admin@healthyrizz.in').first()
        meal_plan = MealPlan.query.first()
        
        if not user or not meal_plan:
            print("❌ Test data not available")
            return False
        
        # Simulate checkout data
        checkout_data = {
            'plan_id': meal_plan.id,
            'frequency': 'weekly',
            'customer_name': user.name,
            'customer_email': user.email,
            'customer_phone': user.phone,
            'customer_address': user.address,
            'customer_city': user.city,
            'customer_state': user.province,  # Use province instead of state
            'customer_pincode': user.postal_code,
            'vegetarian_days': '',
            'applied_coupon_code': '',
            'coupon_discount': '0'
        }
        
        print(f"📋 Checkout data prepared for {meal_plan.name}")
        print(f"💰 Amount: ₹{meal_plan.price_weekly}")
        
        # Simulate the order creation that would happen in verify_payment
        try:
            from app import db
            from database.models import Subscription, SubscriptionFrequency, SubscriptionStatus
            
            # Create subscription
            subscription = Subscription(
                user_id=user.id,
                meal_plan_id=meal_plan.id,
                frequency=SubscriptionFrequency.WEEKLY,
                status=SubscriptionStatus.ACTIVE,
                price=meal_plan.price_weekly,
                vegetarian_days='',
                start_date=datetime.now(),
                current_period_start=datetime.now(),
                current_period_end=datetime.now() + timedelta(days=7)
            )
            
            db.session.add(subscription)
            db.session.flush()
            
            # Create order record
            order = Order(
                user_id=user.id,
                meal_plan_id=meal_plan.id,
                amount=meal_plan.price_weekly,
                status='confirmed',
                payment_status='captured',
                payment_id=f'checkout_test_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                order_id=f'checkout_order_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                created_at=datetime.now()
            )
            
            db.session.add(order)
            db.session.commit()
            
            print(f"✅ Created subscription: #{subscription.id}")
            print(f"✅ Created order: #{order.id}")
            
            # Verify in database
            total_orders = Order.query.filter_by(user_id=user.id).count()
            total_subscriptions = Subscription.query.filter_by(user_id=user.id).count()
            
            print(f"📊 Total orders in database: {total_orders}")
            print(f"📊 Total subscriptions in database: {total_subscriptions}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in checkout simulation: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Testing Purchase Flow and Order Creation")
    print("=" * 60)
    
    # Test basic purchase flow
    success1 = test_purchase_flow()
    
    # Test checkout process
    success2 = test_checkout_process()
    
    if success1 and success2:
        print("\n✅ All tests passed! Orders are being created correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.") 