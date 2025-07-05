#!/usr/bin/env python3
"""
Simple Flask Application Starter for Windows
"""

import os
import sys

def main():
    print("🏥 HealthyRizz - Simple Startup")
    print("=" * 40)
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("📍 Starting Flask Development Server...")
    print("📍 Application will be available at: http://localhost:8000")
    print("📍 Meal plans: http://localhost:8000/meal-plans")
    print("📍 Admin panel: http://localhost:8000/admin/dashboard")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        # Import and start the app
        from app import create_app
        app = create_app()
        
        # Run the app
        app.run(
            host='0.0.0.0',
            port=8000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid issues
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install flask flask-sqlalchemy flask-login flask-wtf")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")

if __name__ == "__main__":
    main() 