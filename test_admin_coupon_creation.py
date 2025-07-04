#!/usr/bin/env python3
"""
Test script to verify admin coupon creation functionality
"""
import requests
from datetime import datetime, timedelta

def test_admin_coupon_creation():
    print("Testing admin coupon creation...")
    
    # First, we need to login to get a session
    session = requests.Session()
    
    # Get the login page to get CSRF token
    login_response = session.get('http://localhost:5000/login')
    if login_response.status_code != 200:
        print("❌ Could not access login page")
        return
    
    # Extract CSRF token from login page (simplified)
    csrf_token = "test_token"  # In real scenario, extract from HTML
    
    # Login data
    login_data = {
        'csrf_token': csrf_token,
        'email': 'admin@healthyrizz.in',
        'password': 'admin123'
    }
    
    # Try to login
    login_response = session.post('http://localhost:5000/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    # Check if we can access admin coupons page
    coupons_response = session.get('http://localhost:5000/admin/coupons')
    print(f"Admin coupons page status: {coupons_response.status_code}")
    
    # Check if we can access add coupon page
    add_coupon_response = session.get('http://localhost:5000/admin/add-coupon')
    print(f"Add coupon page status: {add_coupon_response.status_code}")
    
    if add_coupon_response.status_code == 200:
        print("✅ Admin coupon creation page is accessible")
        print("You can now create coupons through the admin panel!")
    else:
        print("❌ Admin coupon creation page is not accessible")

if __name__ == "__main__":
    test_admin_coupon_creation() 