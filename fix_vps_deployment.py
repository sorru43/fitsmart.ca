#!/usr/bin/env python3
"""
Fix VPS Deployment Issues
This script addresses the import and template errors on the VPS
"""

import os
import sys
import subprocess

def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def fix_vps_deployment():
    """Fix VPS deployment issues"""
    print("🔧 Fixing VPS Deployment Issues")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not check_file_exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project root.")
        return False
    
    # Check if config.py exists
    if not check_file_exists('config.py'):
        print("❌ Error: config.py not found!")
        return False
    
    print("✅ Found app.py and config.py")
    
    # Test the import
    print("\n🔍 Testing imports...")
    try:
        import config
        from config import Config
        print("✅ Config import successful")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    # Test app creation
    print("\n🔍 Testing app creation...")
    try:
        from app import create_app
        app = create_app()
        print("✅ App creation successful")
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False
    
    # Check if wsgi.py is correct
    print("\n🔍 Checking wsgi.py...")
    if check_file_exists('wsgi.py'):
        with open('wsgi.py', 'r') as f:
            wsgi_content = f.read()
        
        if 'from app import create_app' in wsgi_content:
            print("✅ wsgi.py looks correct")
        else:
            print("❌ wsgi.py needs fixing")
            # Fix wsgi.py
            wsgi_fixed = '''from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
'''
            with open('wsgi.py', 'w') as f:
                f.write(wsgi_fixed)
            print("✅ Fixed wsgi.py")
    else:
        print("❌ wsgi.py not found!")
        return False
    
    # Test the application
    print("\n🔍 Testing application...")
    try:
        from app import create_app
        app = create_app()
        with app.app_context():
            # Test basic functionality
            print("✅ Application context works")
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return False
    
    print("\n✅ VPS deployment should now work!")
    print("\n📋 Next steps:")
    print("1. Upload this fixed code to your VPS")
    print("2. Restart the service: sudo systemctl restart healthyrizz")
    print("3. Check status: sudo systemctl status healthyrizz")
    
    return True

if __name__ == "__main__":
    success = fix_vps_deployment()
    sys.exit(0 if success else 1) 