#!/usr/bin/env python3
"""
Test script to check the subscribe route and identify issues
"""

import requests
import sys
from datetime import datetime

def test_subscribe_route():
    """Test the subscribe route to identify issues"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Subscribe Route")
    print("=" * 50)
    
    try:
        # Test 1: Check if application is running
        print("1. Testing application connectivity...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Application is running")
        else:
            print(f"   ❌ Application returned status code: {response.status_code}")
            return False
        
        # Test 2: Test meal plans page
        print("2. Testing meal plans page...")
        response = requests.get(f"{base_url}/meal-plans", timeout=5)
        if response.status_code == 200:
            print("   ✅ Meal plans page loads successfully")
        else:
            print(f"   ❌ Meal plans page returned status code: {response.status_code}")
            return False
        
        # Test 3: Test subscribe route with plan ID 1
        print("3. Testing subscribe route with plan ID 1...")
        response = requests.get(f"{base_url}/subscribe/1", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Subscribe route works successfully")
            print("   📄 Response length:", len(response.text))
            
            # Check if response contains expected content
            if "checkout" in response.text.lower():
                print("   ✅ Response contains checkout content")
            else:
                print("   ⚠️ Response doesn't contain expected checkout content")
                
        elif response.status_code == 404:
            print("   ❌ Plan ID 1 not found - this is expected if no meal plans exist")
            
            # Try to find available plan IDs
            print("4. Searching for available meal plans...")
            response = requests.get(f"{base_url}/meal-plans", timeout=5)
            if response.status_code == 200:
                # Look for plan IDs in the response
                import re
                plan_ids = re.findall(r'/subscribe/(\d+)', response.text)
                if plan_ids:
                    print(f"   📋 Found plan IDs: {plan_ids}")
                    # Test with the first available plan
                    test_plan_id = plan_ids[0]
                    print(f"5. Testing subscribe route with plan ID {test_plan_id}...")
                    response = requests.get(f"{base_url}/subscribe/{test_plan_id}", timeout=10)
                    print(f"   Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("   ✅ Subscribe route works with available plan")
                    else:
                        print(f"   ❌ Subscribe route failed with status: {response.status_code}")
                else:
                    print("   ❌ No plan IDs found in meal plans page")
            else:
                print("   ❌ Could not access meal plans page")
                
        elif response.status_code == 500:
            print("   ❌ Internal Server Error - this is the issue we need to fix")
            print("   📋 Checking server logs for more details...")
            
            # Try to get more details about the error
            try:
                # Check if there's an error page or API endpoint
                response = requests.get(f"{base_url}/error", timeout=5)
                if response.status_code == 200:
                    print("   📄 Error page content preview:", response.text[:200])
            except:
                pass
                
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            
        # Test 4: Check if there are any meal plans in the database
        print("6. Checking meal plans availability...")
        response = requests.get(f"{base_url}/meal-plans", timeout=5)
        if response.status_code == 200:
            if "meal plan" in response.text.lower() or "plan" in response.text.lower():
                print("   ✅ Meal plans content found")
            else:
                print("   ⚠️ No meal plans content found")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to the application")
        print("   💡 Make sure the Flask app is running on http://localhost:5000")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False

def check_server_logs():
    """Provide guidance on checking server logs"""
    print("\n🔍 Debugging Steps:")
    print("=" * 50)
    print("1. Check Flask application logs:")
    print("   - Look for Python traceback errors")
    print("   - Check for import errors or missing modules")
    print("   - Look for database connection issues")
    
    print("\n2. Common issues to check:")
    print("   - Missing imports (FlaskForm, StringField, etc.)")
    print("   - Database connection problems")
    print("   - Template rendering errors")
    print("   - Missing static files or templates")
    
    print("\n3. Quick fixes to try:")
    print("   - Restart the Flask application")
    print("   - Check if all required packages are installed")
    print("   - Verify database is accessible")
    print("   - Check template files exist")

if __name__ == "__main__":
    print(f"🚀 Starting Subscribe Route Test - {datetime.now()}")
    print()
    
    success = test_subscribe_route()
    
    if not success:
        check_server_logs()
    
    print(f"\n✅ Test completed at {datetime.now()}") 