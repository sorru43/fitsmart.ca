#!/usr/bin/env python3
"""
Test if the HealthyRizz application is running
"""

import requests
import time

def test_application():
    """Test if the application is running"""
    print("🧪 Testing if HealthyRizz is running...")
    
    base_url = "http://localhost:8000"
    
    # Wait a moment for the app to start
    print("⏳ Waiting for application to start...")
    time.sleep(3)
    
    try:
        # Test main page
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Application is running!")
            print(f"📍 Main page: {base_url}")
            print(f"📍 Meal plans: {base_url}/meal-plans")
            print(f"📍 Admin panel: {base_url}/admin/dashboard")
            
            # Test meal plans page
            response = requests.get(f"{base_url}/meal-plans", timeout=5)
            if response.status_code == 200:
                print("✅ Meal plans page accessible")
            else:
                print(f"⚠️ Meal plans page returned {response.status_code}")
            
            return True
        else:
            print(f"❌ Application returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to application")
        print("   The application might not be running yet")
        return False
    except Exception as e:
        print(f"❌ Error testing application: {e}")
        return False

if __name__ == "__main__":
    test_application() 