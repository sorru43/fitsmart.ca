<<<<<<< HEAD
#!/usr/bin/env python3
"""
Fix CSRF Token Issues in Production
This script diagnoses and fixes CSRF token problems
"""

import os
import sys
import secrets
from datetime import datetime

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking Environment Configuration")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ main.py not found. Please run this script from the app directory.")
        return False
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
        
        # Read and check .env content
        with open('.env', 'r') as f:
            env_content = f.read()
            
        # Check for required CSRF settings
        required_settings = [
            'SECRET_KEY',
            'WTF_CSRF_SECRET_KEY',
            'WTF_CSRF_ENABLED',
            'WTF_CSRF_SSL_STRICT'
        ]
        
        for setting in required_settings:
            if setting in env_content:
                print(f"✅ {setting} is configured")
            else:
                print(f"❌ {setting} is missing")
                
        # Check specific values
        if 'WTF_CSRF_SSL_STRICT=True' in env_content:
            print("⚠️ WTF_CSRF_SSL_STRICT is True - this can cause issues")
        if 'SESSION_COOKIE_SECURE=True' in env_content:
            print("⚠️ SESSION_COOKIE_SECURE is True - this can cause issues")
            
    else:
        print("❌ .env file not found")
        return False
    
    return True

def fix_environment():
    """Fix environment configuration"""
    print("\n🔧 Fixing Environment Configuration")
    print("=" * 50)
    
    # Backup existing .env
    if os.path.exists('.env'):
        backup_name = f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.rename('.env', backup_name)
        print(f"✅ Backed up .env to {backup_name}")
    
    # Generate new secure keys
    secret_key = secrets.token_hex(32)
    csrf_key = secrets.token_hex(32)
    
    # Create new .env file
    env_content = f"""# HealthyRizz Production Environment - Fixed CSRF
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Security Keys
SECRET_KEY={secret_key}
WTF_CSRF_SECRET_KEY={csrf_key}

# Environment
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=sqlite:///healthyrizz.db

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=healthyrizz.in@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=healthyrizz.in@gmail.com

# Payment Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=your-webhook-secret

# CSRF Configuration - FIXED
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=7200
WTF_CSRF_SSL_STRICT=False
WTF_CSRF_HEADERS=['X-CSRFToken', 'X-CSRF-Token', 'X-XSRF-TOKEN']

# Security Settings - FIXED
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=1800

# Domain
DOMAIN_NAME=healthyrizz.in
BASE_URL=https://healthyrizz.in

# Additional CSRF Settings
WTF_CSRF_METHODS=['POST', 'PUT', 'PATCH', 'DELETE']
WTF_CSRF_FIELD_NAME=csrf_token
WTF_CSRF_CHECK_DEFAULT=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created new .env file with fixed CSRF settings")
    print(f"✅ Generated new SECRET_KEY: {secret_key[:10]}...")
    print(f"✅ Generated new WTF_CSRF_SECRET_KEY: {csrf_key[:10]}...")

def check_templates():
    """Check template CSRF configuration"""
    print("\n🔍 Checking Template Configuration")
    print("=" * 50)
    
    templates_to_check = [
        'templates/base.html',
        'templates/checkout.html',
        'templates/meal_plan_checkout.html'
    ]
    
    for template in templates_to_check:
        if os.path.exists(template):
            print(f"✅ {template} exists")
            
            with open(template, 'r') as f:
                content = f.read()
                
            # Check for CSRF token meta tag
            if 'name="csrf-token"' in content:
                print(f"✅ {template} has CSRF token meta tag")
            else:
                print(f"❌ {template} missing CSRF token meta tag")
                
            # Check for CSRF token in forms
            if 'name="csrf_token"' in content:
                print(f"✅ {template} has CSRF token in forms")
            else:
                print(f"❌ {template} missing CSRF token in forms")
        else:
            print(f"❌ {template} not found")

def fix_templates():
    """Fix template CSRF configuration"""
    print("\n🔧 Fixing Template Configuration")
    print("=" * 50)
    
    # Fix base.html
    if os.path.exists('templates/base.html'):
        with open('templates/base.html', 'r') as f:
            content = f.read()
        
        # Add CSRF token meta tag if missing
        if 'name="csrf-token"' not in content:
            # Find head tag and add meta tag after it
            if '<head>' in content:
                content = content.replace('<head>', '''<head>
    <meta name="csrf-token" content="{{ csrf_token() }}">''')
                with open('templates/base.html', 'w') as f:
                    f.write(content)
                print("✅ Added CSRF token meta tag to base.html")
            else:
                print("❌ Could not find <head> tag in base.html")
        else:
            print("✅ base.html already has CSRF token meta tag")
    
    # Fix checkout.html
    if os.path.exists('templates/checkout.html'):
        with open('templates/checkout.html', 'r') as f:
            content = f.read()
        
        # Add CSRF token to checkout form if missing
        if 'name="csrf_token"' not in content:
            # Find checkout form and add CSRF token
            if '<form id="checkout-form"' in content:
                content = content.replace('<form id="checkout-form"', '''<form id="checkout-form"
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">''')
                with open('templates/checkout.html', 'w') as f:
                    f.write(content)
                print("✅ Added CSRF token to checkout form")
            else:
                print("❌ Could not find checkout form in checkout.html")
        else:
            print("✅ checkout.html already has CSRF token")

def create_test_script():
    """Create a test script to verify CSRF functionality"""
    print("\n🔧 Creating CSRF Test Script")
    print("=" * 50)
    
    test_script = '''#!/usr/bin/env python3
"""
Test CSRF functionality
"""
import requests
import re

def test_csrf():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing CSRF Functionality")
    print("=" * 40)
    
    # Test 1: Get CSRF token from page
    try:
        response = requests.get(f"{base_url}/meal-plans")
        if response.status_code == 200:
            print("✅ Meal plans page accessible")
            
            # Extract CSRF token
            csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRF token found: {csrf_token[:20]}...")
                
                # Test 2: Submit form with CSRF token
                test_data = {
                    'csrf_token': csrf_token,
                    'plan_id': '1',
                    'customer_name': 'Test User',
                    'customer_email': 'test@example.com'
                }
                
                response = requests.post(f"{base_url}/process_checkout", data=test_data)
                print(f"✅ Form submission test completed: {response.status_code}")
                
            else:
                print("❌ CSRF token not found in page")
                
        else:
            print(f"❌ Meal plans page returned: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing CSRF: {e}")

if __name__ == "__main__":
    test_csrf()
'''
    
    with open('test_csrf_functionality.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created test_csrf_functionality.py")
    print("💡 Run: python test_csrf_functionality.py to test CSRF")

def main():
    """Main function"""
    print("🔧 HealthyRizz CSRF Token Fix")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        return
    
    # Fix environment
    fix_environment()
    
    # Check templates
    check_templates()
    
    # Fix templates
    fix_templates()
    
    # Create test script
    create_test_script()
    
    print("\n🎉 CSRF Fix Complete!")
    print("=" * 60)
    print("Next steps:")
    print("1. Restart your Gunicorn application")
    print("2. Test CSRF functionality: python test_csrf_functionality.py")
    print("3. Test payment flow: https://healthyrizz.in/meal-plans")
    print("4. If issues persist, check application logs")

if __name__ == "__main__":
=======
#!/usr/bin/env python3
"""
Fix CSRF Token Issues in Production
This script diagnoses and fixes CSRF token problems
"""

import os
import sys
import secrets
from datetime import datetime

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking Environment Configuration")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ main.py not found. Please run this script from the app directory.")
        return False
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
        
        # Read and check .env content
        with open('.env', 'r') as f:
            env_content = f.read()
            
        # Check for required CSRF settings
        required_settings = [
            'SECRET_KEY',
            'WTF_CSRF_SECRET_KEY',
            'WTF_CSRF_ENABLED',
            'WTF_CSRF_SSL_STRICT'
        ]
        
        for setting in required_settings:
            if setting in env_content:
                print(f"✅ {setting} is configured")
            else:
                print(f"❌ {setting} is missing")
                
        # Check specific values
        if 'WTF_CSRF_SSL_STRICT=True' in env_content:
            print("⚠️ WTF_CSRF_SSL_STRICT is True - this can cause issues")
        if 'SESSION_COOKIE_SECURE=True' in env_content:
            print("⚠️ SESSION_COOKIE_SECURE is True - this can cause issues")
            
    else:
        print("❌ .env file not found")
        return False
    
    return True

def fix_environment():
    """Fix environment configuration"""
    print("\n🔧 Fixing Environment Configuration")
    print("=" * 50)
    
    # Backup existing .env
    if os.path.exists('.env'):
        backup_name = f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        os.rename('.env', backup_name)
        print(f"✅ Backed up .env to {backup_name}")
    
    # Generate new secure keys
    secret_key = secrets.token_hex(32)
    csrf_key = secrets.token_hex(32)
    
    # Create new .env file
    env_content = f"""# HealthyRizz Production Environment - Fixed CSRF
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Security Keys
SECRET_KEY={secret_key}
WTF_CSRF_SECRET_KEY={csrf_key}

# Environment
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=sqlite:///healthyrizz.db

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=healthyrizz.in@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=healthyrizz.in@gmail.com

# Payment Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=your-webhook-secret

# CSRF Configuration - FIXED
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=7200
WTF_CSRF_SSL_STRICT=False
WTF_CSRF_HEADERS=['X-CSRFToken', 'X-CSRF-Token', 'X-XSRF-TOKEN']

# Security Settings - FIXED
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=1800

# Domain
DOMAIN_NAME=healthyrizz.in
BASE_URL=https://healthyrizz.in

# Additional CSRF Settings
WTF_CSRF_METHODS=['POST', 'PUT', 'PATCH', 'DELETE']
WTF_CSRF_FIELD_NAME=csrf_token
WTF_CSRF_CHECK_DEFAULT=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created new .env file with fixed CSRF settings")
    print(f"✅ Generated new SECRET_KEY: {secret_key[:10]}...")
    print(f"✅ Generated new WTF_CSRF_SECRET_KEY: {csrf_key[:10]}...")

def check_templates():
    """Check template CSRF configuration"""
    print("\n🔍 Checking Template Configuration")
    print("=" * 50)
    
    templates_to_check = [
        'templates/base.html',
        'templates/checkout.html',
        'templates/meal_plan_checkout.html'
    ]
    
    for template in templates_to_check:
        if os.path.exists(template):
            print(f"✅ {template} exists")
            
            with open(template, 'r') as f:
                content = f.read()
                
            # Check for CSRF token meta tag
            if 'name="csrf-token"' in content:
                print(f"✅ {template} has CSRF token meta tag")
            else:
                print(f"❌ {template} missing CSRF token meta tag")
                
            # Check for CSRF token in forms
            if 'name="csrf_token"' in content:
                print(f"✅ {template} has CSRF token in forms")
            else:
                print(f"❌ {template} missing CSRF token in forms")
        else:
            print(f"❌ {template} not found")

def fix_templates():
    """Fix template CSRF configuration"""
    print("\n🔧 Fixing Template Configuration")
    print("=" * 50)
    
    # Fix base.html
    if os.path.exists('templates/base.html'):
        with open('templates/base.html', 'r') as f:
            content = f.read()
        
        # Add CSRF token meta tag if missing
        if 'name="csrf-token"' not in content:
            # Find head tag and add meta tag after it
            if '<head>' in content:
                content = content.replace('<head>', '''<head>
    <meta name="csrf-token" content="{{ csrf_token() }}">''')
                with open('templates/base.html', 'w') as f:
                    f.write(content)
                print("✅ Added CSRF token meta tag to base.html")
            else:
                print("❌ Could not find <head> tag in base.html")
        else:
            print("✅ base.html already has CSRF token meta tag")
    
    # Fix checkout.html
    if os.path.exists('templates/checkout.html'):
        with open('templates/checkout.html', 'r') as f:
            content = f.read()
        
        # Add CSRF token to checkout form if missing
        if 'name="csrf_token"' not in content:
            # Find checkout form and add CSRF token
            if '<form id="checkout-form"' in content:
                content = content.replace('<form id="checkout-form"', '''<form id="checkout-form"
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">''')
                with open('templates/checkout.html', 'w') as f:
                    f.write(content)
                print("✅ Added CSRF token to checkout form")
            else:
                print("❌ Could not find checkout form in checkout.html")
        else:
            print("✅ checkout.html already has CSRF token")

def create_test_script():
    """Create a test script to verify CSRF functionality"""
    print("\n🔧 Creating CSRF Test Script")
    print("=" * 50)
    
    test_script = '''#!/usr/bin/env python3
"""
Test CSRF functionality
"""
import requests
import re

def test_csrf():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing CSRF Functionality")
    print("=" * 40)
    
    # Test 1: Get CSRF token from page
    try:
        response = requests.get(f"{base_url}/meal-plans")
        if response.status_code == 200:
            print("✅ Meal plans page accessible")
            
            # Extract CSRF token
            csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRF token found: {csrf_token[:20]}...")
                
                # Test 2: Submit form with CSRF token
                test_data = {
                    'csrf_token': csrf_token,
                    'plan_id': '1',
                    'customer_name': 'Test User',
                    'customer_email': 'test@example.com'
                }
                
                response = requests.post(f"{base_url}/process_checkout", data=test_data)
                print(f"✅ Form submission test completed: {response.status_code}")
                
            else:
                print("❌ CSRF token not found in page")
                
        else:
            print(f"❌ Meal plans page returned: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing CSRF: {e}")

if __name__ == "__main__":
    test_csrf()
'''
    
    with open('test_csrf_functionality.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created test_csrf_functionality.py")
    print("💡 Run: python test_csrf_functionality.py to test CSRF")

def main():
    """Main function"""
    print("🔧 HealthyRizz CSRF Token Fix")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        return
    
    # Fix environment
    fix_environment()
    
    # Check templates
    check_templates()
    
    # Fix templates
    fix_templates()
    
    # Create test script
    create_test_script()
    
    print("\n🎉 CSRF Fix Complete!")
    print("=" * 60)
    print("Next steps:")
    print("1. Restart your Gunicorn application")
    print("2. Test CSRF functionality: python test_csrf_functionality.py")
    print("3. Test payment flow: https://healthyrizz.in/meal-plans")
    print("4. If issues persist, check application logs")

if __name__ == "__main__":
>>>>>>> 81a4199426f7354dc222b670139539c5516ca07d
    main() 