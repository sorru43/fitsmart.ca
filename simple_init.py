#!/usr/bin/env python3
from app import create_app
from extensions import db
from database.models import User

def simple_init():
    app = create_app()
    
    with app.app_context():
        print("🔧 Starting simple database initialization...")
        
        # Create all tables
        db.create_all()
        print("✅ All tables created successfully")
        
        # Create admin user
        admin = User(
            username='admin',
            name='Admin',
            email='admin@healthyrizz.in',
            phone='9999999999',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created successfully!")
        print("   Email: admin@healthyrizz.in")
        print("   Password: admin123")
        
        # Verify tables
        tables = db.engine.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        print(f"📋 Available tables: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")

if __name__ == '__main__':
    simple_init()
