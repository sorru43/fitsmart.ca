#!/usr/bin/env python3
"""
Simple test to verify profile route works
"""

import requests
import json

def test_profile_access():
    """Test profile route access"""
    print("🧪 Testing profile route access...")
    
    try:
        # Test the route locally
        response = requests.get('http://localhost:8000/profile', allow_redirects=False)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("✅ Route exists and redirects (expected for non-authenticated users)")
            print(f"   Redirect location: {response.headers.get('Location', 'None')}")
            return True
        elif response.status_code == 200:
            print("✅ Route exists and returns 200")
            return True
        elif response.status_code == 404:
            print("❌ Route returns 404")
            return False
        else:
            print(f"⚠️ Route returns unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is the Flask app running?")
        return False
    except Exception as e:
        print(f"❌ Error testing route: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Profile Route Test")
    print("=" * 50)
    
    success = test_profile_access()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Profile route test completed successfully")
    else:
        print("❌ Profile route test failed") 