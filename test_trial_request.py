#!/usr/bin/env python3
"""
Test script to debug trial request form submission
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    from database.models import TrialRequest, MealPlan
    from contact_forms import TrialRequestForm
    
    def test_trial_request_creation():
        """Test creating a trial request manually"""
        with app.app_context():
            # Get the first available meal plan
            meal_plan = MealPlan.query.first()
            if not meal_plan:
                print("❌ No meal plans found in database")
                return
            
            print(f"✅ Found meal plan: {meal_plan.name}")
            
            # Create a test trial request
            test_request = TrialRequest(
                name='Test User',
                email='test@example.com',
                phone='9876543210',
                address='123 Test Street',
                city='Ludhiana',
                province='PB',  # Punjab
                postal_code='141001',
                meal_plan_id=meal_plan.id,
                notes='Test trial request',
                preferred_date=datetime.now().date() + timedelta(days=1),
                user_id=None  # No user (guest request)
            )
            
            try:
                db.session.add(test_request)
                db.session.commit()
                print("✅ Test trial request created successfully!")
                print(f"   ID: {test_request.id}")
                print(f"   Name: {test_request.name}")
                print(f"   Email: {test_request.email}")
                print(f"   State: {test_request.province}")
                print(f"   PIN Code: {test_request.postal_code}")
                print(f"   Meal Plan: {test_request.meal_plan.name}")
                
                # Clean up - delete the test request
                db.session.delete(test_request)
                db.session.commit()
                print("✅ Test request cleaned up")
                
            except Exception as e:
                print(f"❌ Error creating test trial request: {e}")
                db.session.rollback()
                return False
            
            return True
    
    def test_form_validation():
        """Test form validation"""
        with app.app_context():
            form = TrialRequestForm()
            
            # Test with valid data
            form.name.data = 'Test User'
            form.email.data = 'test@example.com'
            form.phone.data = '9876543210'
            form.address.data = '123 Test Street'
            form.city.data = 'Ludhiana'
            form.province.data = 'PB'
            form.postal_code.data = '141001'
            form.notes.data = 'Test notes'
            form.preferred_date.data = datetime.now().date() + timedelta(days=1)
            form.meal_plan_id.data = 1
            
            if form.validate():
                print("✅ Form validation passed")
                return True
            else:
                print("❌ Form validation failed:")
                for field, errors in form.errors.items():
                    print(f"   {field}: {errors}")
                return False
    
    if __name__ == "__main__":
        print("🧪 Trial Request Debug Script")
        print("=" * 40)
        
        # Test form validation
        print("\n1. Testing form validation...")
        form_valid = test_form_validation()
        
        # Test database creation
        print("\n2. Testing database creation...")
        db_valid = test_trial_request_creation()
        
        if form_valid and db_valid:
            print("\n✅ All tests passed! The trial request system should work correctly.")
        else:
            print("\n❌ Some tests failed. Check the errors above.")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
except Exception as e:
    print(f"❌ Error: {e}") 