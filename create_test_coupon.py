#!/usr/bin/env python3
"""
Script to create a test coupon in the database
"""
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database.models import CouponCode
from extensions import db

def create_test_coupon():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if test coupon already exists
            existing_coupon = CouponCode.query.filter_by(code='TEST10').first()
            if existing_coupon:
                print("Test coupon 'TEST10' already exists!")
                return
            
            # Create test coupon
            test_coupon = CouponCode(
                code='TEST10',
                discount_type='percent',
                discount_value=10.0,  # 10% discount
                min_order_value=0.0,  # No minimum order value
                valid_from=datetime.now(),
                valid_to=datetime.now() + timedelta(days=30),  # Valid for 30 days
                is_single_use=False,
                max_uses=100,
                current_uses=0,
                is_active=True
            )
            
            db.session.add(test_coupon)
            db.session.commit()
            
            print("✅ Test coupon 'TEST10' created successfully!")
            print(f"   - 10% discount")
            print(f"   - Valid until: {test_coupon.valid_to.strftime('%Y-%m-%d')}")
            print(f"   - Max uses: {test_coupon.max_uses}")
            
        except Exception as e:
            print(f"❌ Error creating test coupon: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_test_coupon() 