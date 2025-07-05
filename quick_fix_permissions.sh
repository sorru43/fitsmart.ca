#!/bin/bash

# Quick Fix for VPS Permission Issues
# Run this script to fix the immediate permission problems

set -e

echo "🔧 Quick Fix for VPS Permission Issues"
echo "======================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ This script must be run as root"
    exit 1
fi

APP_DIR="/home/healthyrizz/htdocs/healthyrizz.in"
APP_USER="healthyrizz"

echo "📁 Fixing directory permissions..."

# Fix the htdocs directory permission issue
chmod 755 "/home/healthyrizz/htdocs"

# Set proper ownership for the application directory
chown -R $APP_USER:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"

echo "✅ Directory permissions fixed"

echo "🐍 Creating virtual environment with correct permissions..."

cd "$APP_DIR"

# Remove existing venv if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment as the app user
echo "🔨 Creating new virtual environment..."
sudo -u $APP_USER python3 -m venv venv

echo "✅ Virtual environment created"

echo "📦 Installing dependencies..."

# Upgrade pip
sudo -u $APP_USER venv/bin/pip install --upgrade pip

# Install dependencies
if [ -f "requirements-production.txt" ]; then
    echo "📋 Installing from requirements-production.txt..."
    sudo -u $APP_USER venv/bin/pip install -r requirements-production.txt
elif [ -f "requirements.txt" ]; then
    echo "📋 Installing from requirements.txt..."
    sudo -u $APP_USER venv/bin/pip install -r requirements.txt
else
    echo "⚠️  No requirements file found. Installing basic dependencies..."
    sudo -u $APP_USER venv/bin/pip install flask gunicorn psycopg2-binary redis flask-sqlalchemy flask-migrate flask-login flask-wtf
fi

echo "✅ Dependencies installed"

echo "🧪 Testing the setup..."

# Test if everything works
if sudo -u $APP_USER venv/bin/python -c "import flask; print('Flask imported successfully')"; then
    echo "✅ Setup test passed!"
else
    echo "❌ Setup test failed"
    exit 1
fi

echo ""
echo "🎉 Quick fix completed successfully!"
echo ""
echo "📋 You can now:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Install additional packages: pip install package_name"
echo "3. Run the application: python app.py"
echo ""
echo "🔧 To test the setup, run:"
echo "sudo -u $APP_USER venv/bin/python -c \"import flask; print('Setup is working!')\""
echo ""
echo "📁 Current directory permissions:"
ls -la "$APP_DIR" 