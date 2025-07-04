#!/usr/bin/env python3
"""
Test deployment script to check if the application starts properly
"""

import os
import sys
import traceback
from datetime import datetime

def test_imports():
    """Test if all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        # Test basic Flask imports
        from flask import Flask
        print("✅ Flask imported successfully")
        
        # Test database imports
        from database.models import User, Order, MealPlan
        print("✅ Database models imported successfully")
        
        # Test routes imports
        from routes.main_routes import main_bp
        print("✅ Main routes imported successfully")
        
        from routes.admin_routes import admin_bp
        print("✅ Admin routes imported successfully")
        
        # Test app creation
        from app import create_app
        print("✅ App factory imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        traceback.print_exc()
        return False

def test_app_creation():
    """Test if the application can be created"""
    print("\n🏗️ Testing app creation...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ App created successfully")
        
        # Test app configuration
        print(f"✅ App name: {app.name}")
        print(f"✅ Debug mode: {app.debug}")
        print(f"✅ Secret key configured: {'SECRET_KEY' in app.config}")
        
        return True, app
        
    except Exception as e:
        print(f"❌ App creation error: {str(e)}")
        traceback.print_exc()
        return False, None

def test_database_connection(app):
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        with app.app_context():
            from extensions import db
            
            # Try to connect to database
            db.engine.connect()
            print("✅ Database connection successful")
            
            # Test basic queries
            from database.models import User, MealPlan
            user_count = User.query.count()
            meal_plan_count = MealPlan.query.count()
            
            print(f"✅ Found {user_count} users")
            print(f"✅ Found {meal_plan_count} meal plans")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        traceback.print_exc()
        return False

def test_routes(app):
    """Test if routes are accessible"""
    print("\n🛣️ Testing routes...")
    
    try:
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            print(f"✅ Home page: {response.status_code}")
            
            # Test login page
            response = client.get('/login')
            print(f"✅ Login page: {response.status_code}")
            
            # Test profile page (should redirect to login)
            response = client.get('/profile')
            print(f"✅ Profile page: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ Route testing error: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 HealthyRizz Deployment Test")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Exiting.")
        return False
    
    # Test app creation
    success, app = test_app_creation()
    if not success:
        print("\n❌ App creation failed. Exiting.")
        return False
    
    # Test database connection
    if not test_database_connection(app):
        print("\n❌ Database tests failed. Exiting.")
        return False
    
    # Test routes
    if not test_routes(app):
        print("\n❌ Route tests failed. Exiting.")
        return False
    
    print("\n✅ All tests passed!")
    print("🎉 Application is ready for deployment!")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 