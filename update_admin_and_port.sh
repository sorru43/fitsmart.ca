#!/bin/bash

# Update Admin Email and Change Port to 9000
# Run this script to update existing admin user and restart on port 9000

set -e

PROJECT_DIR="/home/fitsmart/htdocs/www.fitsmart.ca"

echo "=========================================="
echo "Updating Admin Email and Port"
echo "=========================================="
echo ""

cd "$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

# Update admin user in database
echo "🔄 Updating admin user..."
python3 << 'PYTHON_SCRIPT'
from app import create_app
from database.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Check if old admin exists
    old_admin = User.query.filter_by(email='admin@fitsmart.ca').first()
    new_admin = User.query.filter_by(email='fitsmart.ca@gmail.com').first()
    
    if old_admin:
        # Update existing admin email
        old_admin.email = 'fitsmart.ca@gmail.com'
        db.session.commit()
        print("✅ Updated admin email from admin@fitsmart.ca to fitsmart.ca@gmail.com")
    elif new_admin:
        print("ℹ️  Admin with email fitsmart.ca@gmail.com already exists")
    else:
        # Create new admin
        admin = User(
            email='fitsmart.ca@gmail.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Created new admin user: fitsmart.ca@gmail.com / admin123")
PYTHON_SCRIPT

echo ""
echo "✅ Admin email updated to: fitsmart.ca@gmail.com"
echo ""
echo "To restart on port 9000, stop current server (Ctrl+C) and run:"
echo "  venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app"
echo ""

