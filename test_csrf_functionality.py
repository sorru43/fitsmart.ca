#!/usr/bin/env python3
"""
Test CSRF functionality
"""
import requests
import re

def test_csrf():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing CSRF Functionality")
    print("=" * 40)
    
    # Test 1: Get CSRF token from page
    try:
        response = requests.get(f"{base_url}/meal-plans")
        if response.status_code == 200:
            print("✅ Meal plans page accessible")
            
            # Extract CSRF token
            csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRF token found: {csrf_token[:20]}...")
                
                # Test 2: Submit form with CSRF token
                test_data = {
                    'csrf_token': csrf_token,
                    'plan_id': '1',
                    'customer_name': 'Test User',
                    'customer_email': 'test@example.com'
                }
                
                response = requests.post(f"{base_url}/process_checkout", data=test_data)
                print(f"✅ Form submission test completed: {response.status_code}")
                
            else:
                print("❌ CSRF token not found in page")
                
        else:
            print(f"❌ Meal plans page returned: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing CSRF: {e}")

if __name__ == "__main__":
    test_csrf()
