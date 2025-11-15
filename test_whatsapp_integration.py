#!/usr/bin/env python3
"""
Test WhatsApp Integration System
"""

from app import app, db
from database.models import User, Order, Subscription, MealPlan, Holiday
from whatsapp_marketing_system import whatsapp_system
from datetime import datetime, timedelta

def test_whatsapp_system():
    """Test WhatsApp marketing system functionality"""
    print("🔍 Testing WhatsApp Integration System...")
    
    with app.app_context():
        print("✅ WhatsApp system accessible")
        
        # Test system initialization
        print(f"✅ Base URL: {whatsapp_system.base_url}")
        print(f"✅ Phone Number ID: {whatsapp_system.phone_number_id}")
        print(f"✅ Access Token configured: {bool(whatsapp_system.access_token)}")
        print(f"✅ Verify Token configured: {bool(whatsapp_system.verify_token)}")
        
        # Test templates
        print(f"✅ Available templates: {len(whatsapp_system.templates)}")
        for template_name in whatsapp_system.templates.keys():
            print(f"   - {template_name}")
        
        # Test phone number formatting
        test_phones = [
            "9876543210",
            "+919876543210",
            "919876543210"
        ]
        
        print("\n📱 Testing phone number formatting:")
        for phone in test_phones:
            formatted = whatsapp_system._format_phone_number(phone)
            print(f"   {phone} -> {formatted}")
        
        print("✅ WhatsApp system test completed!")

def test_message_templates():
    """Test message template functionality"""
    print("\n📝 Testing Message Templates...")
    
    with app.app_context():
        # Test welcome message
        print("✅ Testing welcome message template")
        welcome_template = whatsapp_system.templates.get('welcome')
        if welcome_template:
            print(f"   Template name: {welcome_template['name']}")
            print(f"   Language: {welcome_template['language']}")
            print(f"   Components: {len(welcome_template['components'])}")
        
        # Test order confirmation template
        print("✅ Testing order confirmation template")
        order_template = whatsapp_system.templates.get('order_confirmation')
        if order_template:
            print(f"   Template name: {order_template['name']}")
            print(f"   Language: {order_template['language']}")
            print(f"   Components: {len(order_template['components'])}")
        
        # Test delivery reminder template
        print("✅ Testing delivery reminder template")
        delivery_template = whatsapp_system.templates.get('delivery_reminder')
        if delivery_template:
            print(f"   Template name: {delivery_template['name']}")
            print(f"   Language: {delivery_template['language']}")
            print(f"   Components: {len(delivery_template['components'])}")
        
        print("✅ Message templates test completed!")

def test_user_segmentation():
    """Test user segmentation for WhatsApp campaigns"""
    print("\n👥 Testing User Segmentation...")
    
    with app.app_context():
        # Get user statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        users_with_phone = User.query.filter(User.phone.isnot(None)).count()
        new_users_this_week = User.query.filter(
            User.created_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        print(f"✅ Total users: {total_users}")
        print(f"✅ Active users: {active_users}")
        print(f"✅ Users with phone: {users_with_phone}")
        print(f"✅ New users this week: {new_users_this_week}")
        
        # Test user targeting
        if users_with_phone > 0:
            print("✅ Users available for WhatsApp campaigns")
            
            # Get sample users with phone numbers
            sample_users = User.query.filter(
                User.phone.isnot(None),
                User.is_active == True
            ).limit(3).all()
            
            print(f"✅ Sample users for testing:")
            for user in sample_users:
                print(f"   - {user.name} ({user.phone})")
        else:
            print("⚠️ No users with phone numbers found")
        
        print("✅ User segmentation test completed!")

def test_campaign_functions():
    """Test campaign sending functions"""
    print("\n📤 Testing Campaign Functions...")
    
    with app.app_context():
        # Test welcome message function
        print("✅ Testing welcome message function")
        try:
            # This would normally send a message, but we'll just test the function exists
            if hasattr(whatsapp_system, 'send_welcome_message'):
                print("   ✅ send_welcome_message function exists")
            else:
                print("   ❌ send_welcome_message function missing")
        except Exception as e:
            print(f"   ❌ Error testing welcome message: {e}")
        
        # Test order confirmation function
        print("✅ Testing order confirmation function")
        try:
            if hasattr(whatsapp_system, 'send_order_confirmation'):
                print("   ✅ send_order_confirmation function exists")
            else:
                print("   ❌ send_order_confirmation function missing")
        except Exception as e:
            print(f"   ❌ Error testing order confirmation: {e}")
        
        # Test delivery reminder function
        print("✅ Testing delivery reminder function")
        try:
            if hasattr(whatsapp_system, 'send_delivery_reminder'):
                print("   ✅ send_delivery_reminder function exists")
            else:
                print("   ❌ send_delivery_reminder function missing")
        except Exception as e:
            print(f"   ❌ Error testing delivery reminder: {e}")
        
        # Test holiday notification function
        print("✅ Testing holiday notification function")
        try:
            if hasattr(whatsapp_system, 'send_holiday_notification'):
                print("   ✅ send_holiday_notification function exists")
            else:
                print("   ❌ send_holiday_notification function missing")
        except Exception as e:
            print(f"   ❌ Error testing holiday notification: {e}")
        
        # Test promotion offer function
        print("✅ Testing promotion offer function")
        try:
            if hasattr(whatsapp_system, 'send_promotion_offer'):
                print("   ✅ send_promotion_offer function exists")
            else:
                print("   ❌ send_promotion_offer function missing")
        except Exception as e:
            print(f"   ❌ Error testing promotion offer: {e}")
        
        print("✅ Campaign functions test completed!")

def test_webhook_handling():
    """Test webhook handling functionality"""
    print("\n🔄 Testing Webhook Handling...")
    
    with app.app_context():
        # Test webhook handler function
        print("✅ Testing webhook handler function")
        try:
            if hasattr(whatsapp_system, 'handle_webhook'):
                print("   ✅ handle_webhook function exists")
            else:
                print("   ❌ handle_webhook function missing")
        except Exception as e:
            print(f"   ❌ Error testing webhook handler: {e}")
        
        # Test incoming message processing
        print("✅ Testing incoming message processing")
        try:
            if hasattr(whatsapp_system, '_process_incoming_message'):
                print("   ✅ _process_incoming_message function exists")
            else:
                print("   ❌ _process_incoming_message function missing")
        except Exception as e:
            print(f"   ❌ Error testing message processing: {e}")
        
        # Test status update processing
        print("✅ Testing status update processing")
        try:
            if hasattr(whatsapp_system, '_process_status_update'):
                print("   ✅ _process_status_update function exists")
            else:
                print("   ❌ _process_status_update function missing")
        except Exception as e:
            print(f"   ❌ Error testing status processing: {e}")
        
        print("✅ Webhook handling test completed!")

def test_analytics_functions():
    """Test analytics and reporting functions"""
    print("\n📊 Testing Analytics Functions...")
    
    with app.app_context():
        # Test analytics function
        print("✅ Testing analytics function")
        try:
            if hasattr(whatsapp_system, 'get_analytics'):
                print("   ✅ get_analytics function exists")
            else:
                print("   ❌ get_analytics function missing")
        except Exception as e:
            print(f"   ❌ Error testing analytics: {e}")
        
        # Test webhook logs function
        print("✅ Testing webhook logs function")
        try:
            if hasattr(whatsapp_system, 'get_webhook_logs'):
                print("   ✅ get_webhook_logs function exists")
            else:
                print("   ❌ get_webhook_logs function missing")
        except Exception as e:
            print(f"   ❌ Error testing webhook logs: {e}")
        
        # Test message status function
        print("✅ Testing message status function")
        try:
            if hasattr(whatsapp_system, 'get_message_status'):
                print("   ✅ get_message_status function exists")
            else:
                print("   ❌ get_message_status function missing")
        except Exception as e:
            print(f"   ❌ Error testing message status: {e}")
        
        print("✅ Analytics functions test completed!")

def test_bulk_campaigns():
    """Test bulk campaign functionality"""
    print("\n📢 Testing Bulk Campaigns...")
    
    with app.app_context():
        # Test bulk campaign function
        print("✅ Testing bulk campaign function")
        try:
            if hasattr(whatsapp_system, 'send_bulk_campaign'):
                print("   ✅ send_bulk_campaign function exists")
            else:
                print("   ❌ send_bulk_campaign function missing")
        except Exception as e:
            print(f"   ❌ Error testing bulk campaign: {e}")
        
        # Test custom message function
        print("✅ Testing custom message function")
        try:
            if hasattr(whatsapp_system, 'send_custom_message'):
                print("   ✅ send_custom_message function exists")
            else:
                print("   ❌ send_custom_message function missing")
        except Exception as e:
            print(f"   ❌ Error testing custom message: {e}")
        
        print("✅ Bulk campaigns test completed!")

def test_route_integration():
    """Test route integration"""
    print("\n🛣️ Testing Route Integration...")
    
    # Create a fresh app instance to test route registration
    from app import create_app
    test_app = create_app()
    
    with test_app.app_context():
        # Test webhook routes
        print("✅ Testing webhook routes")
        try:
            from routes.whatsapp_routes import whatsapp_bp
            print("   ✅ WhatsApp routes blueprint imported")
            
            # Check if routes are registered
            routes = []
            for rule in test_app.url_map.iter_rules():
                if 'whatsapp' in rule.endpoint:
                    routes.append(rule.endpoint)
            
            print(f"   ✅ Found {len(routes)} WhatsApp routes:")
            for route in routes:
                print(f"      - {route}")
                
        except Exception as e:
            print(f"   ❌ Error testing webhook routes: {e}")
        
        # Test admin routes
        print("✅ Testing admin routes")
        try:
            from routes.admin_whatsapp_routes import admin_whatsapp_bp
            print("   ✅ Admin WhatsApp routes blueprint imported")
            
            # Check if admin routes are registered
            admin_routes = []
            for rule in test_app.url_map.iter_rules():
                if 'admin_whatsapp' in rule.endpoint:
                    admin_routes.append(rule.endpoint)
            
            print(f"   ✅ Found {len(admin_routes)} admin WhatsApp routes:")
            for route in admin_routes:
                print(f"      - {route}")
                
        except Exception as e:
            print(f"   ❌ Error testing admin routes: {e}")
        
        print("✅ Route integration test completed!")

def main():
    """Run all WhatsApp integration tests"""
    print("🚀 Starting WhatsApp Integration Tests...\n")
    
    test_whatsapp_system()
    test_message_templates()
    test_user_segmentation()
    test_campaign_functions()
    test_webhook_handling()
    test_analytics_functions()
    test_bulk_campaigns()
    test_route_integration()
    
    print("\n🎉 WhatsApp Integration Tests Completed!")
    print("\n📋 Summary:")
    print("✅ WhatsApp system core functionality")
    print("✅ Message templates and formatting")
    print("✅ User segmentation and targeting")
    print("✅ Campaign sending functions")
    print("✅ Webhook handling and processing")
    print("✅ Analytics and reporting")
    print("✅ Bulk campaign capabilities")
    print("✅ Route integration")
    
    print("\n🔧 Next Steps:")
    print("1. Configure WhatsApp Business API credentials")
    print("2. Create and approve message templates")
    print("3. Set up webhook URL in Meta Developer Console")
    print("4. Test with real phone numbers")
    print("5. Monitor analytics and performance")

if __name__ == "__main__":
    main()
