#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Checkout Functionality
This script tests the checkout process to ensure everything is working.
"""

import requests
import json

def test_checkout_flow():
    """Test the complete checkout flow"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Checkout Flow...")
    
    # Test 1: Check if subscribe page loads
    print("\n1. Testing subscribe page...")
    try:
        response = requests.get(f"{base_url}/subscribe/4?frequency=weekly")
        if response.status_code == 200:
            print("✅ Subscribe page loads successfully")
        else:
            print(f"❌ Subscribe page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing subscribe page: {e}")
        return False
    
    # Test 2: Check if states are loaded
    print("\n2. Testing states loading...")
    try:
        response = requests.get(f"{base_url}/get-delivery-states")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('states'):
                print(f"✅ States loaded successfully: {len(data['states'])} states")
            else:
                print("❌ No states found")
        else:
            print(f"❌ States loading failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading states: {e}")
    
    # Test 3: Check if cities load for a state
    print("\n3. Testing cities loading...")
    try:
        response = requests.get(f"{base_url}/get-delivery-cities?state=Haryana")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('cities'):
                print(f"✅ Cities loaded successfully: {len(data['cities'])} cities")
            else:
                print("❌ No cities found")
        else:
            print(f"❌ Cities loading failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading cities: {e}")
    
    # Test 4: Check if areas load for a city
    print("\n4. Testing areas loading...")
    try:
        response = requests.get(f"{base_url}/get-delivery-areas?state=Haryana&city=Faridabad")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('areas'):
                print(f"✅ Areas loaded successfully: {len(data['areas'])} areas")
            else:
                print("❌ No areas found")
        else:
            print(f"❌ Areas loading failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading areas: {e}")
    
    # Test 5: Test checkout processing (mock data)
    print("\n5. Testing checkout processing...")
    try:
        checkout_data = {
            'plan_id': '4',
            'frequency': 'weekly',
            'customer_name': 'Test User',
            'customer_email': 'test@example.com',
            'customer_phone': '9876543210',
            'customer_address': 'Test Address',
            'customer_city': 'Faridabad',
            'customer_state': 'Haryana',
            'customer_area': 'Sector 15',
            'customer_pincode': '121001',
            'delivery_instructions': 'Test delivery',
            'total_amount': '1050.00',
            'csrf_token': 'test_token'
        }
        
        response = requests.post(f"{base_url}/process_checkout", data=checkout_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Checkout processing successful")
                print(f"   Order ID: {data.get('order_id', 'N/A')}")
                print(f"   Amount: {data.get('amount', 'N/A')}")
            else:
                print(f"❌ Checkout processing failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Checkout processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error in checkout processing: {e}")
    
    print("\n🎯 Checkout Flow Test Complete!")
    return True

if __name__ == "__main__":
    test_checkout_flow() 