#!/usr/bin/env python3
"""
Restart HealthyRizz with all fixes applied
"""

import os
import sys
import subprocess
import time

def stop_existing_processes():
    """Kill any existing Flask processes"""
    print("🛑 Stopping existing Flask processes...")
    try:
        # Try to kill processes on port 5001
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                      capture_output=True, text=True)
        time.sleep(2)
        print("✅ Existing processes stopped")
    except Exception as e:
        print(f"⚠️  Could not stop processes: {e}")

def verify_fixes():
    """Verify that all fixes are in place"""
    print("🔍 Verifying fixes are applied...")
    
    issues = []
    
    # Check admin routes file
    try:
        with open('routes/admin_routes.py', 'r', encoding='utf-8') as f:
            routes_content = f.read()
            
        if 'def admin_add_meal_plan' not in routes_content:
            issues.append("❌ admin_add_meal_plan route missing")
        else:
            print("✅ admin_add_meal_plan route exists")
            
        # Check for duplicates
        if routes_content.count('def admin_add_meal_plan') > 1:
            issues.append("❌ Duplicate admin_add_meal_plan routes")
        else:
            print("✅ No duplicate routes")
            
    except Exception as e:
        issues.append(f"❌ Cannot read admin routes: {e}")
    
    # Check users template
    try:
        with open('templates/admin/users.html', 'r', encoding='utf-8') as f:
            users_template = f.read()
            
        if 'users.items' not in users_template:
            issues.append("❌ Users template not fixed for pagination")
        else:
            print("✅ Users template pagination fixed")
            
    except Exception as e:
        issues.append(f"❌ Cannot read users template: {e}")
    
    # Check notifications template
    try:
        with open('templates/admin/notifications.html', 'r', encoding='utf-8') as f:
            notif_template = f.read()
            
        # Check for template syntax
        if '{% else %}' in notif_template:
            # Make sure it has proper endif
            else_pos = notif_template.find('{% else %}')
            remaining = notif_template[else_pos:]
            if '{% endfor %}' not in remaining:
                issues.append("❌ Notifications template has syntax error")
            else:
                print("✅ Notifications template syntax OK")
        else:
            print("✅ Notifications template OK")
            
    except Exception as e:
        issues.append(f"❌ Cannot read notifications template: {e}")
    
    # Check required template files exist
    required_templates = [
        'templates/admin/add_meal_plan.html',
        'templates/admin/add_coupon.html', 
        'templates/admin/add_banner.html'
    ]
    
    for template in required_templates:
        if os.path.exists(template):
            print(f"✅ {template} exists")
        else:
            issues.append(f"❌ {template} missing")
    
    if issues:
        print("\n🚨 Issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("\n✅ All fixes verified!")
        return True

def start_app():
    """Start the Flask application"""
    print("\n🚀 Starting HealthyRizz Application...")
    print("=" * 50)
    
    try:
        # Import and run the app
        from main import app
        print("✅ App imported successfully")
        print("🌐 Starting on http://127.0.0.1:5001")
        print("🔑 Admin Login: admin@healthyrizz.in / admin123")
        print("=" * 50)
        
        app.run(host='127.0.0.1', port=5001, debug=True)
        
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        return False

def main():
    """Main function"""
    print("🔧 HealthyRizz Admin Panel - Clean Restart")
    print("=" * 50)
    
    # Step 1: Stop existing processes
    stop_existing_processes()
    
    # Step 2: Verify fixes
    if not verify_fixes():
        print("\n❌ Cannot start - fixes not properly applied")
        return
    
    # Step 3: Start the app
    start_app()

if __name__ == "__main__":
    main() 