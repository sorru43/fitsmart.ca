#!/usr/bin/env python3
"""
Script to reset admin password
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database.models import User
from extensions import db
from werkzeug.security import generate_password_hash

def reset_admin_password():
    app = create_app()
    
    with app.app_context():
        try:
            # Find admin user
            admin = User.query.filter_by(email='admin@healthyrizz.in').first()
            
            if not admin:
                print("❌ Admin user not found!")
                return
            
            # Set new password
            new_password = "admin123"
            admin.password_hash = generate_password_hash(new_password)
            
            db.session.commit()
            
            print("✅ Admin password reset successfully!")
            print(f"Email: {admin.email}")
            print(f"New Password: {new_password}")
            print("\nYou can now login to the admin panel at: http://localhost:5000/login")
            print("Then go to: http://localhost:5000/admin/coupons to see your coupons")
            
        except Exception as e:
            print(f"❌ Error resetting admin password: {e}")
            db.session.rollback()

if __name__ == "__main__":
    reset_admin_password() 