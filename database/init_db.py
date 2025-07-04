import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from database.models import User

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@healthyrizz.ca').first()
        if not admin:
            # Create admin user
            admin = User(
                email='admin@healthyrizz.ca',
                username='admin',
                is_admin=True
            )
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_db() 
