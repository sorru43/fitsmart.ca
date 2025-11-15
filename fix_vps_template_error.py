#!/usr/bin/env python3
"""
Fix VPS Template Error
This script fixes the 'str' object is not callable error in templates
"""

import os
import sys

def fix_template_error():
    """Fix the template error on VPS"""
    print("🔧 Fixing VPS Template Error")
    print("=" * 40)
    
    # Fix the CSRF token injection in app.py
    print("\n🔍 Checking CSRF configuration...")
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Check if the CSRF injection is correct
    if 'inject_csrf_token' in app_content:
        print("✅ CSRF injection function exists")
    else:
        print("❌ CSRF injection function missing")
        return False
    
    # Fix the template to handle CSRF token properly
    print("\n🔍 Fixing template CSRF token usage...")
    
    # Read base.html with proper encoding
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding if utf-8 fails
        with open('templates/base.html', 'r', encoding='latin-1') as f:
            base_content = f.read()
    
    # Replace the problematic CSRF token usage
    if '{{ csrf_token() }}' in base_content:
        print("✅ Found CSRF token usage in template")
        # The issue might be that csrf_token is not a callable
        # Let's make sure it's handled properly
        base_content = base_content.replace('{{ csrf_token() }}', '{{ csrf_token() if csrf_token else "" }}')
        
        with open('templates/base.html', 'w', encoding='utf-8') as f:
            f.write(base_content)
        print("✅ Fixed CSRF token usage in template")
    else:
        print("⚠️  No CSRF token usage found in template")
    
    # Also check if there are any other template files with similar issues
    template_files = [
        'templates/index.html',
        'templates/admin/base_admin.html',
        'templates/forgot_password.html',
        'templates/reset_password.html'
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(template_file, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            if '{{ csrf_token() }}' in content:
                print(f"✅ Found CSRF token usage in {template_file}")
                content = content.replace('{{ csrf_token() }}', '{{ csrf_token() if csrf_token else "" }}')
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed CSRF token usage in {template_file}")
    
    # Create a simple test to verify the fix
    print("\n🔍 Creating test script...")
    test_script = '''#!/usr/bin/env python3
"""
Test VPS Template Fix
"""
from app import create_app

def test_template_rendering():
    """Test if templates render without errors"""
    try:
        app = create_app()
        with app.app_context():
            # Test basic template rendering
            from flask import render_template_string
            
            # Test simple template
            template = "{{ csrf_token() if csrf_token else 'no-csrf' }}"
            result = render_template_string(template)
            print(f"✅ Template test passed: {result}")
            return True
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_template_rendering()
    exit(0 if success else 1)
'''
    
    with open('test_template_fix.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Created test script: test_template_fix.py")
    
    # Test the fix
    print("\n🔍 Testing the fix...")
    try:
        result = os.system('python test_template_fix.py')
        if result == 0:
            print("✅ Template fix test passed!")
        else:
            print("❌ Template fix test failed!")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    print("\n✅ VPS template error should now be fixed!")
    print("\n📋 Next steps:")
    print("1. Upload these fixed files to your VPS")
    print("2. Restart the service: sudo systemctl restart healthyrizz")
    print("3. Check the website: https://healthyrizz.in")
    
    return True

if __name__ == "__main__":
    success = fix_template_error()
    sys.exit(0 if success else 1) 