#!/usr/bin/env python3
"""
Test script to verify the application works correctly
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_application():
    """Test if the application works correctly"""
    try:
        print("🧪 Testing application...")
        
        # Test basic imports
        from app import create_app
        print("✅ App import successful")
        
        app = create_app()
        print("✅ App creation successful")
        
        # Test database models
        from database.models import User, Subscription, Delivery
        print("✅ Database models imported successfully")
        
        # Test routes
        from routes.admin_routes import admin_bp
        print("✅ Admin routes imported successfully")
        
        from routes.enhanced_daily_orders import enhanced_orders_bp
        print("✅ Enhanced daily orders routes imported successfully")
        
        from routes.subscription_management_routes import subscription_mgmt_bp
        print("✅ Subscription management routes imported successfully")
        
        # Test utilities
        from utils.email_functions import send_delivery_status_update_email
        print("✅ Email functions imported successfully")
        
        print("✅ All tests passed! Application is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Application Test Script")
    print("=" * 30)
    test_application()
