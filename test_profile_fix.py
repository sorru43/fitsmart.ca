#!/usr/bin/env python3
"""
Test script to verify the profile route works correctly
"""

from app import create_app
from database.models import User, Order, MealPlan
from flask_login import login_user

def test_profile_route():
    """Test the profile route with a logged-in user"""
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            # Get admin user
            admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
            if not admin_user:
                print("❌ Admin user not found")
                return False
            
            print(f"✅ Found admin user: {admin_user.email} (ID: {admin_user.id})")
            
            # Login the user
            with client.session_transaction() as sess:
                sess['_user_id'] = admin_user.id
                sess['_fresh'] = True
            
            # Test the profile route
            response = client.get('/profile')
            print(f"Profile route status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Profile route working correctly")
                
                # Check if the response contains order information
                response_text = response.get_data(as_text=True)
                if '₹' in response_text and ('Order' in response_text or 'order' in response_text):
                    print("✅ Profile page contains order information")
                    return True
                else:
                    print("❌ Profile page doesn't contain order information")
                    return False
            else:
                print(f"❌ Profile route failed with status {response.status_code}")
                return False

def test_order_query():
    """Test the order query directly"""
    app = create_app()
    
    with app.app_context():
        admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
        if not admin_user:
            print("❌ Admin user not found")
            return False
        
        print(f"✅ Testing order query for user {admin_user.id}")
        
        # Test the exact query from profile route
        try:
            orders = Order.query.join(MealPlan).filter(
                Order.user_id == admin_user.id
            ).order_by(Order.created_at.desc()).all()
            
            print(f"✅ Found {len(orders)} orders")
            
            # Test meal plan access
            for i, order in enumerate(orders[:3]):
                try:
                    meal_plan_name = order.meal_plan.name if order.meal_plan else 'N/A'
                    print(f"  Order {order.id}: ₹{order.amount} - {meal_plan_name}")
                except Exception as e:
                    print(f"  Order {order.id}: ₹{order.amount} - Error: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Order query failed: {str(e)}")
            return False

if __name__ == '__main__':
    print("🧪 Testing Profile Route Fix")
    print("=" * 40)
    
    # Test order query first
    print("\n1. Testing order query...")
    query_success = test_order_query()
    
    # Test profile route
    print("\n2. Testing profile route...")
    route_success = test_profile_route()
    
    if query_success and route_success:
        print("\n✅ All tests passed! Profile route should work correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.") 