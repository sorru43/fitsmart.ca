#!/usr/bin/env python3
"""
Simple script to check if all admin routes are properly defined
"""

import sys
sys.path.append('.')

from main import app

def check_admin_routes():
    """Check if all admin routes are properly defined"""
    
    with app.app_context():
        print("🔧 Checking HealthyRizz Admin Routes...")
        print("=" * 50)
        
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint and rule.endpoint.startswith('admin.'):
                routes.append((rule.rule, rule.endpoint))
        
        # Sort routes
        routes.sort()
        
        print(f"✅ Found {len(routes)} admin routes:")
        print("-" * 30)
        
        for route, endpoint in routes:
            print(f"  {route} -> {endpoint}")
        
        # Check for specific routes that were causing issues
        expected_routes = [
            'admin.admin_dashboard',
            'admin.admin_users', 
            'admin.admin_orders',
            'admin.admin_newsletters',
            'admin.admin_coupons',
            'admin.admin_banners',
            'admin.admin_add_coupon',
            'admin.admin_add_banner',
            'admin.admin_toggle_user_status',
            'admin.admin_toggle_admin_status',
            'admin.admin_delete_user',
        ]
        
        print("\n" + "=" * 50)
        print("🔍 Checking for required routes...")
        print("-" * 30)
        
        found_endpoints = [endpoint for route, endpoint in routes]
        missing_routes = []
        
        for expected in expected_routes:
            if expected in found_endpoints:
                print(f"✅ {expected}")
            else:
                print(f"❌ {expected} - MISSING!")
                missing_routes.append(expected)
        
        print("=" * 50)
        if missing_routes:
            print(f"❌ Missing routes: {len(missing_routes)}")
            return False
        else:
            print("🎉 All required admin routes are defined!")
            return True

if __name__ == '__main__':
    success = check_admin_routes()
    sys.exit(0 if success else 1) 