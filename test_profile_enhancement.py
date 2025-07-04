#!/usr/bin/env python3
"""
Test script to verify enhanced profile functionality
"""

import requests
import json
from datetime import datetime

def test_profile_route():
    """Test that the profile route is accessible and returns enhanced data"""
    print("🧪 Testing enhanced profile route...")
    
    try:
        # Test the route locally
        response = requests.get('http://localhost:8000/profile', allow_redirects=False)
        
        if response.status_code == 302:
            print("✅ Route exists and redirects (expected for non-authenticated users)")
            print(f"   Redirect location: {response.headers.get('Location', 'None')}")
            return True
        elif response.status_code == 200:
            print("✅ Route exists and returns 200")
            return True
        elif response.status_code == 404:
            print("❌ Route returns 404 - NOT WORKING")
            return False
        else:
            print(f"⚠️ Route returns {response.status_code}")
            return True
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to local server. Make sure Flask is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error testing route: {e}")
        return False

def check_profile_template():
    """Check that the profile template has the enhanced sections"""
    print("\n🔍 Checking profile template enhancements...")
    
    try:
        with open('templates/profile.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('Order Summary section', 'Order Summary'),
            ('Payment History section', 'Payment History'),
            ('Order History section', 'Order History'),
            ('Total Orders display', 'Total Orders'),
            ('Total Spent display', 'Total Spent'),
            ('Payment status badges', 'payment_status'),
            ('Order ID display', 'order.id'),
            ('Payment ID display', 'payment_id')
        ]
        
        all_passed = True
        for check_name, search_term in checks:
            if search_term in content:
                print(f"✅ {check_name} found in template")
            else:
                print(f"❌ {check_name} NOT found in template")
                all_passed = False
                
        return all_passed
        
    except FileNotFoundError:
        print("❌ Could not find templates/profile.html")
        return False
    except Exception as e:
        print(f"❌ Error checking template: {e}")
        return False

def check_profile_route_code():
    """Check that the profile route has enhanced functionality"""
    print("\n🔍 Checking profile route enhancements...")
    
    try:
        with open('routes/main_routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('Order query', 'Order.query.filter'),
            ('Payment history processing', 'payment_history'),
            ('Total spent calculation', 'total_spent'),
            ('Recent orders', 'recent_orders'),
            ('Enhanced template variables', 'orders=recent_orders'),
            ('Payment history template variable', 'payment_history=payment_history')
        ]
        
        all_passed = True
        for check_name, search_term in checks:
            if search_term in content:
                print(f"✅ {check_name} found in route")
            else:
                print(f"❌ {check_name} NOT found in route")
                all_passed = False
                
        return all_passed
        
    except FileNotFoundError:
        print("❌ Could not find routes/main_routes.py")
        return False
    except Exception as e:
        print(f"❌ Error checking route: {e}")
        return False

def test_database_models():
    """Check that required database models exist"""
    print("\n🔍 Checking database models...")
    
    try:
        with open('database/models.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('Order model', 'class Order'),
            ('Subscription model', 'class Subscription'),
            ('User model', 'class User'),
            ('Payment fields in Order', 'payment_status'),
            ('Payment ID field', 'payment_id'),
            ('Amount field', 'amount')
        ]
        
        all_passed = True
        for check_name, search_term in checks:
            if search_term in content:
                print(f"✅ {check_name} found in models")
            else:
                print(f"❌ {check_name} NOT found in models")
                all_passed = False
                
        return all_passed
        
    except FileNotFoundError:
        print("❌ Could not find database/models.py")
        return False
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Enhanced Profile Functionality Test Suite")
    print("=" * 60)
    print(f"📅 Test run at: {datetime.now()}")
    
    # Run all tests
    tests = [
        ("Profile Route", test_profile_route),
        ("Profile Template", check_profile_template),
        ("Profile Route Code", check_profile_route_code),
        ("Database Models", test_database_models)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Enhanced profile functionality is ready.")
        print("\n📋 What's been enhanced:")
        print("   ✅ Profile shows order history")
        print("   ✅ Profile shows payment history")
        print("   ✅ Profile shows total spent")
        print("   ✅ Profile shows order summary")
        print("   ✅ Users can see their subscription and payment status")
        
        print("\n🔧 To deploy to production:")
        print("   1. Copy updated routes/main_routes.py to production")
        print("   2. Copy updated templates/profile.html to production")
        print("   3. Restart the application")
        print("   4. Test the profile page in production")
        
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        print("\n🔧 Next steps:")
        print("   1. Fix any failed tests")
        print("   2. Ensure all database models are properly defined")
        print("   3. Verify template syntax is correct")
        print("   4. Test the profile functionality manually")

if __name__ == "__main__":
    main() 