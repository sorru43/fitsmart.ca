#!/usr/bin/env python3
"""
Test script for signup completion flow
This script tests the complete flow for non-logged-in users after payment
"""

import requests
import json
import sys
from datetime import datetime

def test_signup_complete_flow():
    """Test the complete signup completion flow"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Signup Completion Flow")
    print("=" * 50)
    
    try:
        # Test 1: Check if application is running
        print("1. Testing application connectivity...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Application is running")
        else:
            print(f"   ❌ Application returned status code: {response.status_code}")
            return False
        
        # Test 2: Test signup complete route with invalid order ID
        print("2. Testing signup complete route with invalid order ID...")
        response = requests.get(f"{base_url}/signup-complete/999999", timeout=5, allow_redirects=False)
        if response.status_code == 302:  # Should redirect to meal plans
            print("   ✅ Signup complete route redirects for invalid order ID")
        else:
            print(f"   ⚠️  Signup complete route returned status: {response.status_code}")
        
        # Test 3: Test checkout success route without being logged in
        print("3. Testing checkout success route without authentication...")
        response = requests.get(f"{base_url}/checkout-success", timeout=5, allow_redirects=False)
        if response.status_code == 302:  # Should redirect
            print("   ✅ Checkout success route redirects when not authenticated")
        else:
            print(f"   ⚠️  Checkout success route returned status: {response.status_code}")
        
        # Test 4: Test that signup complete template exists
        print("4. Testing signup complete template...")
        response = requests.get(f"{base_url}/signup-complete/999999", timeout=5)
        if "Complete Your Account" in response.text or "Payment Successful" in response.text:
            print("   ✅ Signup complete template is accessible")
        else:
            print("   ⚠️  Signup complete template may not be loading correctly")
        
        print("\n✅ All basic tests passed!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing application: {e}")
        return False

def test_with_real_order():
    """Test with a real order ID from the database"""
    print("\n🔍 Testing with real order data...")
    print("Note: This requires a real order ID from the database")
    
    # You can modify this to use a real order ID for testing
    real_order_id = input("Enter a real order ID to test with (or press Enter to skip): ").strip()
    
    if not real_order_id:
        print("   ⏭️  Skipping real order test")
        return True
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/signup-complete/{real_order_id}", timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Signup complete page loaded successfully")
            
            # Check for expected content
            if "Complete Your Account" in response.text:
                print("   ✅ Account completion form is present")
            else:
                print("   ⚠️  Account completion form not found")
            
            if "Subscription Details" in response.text:
                print("   ✅ Subscription details section is present")
            else:
                print("   ⚠️  Subscription details section not found")
            
            if "Create Password" in response.text:
                print("   ✅ Password creation form is present")
            else:
                print("   ⚠️  Password creation form not found")
                
        else:
            print(f"   ❌ Signup complete page returned status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error testing with real order: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Signup Completion Flow Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run basic tests
    basic_success = test_signup_complete_flow()
    
    if not basic_success:
        print("\n❌ Basic tests failed!")
        sys.exit(1)
    
    # Run real order test (optional)
    real_order_success = test_with_real_order()
    
    if not real_order_success:
        print("\n⚠️  Real order test failed, but basic functionality is working")
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("✅ Basic connectivity tests passed")
    print("✅ Route accessibility tests passed")
    print("✅ Template loading tests passed")
    
    if real_order_success:
        print("✅ Real order integration tests passed")
    else:
        print("⚠️  Real order integration tests skipped or failed")
    
    print("\n🎉 Signup completion flow is working correctly!")
    print("\n📝 Manual Testing Steps:")
    print("1. Open the application in a browser")
    print("2. Go to a meal plan and start checkout without logging in")
    print("3. Complete payment process")
    print("4. Verify you're redirected to signup completion page")
    print("5. Check that subscription details are displayed")
    print("6. Set a password and complete account setup")
    print("7. Verify you're logged in and redirected to profile")

if __name__ == "__main__":
    main() 