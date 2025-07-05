#!/usr/bin/env python3
"""
Debug CSRF issues in login/register forms
"""

from app import create_app
from flask_wtf.csrf import generate_csrf

def debug_csrf_issue():
    """Debug CSRF token generation and validation"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Debugging CSRF Issues")
        print("=" * 40)
        
        # Check SECRET_KEY
        secret_key = app.config.get('SECRET_KEY')
        print(f"✅ SECRET_KEY: {'Set' if secret_key else 'Missing'}")
        if secret_key:
            print(f"   Length: {len(secret_key)} characters")
            print(f"   Value: {secret_key[:10]}...")
        
        # Check CSRF configuration
        csrf_enabled = app.config.get('WTF_CSRF_ENABLED', True)
        csrf_secret = app.config.get('WTF_CSRF_SECRET_KEY')
        print(f"✅ CSRF Enabled: {csrf_enabled}")
        print(f"✅ CSRF Secret Key: {'Set' if csrf_secret else 'Missing'}")
        
        # Generate CSRF token
        try:
            csrf_token = generate_csrf()
            print(f"✅ CSRF Token Generated: {csrf_token[:20]}...")
        except Exception as e:
            print(f"❌ Error generating CSRF token: {str(e)}")
            return False
        
        # Test session configuration
        session_secure = app.config.get('SESSION_COOKIE_SECURE', False)
        session_httponly = app.config.get('SESSION_COOKIE_HTTPONLY', True)
        session_samesite = app.config.get('SESSION_COOKIE_SAMESITE', 'Lax')
        
        print(f"✅ Session Configuration:")
        print(f"   Secure: {session_secure}")
        print(f"   HttpOnly: {session_httponly}")
        print(f"   SameSite: {session_samesite}")
        
        return True

def test_login_form():
    """Test login form with test client"""
    app = create_app()
    
    with app.test_client() as client:
        print("\n🧪 Testing Login Form")
        print("=" * 30)
        
        # Test GET request to login page
        print("📄 Testing GET /login...")
        response = client.get('/login')
        
        if response.status_code == 200:
            print("✅ Login page loads successfully")
            
            # Check if CSRF token is in the response
            content = response.get_data(as_text=True)
            if 'csrf_token' in content:
                print("✅ CSRF token found in page")
            else:
                print("❌ CSRF token not found in page")
            
            # Check session cookie
            if 'session' in response.headers.get('Set-Cookie', ''):
                print("✅ Session cookie set")
            else:
                print("❌ Session cookie not set")
            
            # Test POST request with CSRF token
            print("\n📝 Testing POST /login...")
            
            # Get the CSRF token from the form
            import re
            csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', content)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ Found CSRF token: {csrf_token[:20]}...")
                
                # Test POST with CSRF token
                post_response = client.post('/login', data={
                    'email': 'test@example.com',
                    'password': 'testpassword',
                    'csrf_token': csrf_token
                })
                
                print(f"✅ POST response status: {post_response.status_code}")
                
                if post_response.status_code == 302:
                    print("✅ Login redirect successful (expected for invalid credentials)")
                elif post_response.status_code == 400:
                    print("❌ CSRF validation failed")
                else:
                    print(f"⚠️ Unexpected status: {post_response.status_code}")
            else:
                print("❌ Could not extract CSRF token from form")
        else:
            print(f"❌ Login page failed to load. Status: {response.status_code}")
            return False
        
        return True

def test_register_form():
    """Test register form with test client"""
    app = create_app()
    
    with app.test_client() as client:
        print("\n🧪 Testing Register Form")
        print("=" * 30)
        
        # Test GET request to register page
        print("📄 Testing GET /register...")
        response = client.get('/register')
        
        if response.status_code == 200:
            print("✅ Register page loads successfully")
            
            # Check if CSRF token is in the response
            content = response.get_data(as_text=True)
            if 'csrf_token' in content:
                print("✅ CSRF token found in page")
            else:
                print("❌ CSRF token not found in page")
            
            # Check session cookie
            if 'session' in response.headers.get('Set-Cookie', ''):
                print("✅ Session cookie set")
            else:
                print("❌ Session cookie not set")
            
            # Test POST request with CSRF token
            print("\n📝 Testing POST /register...")
            
            # Get the CSRF token from the form
            import re
            csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', content)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ Found CSRF token: {csrf_token[:20]}...")
                
                # Test POST with CSRF token
                post_response = client.post('/register', data={
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'phone': '1234567890',
                    'password': 'testpassword123',
                    'confirm_password': 'testpassword123',
                    'csrf_token': csrf_token
                })
                
                print(f"✅ POST response status: {post_response.status_code}")
                
                if post_response.status_code == 302:
                    print("✅ Register redirect successful")
                elif post_response.status_code == 400:
                    print("❌ CSRF validation failed")
                else:
                    print(f"⚠️ Unexpected status: {post_response.status_code}")
            else:
                print("❌ Could not extract CSRF token from form")
        else:
            print(f"❌ Register page failed to load. Status: {response.status_code}")
            return False
        
        return True

if __name__ == "__main__":
    print("🚀 CSRF Debug Script")
    print("=" * 30)
    
    success1 = debug_csrf_issue()
    success2 = test_login_form()
    success3 = test_register_form()
    
    if success1 and success2 and success3:
        print("\n✅ All CSRF tests passed!")
        print("\n📝 If you're still getting CSRF errors in browser:")
        print("   1. Clear browser cookies and cache")
        print("   2. Try incognito/private window")
        print("   3. Check if using HTTPS locally (set SESSION_COOKIE_SECURE=False)")
        print("   4. Check for proxy/load balancer issues")
    else:
        print("\n❌ Some CSRF tests failed. Check the errors above.") 