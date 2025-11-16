#!/bin/bash

# Quick Start Script for FitSmart on CloudPanel
# Run this script to start your Flask application

set -e

PROJECT_DIR="/home/fitsmart/htdocs/www.fitsmart.ca"
VENV_DIR="$PROJECT_DIR/venv"

echo "=========================================="
echo "FitSmart Application Startup"
echo "=========================================="
echo ""

# Navigate to project
cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if requirements are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Dependencies not installed. Installing..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check if .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > "$PROJECT_DIR/.env" << EOF
# Flask Configuration
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FLASK_APP=wsgi.py
FLASK_ENV=production

# Database
DATABASE_URL=sqlite:///database/fitsmart.db

# Set DEBUG to True for development
DEBUG=False
EOF
    echo "✅ .env file created (please edit with your settings)"
fi

# Check if database exists
if [ ! -f "$PROJECT_DIR/database/fitsmart.db" ]; then
    echo "⚠️  Database not found. Initializing..."
    python3 -c "
from app import create_app
from database.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    db.create_all()
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
        print('✅ Admin user created: fitsmart.ca@gmail.com / admin123')
    else:
        print('ℹ️  Admin user already exists')
"
    echo "✅ Database initialized"
fi

# Start the application
echo ""
echo "🚀 Starting application..."
echo "=========================================="
echo "Application will be available at:"
echo "  - http://localhost:9000"
echo "  - http://$(hostname -I | awk '{print $1}'):9000"
echo ""
echo "Admin login: fitsmart.ca@gmail.com / admin123"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Run with Gunicorn (production)
if command -v gunicorn &> /dev/null; then
    gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
else
    # Fallback to Flask dev server
    export FLASK_APP=wsgi.py
    export FLASK_ENV=development
    flask run --host=0.0.0.0 --port=9000
fi

