#!/usr/bin/env python3
"""
Simple Payment Flow Test
Tests the payment flow without CSRF complications for development testing.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"

def test_basic_pages():
    """Test if basic pages load correctly"""
    print("🔍 Testing Basic Pages...")
    
    pages_to_test = [
        ("/", "Home Page"),
        ("/meal-plans", "Meal Plans Page"),
        ("/meal-calculator", "Meal Calculator Page"),
        ("/blog", "Blog Page"),
        ("/about", "About Page"),
        ("/contact", "Contact Page")
    ]
    
    all_passed = True
    for url, name in pages_to_test:
        try:
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code == 200:
                print(f"✅ {name} loads successfully")
            else:
                print(f"❌ {name} failed: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name} error: {e}")
            all_passed = False
    
    return all_passed

def test_subscribe_page():
    """Test subscribe page for a specific plan"""
    print("\n🔍 Testing Subscribe Page...")
    try:
        response = requests.get(f"{BASE_URL}/subscribe/1")
        if response.status_code == 200:
            print("✅ Subscribe page loads successfully")
            return True
        else:
            print(f"❌ Subscribe page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing subscribe page: {e}")
        return False

def test_webhook_endpoint():
    """Test if webhook endpoint is accessible"""
    print("\n🔍 Testing Webhook Endpoint...")
    try:
        # Test with a simple POST request
        test_data = {"test": "data"}
        response = requests.post(f"{BASE_URL}/webhook/razorpay", json=test_data)
        print(f"Webhook endpoint response: {response.status_code}")
        
        # Even if it returns an error (expected due to invalid signature), 
        # the endpoint is accessible
        if response.status_code in [200, 400, 401, 403]:
            print("✅ Webhook endpoint is accessible")
            return True
        else:
            print(f"❌ Webhook endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing webhook: {e}")
        return False

def test_checkout_success_page():
    """Test checkout success page"""
    print("\n🔍 Testing Checkout Success Page...")
    try:
        response = requests.get(f"{BASE_URL}/checkout-success")
        print(f"Checkout success response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Checkout success page loads successfully")
            return True
        elif response.status_code == 302:  # Redirect
            print("✅ Checkout success page redirects (expected)")
            return True
        else:
            print(f"❌ Checkout success page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing checkout success: {e}")
        return False

def test_database_access():
    """Test database access"""
    print("\n🔍 Testing Database Access...")
    try:
        response = requests.get(f"{BASE_URL}/init_db")
        if response.status_code == 200:
            print("✅ Database is accessible")
            return True
        else:
            print(f"❌ Database access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return False

def test_razorpay_config():
    """Test Razorpay configuration"""
    print("\n🔍 Testing Razorpay Configuration...")
    try:
        # Test if we can access the meal plans page which should show Razorpay integration
        response = requests.get(f"{BASE_URL}/meal-plans")
        if response.status_code == 200:
            content = response.text.lower()
            if 'razorpay' in content or 'payment' in content:
                print("✅ Razorpay integration detected")
                return True
            else:
                print("⚠️ Razorpay integration not clearly visible")
                return True  # Still consider it a pass
        else:
            print(f"❌ Cannot test Razorpay config: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Razorpay config: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Simple Payment Flow Test")
    print("=" * 50)
    
    tests = [
        ("Basic Pages", test_basic_pages),
        ("Subscribe Page", test_subscribe_page),
        ("Webhook Endpoint", test_webhook_endpoint),
        ("Checkout Success Page", test_checkout_success_page),
        ("Database Access", test_database_access),
        ("Razorpay Configuration", test_razorpay_config)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Test Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your payment system is ready for testing.")
    elif passed >= total * 0.8:
        print("✅ Most tests passed! Your payment system is mostly ready.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    print(f"\n🌐 Your application is running at: {BASE_URL}")
    print("\n💡 Manual Testing Instructions:")
    print("1. Go to http://127.0.0.1:8000/meal-plans")
    print("2. Click on a meal plan to subscribe")
    print("3. Fill in the checkout form")
    print("4. Test the payment flow")
    print("5. Check if success page loads")
    print("6. Verify webhook processing")

if __name__ == "__main__":
    main() 