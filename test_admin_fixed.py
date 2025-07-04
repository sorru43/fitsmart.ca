#!/usr/bin/env python3
"""
Test script to verify all admin routes are working properly after fixes
"""

import sys
import os
sys.path.append('.')

from main import app
from models import User
from extensions import db

def test_admin_routes():
    """Test all admin routes to ensure they work properly"""
    
    with app.test_client() as client:
        with app.app_context():
            print("🔧 Testing HealthyRizz Admin Panel Routes...")
            print("=" * 50)
            
            # Check if admin user exists
            admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
            if not admin_user:
                print("❌ Admin user not found!")
                return False
            
            print(f"✅ Admin user found: {admin_user.email}")
            
            # Login first
            login_response = client.post('/login', data={
                'email': 'admin@healthyrizz.in',
                'password': 'admin123'
            }, follow_redirects=True)
            
            if login_response.status_code != 200:
                print("❌ Login failed!")
                return False
            
            print("✅ Login successful")
            
            # Test all admin routes
            routes_to_test = [
                ('/admin/dashboard', 'Dashboard'),
                ('/admin/users', 'Users'),
                ('/admin/orders', 'Orders'),
                ('/admin/subscriptions', 'Subscriptions'),
                ('/admin/newsletters', 'Newsletters'),
                ('/admin/coupons', 'Coupons'),
                ('/admin/banners', 'Banners'),
                ('/admin/notifications', 'Notifications'),
                ('/admin/location-tree', 'Location Tree'),
                ('/admin/media', 'Media'),
                ('/admin/meal-plans', 'Meal Plans'),
                ('/admin/trial-requests', 'Trial Requests'),
                ('/admin/blog', 'Blog'),
                ('/admin/contact-inquiries', 'Contact Inquiries'),
                ('/admin/faqs', 'FAQs'),
                ('/admin/add-coupon', 'Add Coupon'),
                ('/admin/add-banner', 'Add Banner'),
            ]
            
            failed_routes = []
            success_count = 0
            
            for route, name in routes_to_test:
                try:
                    response = client.get(route)
                    if response.status_code == 200:
                        print(f"✅ {name} ({route}): OK")
                        success_count += 1
                    else:
                        print(f"❌ {name} ({route}): HTTP {response.status_code}")
                        failed_routes.append((route, name, response.status_code))
                except Exception as e:
                    print(f"❌ {name} ({route}): ERROR - {str(e)}")
                    failed_routes.append((route, name, f"Exception: {str(e)}"))
            
            print("=" * 50)
            print(f"✅ Successful routes: {success_count}/{len(routes_to_test)}")
            
            if failed_routes:
                print(f"❌ Failed routes: {len(failed_routes)}")
                for route, name, error in failed_routes:
                    print(f"   - {name}: {error}")
                return False
            else:
                print("🎉 All admin routes are working correctly!")
                return True

if __name__ == '__main__':
    success = test_admin_routes()
    sys.exit(0 if success else 1) 