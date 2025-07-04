from app import create_app, db
from database.models import User

app = create_app()

with app.app_context():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@healthyrizz.ca',
        is_admin=True
    )
    admin.set_password('admin123')
    
    # Add admin to database
    db.session.add(admin)
    db.session.commit()
    
    print("Database reset complete!")
    print("Admin user created with:")
    print("Email: admin@healthyrizz.ca")
    print("Password: admin123") 
