#!/usr/bin/env python3
"""
Test script to verify coupon functionality
"""
import requests
import json

def test_coupon_validation():
    print("Testing coupon validation...")
    
    # Test data
    test_data = {
        'coupon_code': 'TEST10',
        'plan_id': 3,
        'frequency': 'weekly'
    }
    
    try:
        response = requests.post('http://localhost:5000/validate_coupon', 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print("✅ Coupon validation successful!")
                    print(f"Discount Amount: ₹{data.get('discount_amount', 0)}")
                    print(f"Message: {data.get('message', '')}")
                else:
                    print(f"❌ Coupon validation failed: {data.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ Invalid JSON response: {e}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_coupon_validation() 