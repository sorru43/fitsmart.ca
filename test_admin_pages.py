#!/usr/bin/env python3
"""
Test admin pages to identify which ones are still returning 500 errors
"""

import requests
import sys

def test_admin_pages():
    base_url = "http://127.0.0.1:5001"
    
    pages_to_test = [
        ('/admin/dashboard', 'Dashboard'),
        ('/admin/users', 'Users'),
        ('/admin/meal-plans', 'Meal Plans'),
        ('/admin/notifications', 'Notifications'),
        ('/admin/orders', 'Orders'),
        ('/admin/coupons', 'Coupons'),
        ('/admin/banners', 'Banners'),
        ('/admin/newsletters', 'Newsletters'),
        ('/admin/blog', 'Blog'),
        ('/admin/subscriptions', 'Subscriptions')
    ]
    
    print("🔍 Testing HealthyRizz Admin Pages")
    print("=" * 50)
    
    working_pages = []
    broken_pages = []
    
    for page_url, page_name in pages_to_test:
        try:
            response = requests.get(f"{base_url}{page_url}", timeout=10)
            
            if response.status_code == 200:
                status = "✅ Working"
                working_pages.append(page_name)
            elif response.status_code == 302:
                status = "🔄 Redirect (needs login)"
            elif response.status_code == 500:
                status = "❌ 500 Error"
                broken_pages.append(page_name)
            else:
                status = f"⚠️  {response.status_code}"
                
            print(f"{page_name:<15} {page_url:<20} {status}")
            
        except requests.exceptions.ConnectionError:
            print(f"{page_name:<15} {page_url:<20} ❌ Connection failed (app not running?)")
            return False
        except Exception as e:
            print(f"{page_name:<15} {page_url:<20} ❌ Error: {e}")
            broken_pages.append(page_name)
    
    print("\n" + "=" * 50)
    print(f"✅ Working pages: {len(working_pages)}")
    print(f"❌ Broken pages: {len(broken_pages)}")
    
    if broken_pages:
        print(f"\n🔧 Pages still needing fixes:")
        for page in broken_pages:
            print(f"   - {page}")
        return False
    else:
        print(f"\n🎉 All admin pages are working correctly!")
        return True

if __name__ == "__main__":
    test_admin_pages() 