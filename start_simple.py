#!/usr/bin/env python3
"""
Simple startup script for HealthyRizz to test fixes
"""

import sys
import os
sys.path.append('.')

def start_app():
    """Start the HealthyRizz application"""
    print("🚀 Starting HealthyRizz Application...")
    print("=" * 50)
    
    try:
        from main import app
        
        print("✅ App imported successfully")
        print("✅ Starting on http://127.0.0.1:5001")
        print("=" * 50)
        print("📋 Admin Panel Test Instructions:")
        print("   1. Open http://127.0.0.1:5001 in your browser")
        print("   2. Click 'Login' and use: admin@healthyrizz.in / admin123")
        print("   3. After login, click 'Admin Dashboard' from profile menu")
        print("   4. Test all admin tabs to verify they work")
        print("=" * 50)
        
        # Start the application
        app.run(host='127.0.0.1', port=5001, debug=True)
        
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    start_app() 