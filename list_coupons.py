#!/usr/bin/env python3
"""
Script to list all coupons in the database
"""
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database.models import CouponCode
from extensions import db

def list_coupons():
    app = create_app()
    
    with app.app_context():
        try:
            coupons = CouponCode.query.all()
            
            print(f"📋 Found {len(coupons)} coupons in database:")
            print("=" * 60)
            
            for i, coupon in enumerate(coupons, 1):
                print(f"\n{i}. Coupon Code: {coupon.code}")
                print(f"   Discount Type: {coupon.discount_type}")
                print(f"   Discount Value: {coupon.discount_value}")
                print(f"   Min Order Value: ₹{coupon.min_order_value}")
                print(f"   Valid From: {coupon.valid_from.strftime('%Y-%m-%d %H:%M')}")
                print(f"   Valid To: {coupon.valid_to.strftime('%Y-%m-%d %H:%M')}")
                print(f"   Active: {'✅ Yes' if coupon.is_active else '❌ No'}")
                print(f"   Single Use: {'✅ Yes' if coupon.is_single_use else '❌ No'}")
                print(f"   Uses: {coupon.current_uses}/{coupon.max_uses if coupon.max_uses else 'Unlimited'}")
                print(f"   Is Valid: {'✅ Yes' if coupon.is_valid() else '❌ No'}")
                print("-" * 40)
            
            print(f"\n🎯 To view coupons in admin panel:")
            print("1. Go to: http://localhost:5000/login")
            print("2. Login with: admin@healthyrizz.in / admin123")
            print("3. Go to: http://localhost:5000/admin/coupons")
            
        except Exception as e:
            print(f"❌ Error listing coupons: {e}")

if __name__ == "__main__":
    list_coupons() 