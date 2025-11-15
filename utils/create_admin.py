"""
Script to create an admin user for the HealthyRizz application.
"""
from app import create_app, db
from database.models import User

def create_admin_user():
    """Create an admin user in the database"""
    app = create_app()
    
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@healthyrizz.in').first()
        if admin:
            print("Admin user already exists.")
            return
        
        # Create admin user
        admin = User(
            username='Admin',
            email='admin@healthyrizz.in',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')
        
        try:
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        except Exception as e:
            print(f"Error creating admin user: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_admin_user()
