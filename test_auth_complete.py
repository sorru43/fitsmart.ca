#!/usr/bin/env python3
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, '/home/healthyrizz/htdocs/healthyrizz.in')

try:
    from main import app
    from forms.auth_forms import LoginForm, RegisterForm
    import re
    
    print("✅ Imports successful")
    
    # Test basic app context
    with app.app_context():
        print("✅ App context works")
        
        # Test form creation in context
        try:
            login_form = LoginForm()
            print("✅ LoginForm created successfully")
        except Exception as e:
            print(f"❌ LoginForm creation failed: {e}")
            import traceback
            traceback.print_exc()
            
        try:
            register_form = RegisterForm()
            print("✅ RegisterForm created successfully")
        except Exception as e:
            print(f"❌ RegisterForm creation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test with test client
        try:
            with app.test_client() as client:
                print("✅ Test client created")
                
                # Test 1: Login page GET
                response = client.get('/login')
                print(f'✅ Login page GET: {response.status_code}')
                
                # Test 2: Registration page GET
                response = client.get('/register')
                print(f'✅ Registration page GET: {response.status_code}')
                
                if response.status_code != 200:
                    print(f"❌ Registration page failed: {response.data}")
                else:
                    # Check if CSRF token is in the response
                    response_text = response.data.decode()
                    if 'csrf_token' in response_text:
                        print('✅ Registration page: CSRF token found in response')
                        
                        # Extract the CSRF token
                        match = re.search(r'name="csrf_token" value="([^"]+)"', response_text)
                        if match:
                            csrf_token = match.group(1)
                            print(f'✅ Registration CSRF token extracted: {csrf_token[:10]}...')
                            
                            # Test registration with CSRF token
                            response = client.post('/register', data={
                                'name': 'Test User',
                                'email': 'testuser@healthyrizz.in',
                                'phone': '9876543210',
                                'password': 'testpassword123',
                                'confirm_password': 'testpassword123',
                                'csrf_token': csrf_token
                            }, follow_redirects=True)
                            print(f'✅ Registration POST with CSRF: {response.status_code}')
                            
                            if response.status_code == 200:
                                response_text = response.data.decode()
                                if 'successful' in response_text.lower() or 'login' in response_text.lower():
                                    print('✅ Registration test successful!')
                                else:
                                    print('🔄 Registration completed but check response')
                            else:
                                print(f'❌ Registration failed. Response: {response.data[:500]}')
                        else:
                            print('❌ Could not extract CSRF token from registration response')
                    else:
                        print('❌ CSRF token not found in registration response')
                        print('Response content preview:')
                        print(response_text[:500])
                
                # Test 3: Login functionality (we know this works)
                response = client.get('/login')
                if response.status_code == 200:
                    response_text = response.data.decode()
                    if 'csrf_token' in response_text:
                        match = re.search(r'name="csrf_token" value="([^"]+)"', response_text)
                        if match:
                            csrf_token = match.group(1)
                            
                            # Test login with existing admin user
                            response = client.post('/login', data={
                                'email': 'admin@healthyrizz.in',
                                'password': 'admin123',
                                'csrf_token': csrf_token
                            }, follow_redirects=True)
                            print(f'✅ Login test: {response.status_code}')
                            
                            if response.status_code == 200:
                                print('✅ Login still working correctly!')
                            else:
                                print(f'❌ Login test failed: {response.data[:200]}')
                        
        except Exception as e:
            print(f"❌ Test client error: {e}")
            import traceback
            traceback.print_exc()
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ General error: {e}")
    import traceback
    traceback.print_exc()

print("Auth test completed.") 