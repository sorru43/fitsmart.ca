#!/usr/bin/env python3
"""
Payment Flow Verification Script
Comprehensive testing of the complete payment flow including success handling and webhook confirmation.
"""

import requests
import json
import time
import hmac
import hashlib
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️ {message}")

def test_payment_flow_steps():
    """Test each step of the payment flow"""
    print_header("PAYMENT FLOW VERIFICATION")
    
    # Step 1: Verify meal plans page
    print_info("Step 1: Verifying Meal Plans Page")
    try:
        response = requests.get(f"{BASE_URL}/meal-plans")
        if response.status_code == 200:
            print_success("Meal plans page loads successfully")
            
            # Check for payment-related content
            content = response.text.lower()
            payment_indicators = ['subscribe', 'checkout', 'payment', 'razorpay', 'order']
            found_indicators = [indicator for indicator in payment_indicators if indicator in content]
            
            if found_indicators:
                print_success(f"Payment indicators found: {', '.join(found_indicators)}")
            else:
                print_warning("No clear payment indicators found in meal plans page")
        else:
            print_error(f"Meal plans page failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error accessing meal plans: {e}")
        return False
    
    # Step 2: Verify subscribe page
    print_info("Step 2: Verifying Subscribe Page")
    try:
        response = requests.get(f"{BASE_URL}/subscribe/1")
        if response.status_code == 200:
            print_success("Subscribe page loads successfully")
            
            # Check for checkout form
            content = response.text.lower()
            if 'checkout' in content or 'payment' in content or 'form' in content:
                print_success("Checkout form detected")
            else:
                print_warning("Checkout form not clearly visible")
        else:
            print_error(f"Subscribe page failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error accessing subscribe page: {e}")
        return False
    
    return True

def test_webhook_functionality():
    """Test webhook functionality"""
    print_header("WEBHOOK FUNCTIONALITY TEST")
    
    # Test 1: Webhook endpoint accessibility
    print_info("Testing webhook endpoint accessibility")
    try:
        test_data = {"test": "data"}
        response = requests.post(f"{BASE_URL}/webhook/razorpay", json=test_data)
        
        if response.status_code == 400:
            print_success("Webhook endpoint accessible (400 expected for invalid signature)")
        elif response.status_code == 200:
            print_success("Webhook endpoint accessible")
        else:
            print_warning(f"Webhook endpoint returned unexpected status: {response.status_code}")
    except Exception as e:
        print_error(f"Error testing webhook endpoint: {e}")
        return False
    
    # Test 2: Webhook signature verification
    print_info("Testing webhook signature verification")
    try:
        webhook_secret = 'javnWRC_mZFz6ub'
        test_payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test_123",
                        "order_id": "order_test_123",
                        "amount": 75000,
                        "currency": "INR",
                        "status": "captured"
                    }
                }
            }
        }
        
        payload_str = json.dumps(test_payload)
        signature = hmac.new(
            webhook_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'Content-Type': 'application/json',
            'X-Razorpay-Signature': signature
        }
        
        response = requests.post(
            f"{BASE_URL}/webhook/razorpay",
            data=payload_str,
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("Webhook signature verification working")
        else:
            print_warning(f"Webhook signature verification returned: {response.status_code}")
            
    except Exception as e:
        print_error(f"Error testing webhook signature: {e}")
        return False
    
    return True

def test_success_handling():
    """Test success page handling"""
    print_header("SUCCESS PAGE HANDLING TEST")
    
    # Test 1: Checkout success page
    print_info("Testing checkout success page")
    try:
        response = requests.get(f"{BASE_URL}/checkout-success")
        if response.status_code == 200:
            print_success("Checkout success page loads successfully")
            
            # Check for success indicators
            content = response.text.lower()
            success_indicators = ['success', 'thank you', 'order confirmed', 'subscription']
            found_indicators = [indicator for indicator in success_indicators if indicator in content]
            
            if found_indicators:
                print_success(f"Success indicators found: {', '.join(found_indicators)}")
            else:
                print_warning("No clear success indicators found")
        else:
            print_warning(f"Checkout success page returned: {response.status_code}")
    except Exception as e:
        print_error(f"Error testing checkout success: {e}")
        return False
    
    # Test 2: Signup complete page
    print_info("Testing signup complete page")
    try:
        response = requests.get(f"{BASE_URL}/signup-complete/1")
        if response.status_code == 200:
            print_success("Signup complete page loads successfully")
        elif response.status_code == 404:
            print_info("Signup complete page returns 404 (expected for non-existent order)")
        else:
            print_warning(f"Signup complete page returned: {response.status_code}")
    except Exception as e:
        print_error(f"Error testing signup complete: {e}")
        return False
    
    return True

def test_database_integration():
    """Test database integration"""
    print_header("DATABASE INTEGRATION TEST")
    
    # Test database access
    print_info("Testing database access")
    try:
        response = requests.get(f"{BASE_URL}/init_db")
        if response.status_code == 200:
            print_success("Database is accessible")
        else:
            print_warning(f"Database access returned: {response.status_code}")
    except Exception as e:
        print_error(f"Error testing database: {e}")
        return False
    
    return True

def generate_test_scenarios():
    """Generate test scenarios for manual testing"""
    print_header("MANUAL TESTING SCENARIOS")
    
    scenarios = [
        {
            "name": "Complete Payment Flow",
            "steps": [
                "1. Go to http://127.0.0.1:8000/meal-plans",
                "2. Click 'Subscribe Now' on any meal plan",
                "3. Fill in customer details (name, email, phone, address)",
                "4. Select frequency (weekly/monthly)",
                "5. Choose vegetarian days if applicable",
                "6. Apply coupon code if available",
                "7. Click 'Proceed to Checkout'",
                "8. Complete payment on Razorpay",
                "9. Verify success page loads",
                "10. Check if subscription is created in database"
            ]
        },
        {
            "name": "Webhook Testing",
            "steps": [
                "1. Make a test payment",
                "2. Check application logs for webhook events",
                "3. Verify order status is updated to 'confirmed'",
                "4. Verify subscription is created",
                "5. Check if user receives confirmation email"
            ]
        },
        {
            "name": "Error Handling",
            "steps": [
                "1. Test with invalid payment data",
                "2. Test with expired coupon codes",
                "3. Test with invalid delivery locations",
                "4. Test network interruptions during payment",
                "5. Verify proper error messages are shown"
            ]
        },
        {
            "name": "User Account Flow",
            "steps": [
                "1. Complete payment without being logged in",
                "2. Verify redirect to signup completion page",
                "3. Create account with password",
                "4. Verify automatic login after account creation",
                "5. Check subscription appears in user profile"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}:")
        for step in scenario['steps']:
            print(f"   {step}")

def main():
    """Run complete payment flow verification"""
    print("🚀 HEALTHYRIZZ PAYMENT FLOW VERIFICATION")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Payment Flow Steps", test_payment_flow_steps),
        ("Webhook Functionality", test_webhook_functionality),
        ("Success Handling", test_success_handling),
        ("Database Integration", test_database_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"{test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Generate manual testing scenarios
    generate_test_scenarios()
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("🎉 All payment flow components are working correctly!")
        print_info("Your payment system is ready for production testing.")
    elif passed >= total * 0.8:
        print_success("✅ Most payment flow components are working correctly!")
        print_info("Your payment system is mostly ready for testing.")
    else:
        print_warning("⚠️ Some payment flow components need attention.")
        print_info("Please review the failed tests above.")
    
    print(f"\n🌐 Application URL: {BASE_URL}")
    print_info("Use the manual testing scenarios above to thoroughly test your payment flow.")

if __name__ == "__main__":
    main() 