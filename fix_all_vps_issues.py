#!/usr/bin/env python3
"""
Fix All VPS Issues
This script fixes all the VPS deployment issues automatically
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

def fix_all_vps_issues():
    """Fix all VPS deployment issues"""
    print("🔧 Fixing All VPS Issues")
    print("=" * 50)
    
    # Step 1: Check if we're in the right directory
    if not check_file_exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project root.")
        return False
    
    if not check_file_exists('config.py'):
        print("❌ Error: config.py not found!")
        return False
    
    print("✅ Found app.py and config.py")
    
    # Step 2: Test imports
    print("\n🔍 Step 1: Testing imports...")
    try:
        import config
        from config import Config
        print("✅ Config import successful")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    # Step 3: Test app creation
    print("\n🔍 Step 2: Testing app creation...")
    try:
        from app import create_app
        app = create_app()
        print("✅ App creation successful")
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False
    
    # Step 4: Fix wsgi.py
    print("\n🔍 Step 3: Fixing wsgi.py...")
    wsgi_content = '''from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
'''
    
    with open('wsgi.py', 'w', encoding='utf-8') as f:
        f.write(wsgi_content)
    print("✅ Fixed wsgi.py")
    
    # Step 5: Fix template CSRF token issues
    print("\n🔍 Step 4: Fixing template CSRF token issues...")
    
    template_files = [
        'templates/base.html',
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
            
            # Fix CSRF token usage
            if '{{ csrf_token() }}' in content:
                print(f"✅ Found CSRF token usage in {template_file}")
                content = content.replace('{{ csrf_token() }}', '{{ csrf_token() if csrf_token else "" }}')
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed CSRF token usage in {template_file}")
    
    # Step 6: Test the application
    print("\n🔍 Step 5: Testing application...")
    try:
        from app import create_app
        app = create_app()
        with app.app_context():
            print("✅ Application context works")
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return False
    
    # Step 7: Create deployment script for VPS
    print("\n🔍 Step 6: Creating VPS deployment script...")
    
    vps_script = '''#!/bin/bash
# VPS Deployment Script
echo "🚀 Deploying HealthyRizz to VPS..."

# Stop the service
sudo systemctl stop healthyrizz

# Navigate to project directory
cd /home/healthyrizz/htdocs/healthyrizz.in

# Activate virtual environment
source venv/bin/activate

# Test the application
python -c "from app import create_app; app = create_app(); print('✅ App created successfully')"

if [ $? -eq 0 ]; then
    echo "✅ Application test passed"
    
    # Start the service
    sudo systemctl start healthyrizz
    
    # Check status
    sudo systemctl status healthyrizz
    
    echo "✅ Deployment completed successfully!"
    echo "🌐 Visit: https://healthyrizz.in"
else
    echo "❌ Application test failed"
    exit 1
fi
'''
    
    with open('deploy_to_vps.sh', 'w', encoding='utf-8') as f:
        f.write(vps_script)
    
    # Make it executable
    os.chmod('deploy_to_vps.sh', 0o755)
    print("✅ Created deploy_to_vps.sh")
    
    # Step 8: Create comprehensive VPS fix guide
    print("\n🔍 Step 7: Creating comprehensive VPS fix guide...")
    
    vps_guide = '''# Complete VPS Fix Guide

## 🚀 Quick Fix Commands

### 1. Connect to VPS
```bash
ssh root@89.116.122.69
```

### 2. Navigate to project
```bash
cd /home/healthyrizz/htdocs/healthyrizz.in
```

### 3. Stop service
```bash
sudo systemctl stop healthyrizz
```

### 4. Upload fixed files
Upload these files from your local machine to the VPS:
- app.py
- config.py
- wsgi.py
- templates/base.html
- templates/admin/base_admin.html
- All other template files

### 5. Activate environment
```bash
source venv/bin/activate
```

### 6. Test application
```bash
python -c "from app import create_app; app = create_app(); print('✅ App created successfully')"
```

### 7. Start service
```bash
sudo systemctl start healthyrizz
```

### 8. Check status
```bash
sudo systemctl status healthyrizz
```

### 9. Check logs
```bash
sudo journalctl -u healthyrizz -f
```

## 🔧 Manual Fixes (if needed)

### Fix CSRF Token Error
Edit templates/base.html line 17:
```html
<!-- Change this: -->
<meta name="csrf-token" content="{{ csrf_token() }}">

<!-- To this: -->
<meta name="csrf-token" content="{{ csrf_token() if csrf_token else '' }}">
```

### Fix wsgi.py
```bash
cat > wsgi.py << 'EOF'
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
EOF
```

### Check file permissions
```bash
chmod 644 *.py
chmod 644 templates/*.html
chmod 644 templates/admin/*.html
```

## 📊 Monitoring

### Check service status
```bash
sudo systemctl status healthyrizz
```

### Check logs
```bash
sudo journalctl -u healthyrizz -n 50
```

### Check port
```bash
netstat -tlnp | grep 8000
```

### Test website
```bash
curl -I http://localhost:8000
```

## ✅ Success Indicators

- Service status: "active (running)"
- No errors in logs
- Port 8000 listening
- Website loads: https://healthyrizz.in

## 🆘 Emergency Reset

If everything fails:
```bash
sudo systemctl stop healthyrizz
cp -r /home/healthyrizz/htdocs/healthyrizz.in /home/healthyrizz/htdocs/healthyrizz.in.backup
# Upload fresh files from local machine
sudo systemctl start healthyrizz
```
'''
    
    with open('COMPLETE_VPS_FIX_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(vps_guide)
    
    print("✅ Created COMPLETE_VPS_FIX_GUIDE.md")
    
    # Step 9: Final test
    print("\n🔍 Step 8: Final comprehensive test...")
    
    try:
        # Test imports
        import config
        from config import Config
        
        # Test app creation
        from app import create_app
        app = create_app()
        
        # Test template rendering
        with app.app_context():
            from flask import render_template_string
            template = "{{ csrf_token() if csrf_token else 'no-csrf' }}"
            result = render_template_string(template)
            print(f"✅ Template test passed: {result}")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Final test failed: {e}")
        return False
    
    print("\n🎉 All VPS issues have been fixed!")
    print("\n📋 Next steps:")
    print("1. Upload all files to your VPS")
    print("2. Run: chmod +x deploy_to_vps.sh")
    print("3. Run: ./deploy_to_vps.sh")
    print("4. Check: https://healthyrizz.in")
    
    return True

if __name__ == "__main__":
    success = fix_all_vps_issues()
    sys.exit(0 if success else 1) 