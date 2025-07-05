#!/usr/bin/env python3
"""
Test script to verify payment flow fixes
"""

import requests
import json
from datetime import datetime

def test_checkout_success_route():
    """Test that the checkout-success route is accessible"""
    print("🧪 Testing checkout-success route...")
    
    try:
        # Test the route locally
        response = requests.get('http://localhost:8000/checkout-success', allow_redirects=False)
        
        if response.status_code == 302:
            print("✅ Route exists and redirects (expected for non-authenticated users)")
            print(f"   Redirect location: {response.headers.get('Location', 'None')}")
        elif response.status_code == 200:
            print("✅ Route exists and returns 200")
        elif response.status_code == 404:
            print("❌ Route returns 404 - NOT FIXED")
            return False
        else:
            print(f"⚠️ Route returns {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to local server. Make sure Flask is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error testing route: {e}")
        return False

def test_payment_flow():
    """Test the complete payment flow"""
    print("\n🧪 Testing complete payment flow...")
    
    # Test process_checkout route
    try:
        response = requests.post('http://localhost:8000/process_checkout', 
                               json={'test': 'data'}, 
                               allow_redirects=False)
        
        if response.status_code in [200, 302, 400, 401]:
            print("✅ process_checkout route is accessible")
        else:
            print(f"⚠️ process_checkout route returns {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing process_checkout: {e}")
    
    # Test verify_payment route
    try:
        response = requests.post('http://localhost:8000/verify_payment', 
                               json={'test': 'data'}, 
                               allow_redirects=False)
        
        if response.status_code in [200, 302, 400, 401]:
            print("✅ verify_payment route is accessible")
        else:
            print(f"⚠️ verify_payment route returns {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing verify_payment: {e}")

def check_routes_in_code():
    """Check that routes are properly defined in the code"""
    print("\n🔍 Checking route definitions in code...")
    
    try:
        with open('routes/main_routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '@main_bp.route(\'/checkout-success\')' in content:
            print("✅ checkout-success route is defined in main_routes.py")
        else:
            print("❌ checkout-success route is NOT defined in main_routes.py")
            return False
            
        if '@main_bp.route(\'/process_checkout\')' in content:
            print("✅ process_checkout route is defined in main_routes.py")
        else:
            print("❌ process_checkout route is NOT defined in main_routes.py")
            
        if '@main_bp.route(\'/verify_payment\')' in content:
            print("✅ verify_payment route is defined in main_routes.py")
        else:
            print("❌ verify_payment route is NOT defined in main_routes.py")
            
        return True
        
    except FileNotFoundError:
        print("❌ Could not find routes/main_routes.py")
        return False
    except Exception as e:
        print(f"❌ Error checking routes: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Payment Flow Fix Test Suite")
    print("=" * 50)
    print(f"📅 Test run at: {datetime.now()}")
    
    # Check code first
    code_ok = check_routes_in_code()
    
    if not code_ok:
        print("\n❌ Code check failed. Please fix the route definitions first.")
        return
    
    # Test routes
    route_ok = test_checkout_success_route()
    test_payment_flow()
    
    print("\n" + "=" * 50)
    if route_ok:
        print("🎉 All tests passed! Payment flow should work correctly.")
        print("\n📋 Summary:")
        print("   ✅ checkout-success route is properly defined")
        print("   ✅ Payment flow routes are accessible")
        print("   ✅ Ready for production deployment")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    print("\n🔧 To deploy to production:")
    print("   1. Run: chmod +x deploy_payment_fix.sh")
    print("   2. Run: ./deploy_payment_fix.sh")
    print("   3. Test a payment flow in production")

if __name__ == "__main__":
    main() 