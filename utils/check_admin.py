from app import create_app, db
from database.models import User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='admin@healthyrizz.ca').first()
    print(f"Admin exists: {admin is not None}")
    if admin:
        print(f"Admin username: {admin.username}")
        print(f"Admin is_admin: {admin.is_admin}")
        print(f"Admin is_active: {admin.is_active}") 
