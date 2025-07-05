#!/usr/bin/env python3
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, '/home/healthyrizz/htdocs/healthyrizz.in')

try:
    from main import app
    from forms.auth_forms import LoginForm
    import re
    
    print("✅ Imports successful")
    
    # Test basic app context
    with app.app_context():
        print("✅ App context works")
        
        # Test form creation in context
        try:
            form = LoginForm()
            print("✅ LoginForm created successfully")
        except Exception as e:
            print(f"❌ LoginForm creation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test with test client
        try:
            with app.test_client() as client:
                print("✅ Test client created")
                
                # Get the login page
                response = client.get('/login')
                print(f'✅ Login page GET: {response.status_code}')
                
                if response.status_code != 200:
                    print(f"❌ Login page failed: {response.data}")
                else:
                    # Check if CSRF token is in the response
                    response_text = response.data.decode()
                    if 'csrf_token' in response_text:
                        print('✅ CSRF token found in response')
                        
                        # Extract the CSRF token
                        match = re.search(r'name="csrf_token" value="([^"]+)"', response_text)
                        if match:
                            csrf_token = match.group(1)
                            print(f'✅ CSRF token extracted: {csrf_token[:10]}...')
                            
                            # Test login with CSRF token
                            response = client.post('/login', data={
                                'email': 'admin@healthyrizz.in',
                                'password': 'admin123',
                                'csrf_token': csrf_token
                            }, follow_redirects=True)
                            print(f'✅ Login POST with CSRF: {response.status_code}')
                            
                            if response.status_code == 200:
                                print('✅ Login test successful!')
                                # Check if we're redirected to dashboard or home
                                final_url = response.request.path if hasattr(response, 'request') else 'unknown'
                                print(f'Final URL: {final_url}')
                            else:
                                print(f'❌ Login failed. Response: {response.data[:500]}')
                        else:
                            print('❌ Could not extract CSRF token from response')
                    else:
                        print('❌ CSRF token not found in response')
                        print('Response content preview:')
                        print(response_text[:500])
                        
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

print("Test completed.") 