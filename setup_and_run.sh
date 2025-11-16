#!/bin/bash

# Setup Database and Run Application
# Run this after virtual environment is set up

set -e

PROJECT_DIR="/home/fitsmart/htdocs/www.fitsmart.ca"

echo "=========================================="
echo "Setting Up Database and Running Application"
echo "=========================================="
echo ""

cd "$PROJECT_DIR"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists, create if not
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=$SECRET_KEY
FLASK_APP=wsgi.py
FLASK_ENV=production

# Database
DATABASE_URL=sqlite:///database/fitsmart.db

# Set DEBUG to True for development
DEBUG=False
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Create database directory if it doesn't exist
mkdir -p database

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python3 << 'PYTHON_SCRIPT'
from app import create_app
from database.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Database tables created")
    
    # Create admin user if doesn't exist
    admin = User.query.filter_by(email='fitsmart.ca@gmail.com').first()
    if not admin:
        admin = User(
            email='fitsmart.ca@gmail.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created:")
        print("   Email: fitsmart.ca@gmail.com")
        print("   Password: admin123")
    else:
        print("ℹ️  Admin user already exists")
PYTHON_SCRIPT

echo ""
echo "=========================================="
echo "🚀 Starting Application"
echo "=========================================="
echo ""
echo "Application will be available at:"
echo "  - http://localhost:9000"
echo "  - http://$(hostname -I | awk '{print $1}'):9000"
echo ""
echo "Admin Panel: http://$(hostname -I | awk '{print $1}'):9000/admin"
echo "Admin Login: fitsmart.ca@gmail.com / admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Check if gunicorn is installed
if venv/bin/pip show gunicorn &> /dev/null; then
    echo "🚀 Starting with Gunicorn (Production)..."
    venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
else
    echo "🚀 Starting with Flask dev server..."
    export FLASK_APP=wsgi.py
    export FLASK_ENV=development
    venv/bin/flask run --host=0.0.0.0 --port=9000
fi

