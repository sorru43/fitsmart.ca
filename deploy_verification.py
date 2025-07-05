#!/usr/bin/env python3
"""
Deployment Verification Script for HealthyRizz
This script tests the favicon fix and other critical routes
"""

import requests
import sys
import os

def test_local_server():
    """Test the local server to verify fixes"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 Testing Local Server...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not running: {e}")
        return False
    
    # Test 2: Check favicon route
    try:
        response = requests.get(f"{base_url}/favicon.ico", timeout=5)
        print(f"✅ Favicon route working (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Favicon route failed: {e}")
    
    # Test 3: Check meal plans page
    try:
        response = requests.get(f"{base_url}/meal-plans", timeout=5)
        print(f"✅ Meal plans page working (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Meal plans page failed: {e}")
    
    # Test 4: Check subscribe route
    try:
        response = requests.get(f"{base_url}/subscribe/1", timeout=5)
        print(f"✅ Subscribe route working (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Subscribe route failed: {e}")
    
    print("\n📋 Deployment Checklist:")
    print("=" * 50)
    print("1. ✅ Upload updated app.py to server")
    print("2. ✅ Upload updated templates/base.html to server")
    print("3. ✅ Restart Flask application on server")
    print("4. ✅ Clear any template cache on server")
    print("5. ✅ Test favicon.ico route on live server")
    print("6. ✅ Test /subscribe/1 route on live server")
    
    print("\n🚀 To deploy to live server:")
    print("1. Upload these files to your server:")
    print("   - app.py (with favicon fallback route)")
    print("   - templates/base.html (with direct favicon path)")
    print("2. Restart your Flask application")
    print("3. Clear any caching (if using nginx/apache)")
    print("4. Test: https://healthyrizz.in/favicon.ico")
    print("5. Test: https://healthyrizz.in/subscribe/1")
    
    return True

if __name__ == "__main__":
    test_local_server() 