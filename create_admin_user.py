#!/usr/bin/env python3
"""
Create admin user for blog functionality
"""

from app import create_app, db
from database.models import User

def create_admin_user():
    """Create admin user if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        print("=== Creating Admin User ===")
        
        # Check if admin user already exists
        admin = User.query.filter_by(email='admin@healthyrizz.com').first()
        if admin:
            print(f"✅ Admin user already exists: {admin.name}")
            return admin
        
        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@healthyrizz.com',
            phone='1234567890',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Admin user created successfully!")
        print(f"   - Name: {admin.name}")
        print(f"   - Email: {admin.email}")
        print(f"   - Password: admin123")
        print(f"   - Admin: {admin.is_admin}")
        
        return admin

if __name__ == "__main__":
    create_admin_user() 