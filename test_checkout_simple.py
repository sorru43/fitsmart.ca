#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Checkout Test for Windows
This script tests the checkout process to ensure everything is working.
"""

import requests
import json

def test_checkout():
    """Test the checkout functionality"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Checkout Functionality...")
    
    # Test 1: Check if subscribe page loads
    print("\n1. Testing subscribe page...")
    try:
        response = requests.get(f"{base_url}/subscribe/4?frequency=weekly")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Subscribe page loads successfully")
            # Check if total_amount is in the response
            if "total_amount" in response.text:
                print("✅ total_amount is present in the page")
            else:
                print("❌ total_amount is missing from the page")
        else:
            print(f"❌ Subscribe page failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error accessing subscribe page: {e}")
    
    # Test 2: Check if states are loaded
    print("\n2. Testing states loading...")
    try:
        response = requests.get(f"{base_url}/get-delivery-states")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('states'):
                print(f"✅ States loaded successfully: {len(data['states'])} states")
                for state in data['states']:
                    print(f"   - {state['name']}")
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
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('cities'):
                print(f"✅ Cities loaded successfully: {len(data['cities'])} cities")
                for city in data['cities']:
                    print(f"   - {city['name']}")
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
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('areas'):
                print(f"✅ Areas loaded successfully: {len(data['areas'])} areas")
                for area in data['areas']:
                    print(f"   - {area['name']}")
            else:
                print("❌ No areas found")
        else:
            print(f"❌ Areas loading failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading areas: {e}")
    
    print("\n🎯 Checkout Test Complete!")
    print("\n📝 Next Steps:")
    print("1. Open your browser and go to: http://localhost:5000/meal-plans")
    print("2. Click on a meal plan to subscribe")
    print("3. Fill in the checkout form with the cascading dropdowns")
    print("4. Test the payment process")

if __name__ == "__main__":
    test_checkout() 