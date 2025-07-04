#!/usr/bin/env python3
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, '/home/healthyrizz/htdocs/healthyrizz.in')

try:
    from main import app
    from models import User, Subscription
    import re
    
    print("✅ Imports successful")
    
    # Test basic app context
    with app.app_context():
        print("✅ App context works")
        
        # Test admin user exists
        admin = User.query.filter_by(email='admin@healthyrizz.in').first()
        if admin:
            print(f'✅ Admin user found: {admin.email}, is_admin: {admin.is_admin}')
        else:
            print('❌ Admin user not found')
        
        # Test with test client
        try:
            with app.test_client() as client:
                print("✅ Test client created")
                
                # Test 1: Login first
                response = client.get('/login')
                if response.status_code == 200:
                    response_text = response.data.decode()
                    if 'csrf_token' in response_text:
                        match = re.search(r'name="csrf_token" value="([^"]+)"', response_text)
                        if match:
                            csrf_token = match.group(1)
                            
                            # Login as admin
                            response = client.post('/login', data={
                                'email': 'admin@healthyrizz.in',
                                'password': 'admin123',
                                'csrf_token': csrf_token
                            }, follow_redirects=True)
                            print(f'✅ Login test: {response.status_code}')
                            
                            if response.status_code == 200:
                                print('✅ Login successful!')
                                
                                # Test 2: Profile page (user dashboard)
                                response = client.get('/profile')
                                print(f'✅ Profile page status: {response.status_code}')
                                if response.status_code == 200:
                                    print('✅ Profile page loads successfully!')
                                else:
                                    print(f'❌ Profile page failed: {response.data[:200]}')
                                
                                # Test 3: Admin dashboard
                                response = client.get('/admin/dashboard')
                                print(f'✅ Admin dashboard status: {response.status_code}')
                                if response.status_code == 200:
                                    print('✅ Admin dashboard loads successfully!')
                                else:
                                    print(f'❌ Admin dashboard failed: {response.data[:200]}')
                            else:
                                print(f'❌ Login failed: {response.data[:200]}')
                        else:
                            print('❌ Could not extract CSRF token')
                    else:
                        print('❌ CSRF token not found in login response')
                else:
                    print(f'❌ Login page failed: {response.status_code}')
                        
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

print("Dashboard test completed.") 