#!/usr/bin/env python3
"""
Simple startup script for HealthyRizz website
Uses port 5002 to avoid Windows permission issues
"""

import sys
import os

def start_website():
    """Start the HealthyRizz website"""
    try:
        print("🚀 Starting HealthyRizz Website...")
        print("=" * 50)
        
        # Import the Flask app
        from main import app
        
        print("✅ App imported successfully")
        print("🌐 Starting server on http://127.0.0.1:5002")
        print("📱 Admin Panel: http://127.0.0.1:5002/admin/dashboard")
        print("👤 Admin Login: admin@healthyrizz.in / admin123")
        print("=" * 50)
        
        # Run the app on port 5002 with debug mode
        app.run(
            host='127.0.0.1', 
            port=5002, 
            debug=True, 
            use_reloader=False  # Disable reloader to avoid issues
        )
        
    except Exception as e:
        print(f"❌ Error starting website: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    start_website() 