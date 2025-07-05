#!/usr/bin/env python3
"""
Start HealthyRizz Application on Windows
This script starts the Flask application using the built-in development server
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def kill_existing_processes():
    """Kill any existing Python processes running the app"""
    print("🔧 Checking for existing processes...")
    
    try:
        # Use tasklist to find Python processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'python.exe' in result.stdout:
            print("⚠️ Found existing Python processes")
            
            # Kill processes that might be running our app
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                         capture_output=True, shell=True)
            print("✅ Killed existing Python processes")
        else:
            print("✅ No existing Python processes found")
            
    except Exception as e:
        print(f"⚠️ Could not check for existing processes: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔧 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask_sqlalchemy', 
        'flask_login',
        'flask_wtf',
        'werkzeug',
        'sqlalchemy',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True)
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def check_database():
    """Check if database exists and is accessible"""
    print("🔧 Checking database...")
    
    try:
        # Try to import and check database
        from app import create_app, db
        from database.models import User, MealPlan, DeliveryLocation
        
        app = create_app()
        with app.app_context():
            # Check if tables exist
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful")
            
            # Check if we have meal plans
            meal_plans = MealPlan.query.count()
            print(f"✅ Found {meal_plans} meal plans")
            
            # Check if we have delivery locations
            locations = DeliveryLocation.query.count()
            print(f"✅ Found {locations} delivery locations")
            
            return True
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def start_application():
    """Start the Flask application"""
    print("🚀 Starting HealthyRizz Application...")
    print("=" * 60)
    
    # Kill existing processes
    kill_existing_processes()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependencies check failed")
        return False
    
    # Check database
    if not check_database():
        print("❌ Database check failed")
        return False
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("\n🎯 Starting Flask Development Server...")
    print("📍 Application will be available at: http://localhost:8000")
    print("📍 Admin panel: http://localhost:8000/admin/dashboard")
    print("📍 Meal plans: http://localhost:8000/meal-plans")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the Flask app
        from app import create_app
        app = create_app()
        
        # Run the app
        app.run(
            host='0.0.0.0',
            port=8000,
            debug=True,
            use_reloader=True
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🏥 HealthyRizz - Windows Startup Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py') and not os.path.exists('app.py'):
        print("❌ main.py or app.py not found")
        print("   Please run this script from the HealthyRizz directory")
        return
    
    # Start the application
    success = start_application()
    
    if success:
        print("\n✅ Application started successfully!")
    else:
        print("\n❌ Failed to start application")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Python is installed and in PATH")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check database configuration")
        print("4. Ensure all required files are present")

if __name__ == "__main__":
    main() 