#!/bin/bash

# Fix VPS Permissions and Setup Script
# This script fixes permission issues and properly sets up the HealthyRizz deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
APP_DIR="/home/healthyrizz/htdocs/healthyrizz.in"
APP_USER="healthyrizz"
WEB_USER="www-data"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root"
fi

log "Starting VPS permission fix and setup..."

# 1. Fix directory permissions
log "Fixing directory permissions..."

# Create directories if they don't exist
mkdir -p "$APP_DIR"
mkdir -p "/home/healthyrizz/logs"
mkdir -p "/home/healthyrizz/backups"

# Set proper ownership
chown -R $APP_USER:$WEB_USER "$APP_DIR"
chown -R $APP_USER:$APP_USER "/home/healthyrizz/logs"
chown -R $APP_USER:$APP_USER "/home/healthyrizz/backups"

# Set proper permissions
chmod -R 755 "$APP_DIR"
chmod -R 755 "/home/healthyrizz/logs"
chmod -R 755 "/home/healthyrizz/backups"

# Make sure the htdocs directory is accessible
chmod 755 "/home/healthyrizz/htdocs"

log "Directory permissions fixed"

# 2. Create virtual environment with proper permissions
log "Setting up Python virtual environment..."

cd "$APP_DIR"

# Remove existing venv if it exists
if [ -d "venv" ]; then
    log "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment as the app user
log "Creating new virtual environment..."
sudo -u $APP_USER python3 -m venv venv

# Verify virtual environment was created
if [ ! -f "venv/bin/activate" ]; then
    error "Failed to create virtual environment"
fi

log "Virtual environment created successfully"

# 3. Install dependencies
log "Installing Python dependencies..."

# Upgrade pip first
sudo -u $APP_USER venv/bin/pip install --upgrade pip

# Install dependencies from requirements-production.txt if it exists
if [ -f "requirements-production.txt" ]; then
    sudo -u $APP_USER venv/bin/pip install -r requirements-production.txt
elif [ -f "requirements.txt" ]; then
    sudo -u $APP_USER venv/bin/pip install -r requirements.txt
else
    warning "No requirements file found. Installing basic dependencies..."
    sudo -u $APP_USER venv/bin/pip install flask gunicorn psycopg2-binary redis
fi

log "Dependencies installed successfully"

# 4. Set up environment file
log "Setting up environment configuration..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << EOL
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://healthyrizz:your_password@localhost/healthyrizz

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Admin Configuration
ADMIN_EMAIL=admin@healthyrizz.in
ADMIN_PASSWORD=admin123

# Security Configuration
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
WTF_CSRF_ENABLED=True

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
RATELIMIT_DEFAULT=200 per day

# Application Settings
PORT=8090
DEBUG=False
EOL

    # Set proper permissions for .env file
    chown $APP_USER:$APP_USER .env
    chmod 600 .env
    
    log "Environment file created"
else
    log "Environment file already exists"
fi

# 5. Create necessary directories for the application
log "Creating application directories..."

# Create static and upload directories
sudo -u $APP_USER mkdir -p static/uploads
sudo -u $APP_USER mkdir -p static/videos
sudo -u $APP_USER mkdir -p static/images
sudo -u $APP_USER mkdir -p static/templates
sudo -u $APP_USER mkdir -p instance
sudo -u $APP_USER mkdir -p flask_session

# Set permissions for upload directories
chmod -R 755 static/uploads
chmod -R 755 static/videos
chmod -R 755 static/images
chmod -R 755 instance
chmod -R 755 flask_session

log "Application directories created"

# 6. Test the setup
log "Testing the setup..."

# Test virtual environment
if sudo -u $APP_USER venv/bin/python -c "import flask; print('Flask imported successfully')"; then
    log "Virtual environment test passed"
else
    error "Virtual environment test failed"
fi

# Test if we can access the application directory
if sudo -u $APP_USER test -r "$APP_DIR"; then
    log "Directory access test passed"
else
    error "Directory access test failed"
fi

# 7. Create a simple test script
log "Creating test script..."

cat > test_setup.py << EOL
#!/usr/bin/env python3
import sys
import os

def test_imports():
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import psycopg2
        print("✓ PostgreSQL driver imported successfully")
    except ImportError as e:
        print(f"✗ PostgreSQL driver import failed: {e}")
        return False
    
    try:
        import redis
        print("✓ Redis imported successfully")
    except ImportError as e:
        print(f"✗ Redis import failed: {e}")
        return False
    
    return True

def test_permissions():
    app_dir = "$APP_DIR"
    if os.access(app_dir, os.R_OK | os.W_OK):
        print("✓ Application directory permissions OK")
        return True
    else:
        print("✗ Application directory permission issues")
        return False

if __name__ == "__main__":
    print("Testing HealthyRizz VPS Setup...")
    print("=" * 40)
    
    success = True
    success &= test_imports()
    success &= test_permissions()
    
    if success:
        print("\\n✓ All tests passed! Setup is ready.")
        sys.exit(0)
    else:
        print("\\n✗ Some tests failed. Please check the setup.")
        sys.exit(1)
EOL

chown $APP_USER:$APP_USER test_setup.py
chmod +x test_setup.py

log "Test script created"

# 8. Final verification
log "Running final verification..."

if sudo -u $APP_USER venv/bin/python test_setup.py; then
    log "✓ All tests passed! Setup is complete."
else
    warning "Some tests failed. Please check the output above."
fi

# 9. Display next steps
echo ""
log "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update the .env file with your actual database password and other settings"
echo "2. Run database migrations: sudo -u $APP_USER venv/bin/python init_db.py"
echo "3. Start the application: sudo -u $APP_USER venv/bin/gunicorn --bind 127.0.0.1:8090 app:app"
echo "4. Set up Nginx reverse proxy to forward requests to port 8090"
echo ""
echo "To test the setup again, run:"
echo "sudo -u $APP_USER venv/bin/python test_setup.py"
echo ""
echo "Current directory permissions:"
ls -la "$APP_DIR"
echo ""
echo "Virtual environment location: $APP_DIR/venv" 