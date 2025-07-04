#!/bin/bash

# Simplified VPS Deployment Script for HealthyRizz
# This script addresses permission issues and provides a clean deployment

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

log "Starting HealthyRizz VPS Deployment..."

# Step 1: Fix directory permissions
log "Step 1: Fixing directory permissions..."

# Create directories with proper ownership
mkdir -p "$APP_DIR"
mkdir -p "/home/healthyrizz/logs"
mkdir -p "/home/healthyrizz/backups"

# Set ownership - app user owns the app, web user can read
chown -R $APP_USER:$WEB_USER "$APP_DIR"
chown -R $APP_USER:$APP_USER "/home/healthyrizz/logs"
chown -R $APP_USER:$APP_USER "/home/healthyrizz/backups"

# Set permissions - app user can read/write, web user can read
chmod -R 755 "$APP_DIR"
chmod -R 755 "/home/healthyrizz/logs"
chmod -R 755 "/home/healthyrizz/backups"

# Ensure htdocs is accessible
chmod 755 "/home/healthyrizz/htdocs"

log "✓ Directory permissions fixed"

# Step 2: Create virtual environment
log "Step 2: Creating Python virtual environment..."

cd "$APP_DIR"

# Remove existing venv if it exists
if [ -d "venv" ]; then
    log "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment as the app user
log "Creating new virtual environment..."
sudo -u $APP_USER python3 -m venv venv

# Verify creation
if [ ! -f "venv/bin/activate" ]; then
    error "Failed to create virtual environment"
fi

log "✓ Virtual environment created"

# Step 3: Install dependencies
log "Step 3: Installing Python dependencies..."

# Upgrade pip
sudo -u $APP_USER venv/bin/pip install --upgrade pip

# Install dependencies
if [ -f "requirements-production.txt" ]; then
    log "Installing from requirements-production.txt..."
    sudo -u $APP_USER venv/bin/pip install -r requirements-production.txt
elif [ -f "requirements.txt" ]; then
    log "Installing from requirements.txt..."
    sudo -u $APP_USER venv/bin/pip install -r requirements.txt
else
    warning "No requirements file found. Installing basic dependencies..."
    sudo -u $APP_USER venv/bin/pip install flask gunicorn psycopg2-binary redis flask-sqlalchemy flask-migrate flask-login flask-wtf
fi

log "✓ Dependencies installed"

# Step 4: Create environment configuration
log "Step 4: Setting up environment configuration..."

# Create .env file
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

# Set proper permissions for .env
chown $APP_USER:$APP_USER .env
chmod 600 .env

log "✓ Environment file created"

# Step 5: Create application directories
log "Step 5: Creating application directories..."

# Create necessary directories
sudo -u $APP_USER mkdir -p static/uploads
sudo -u $APP_USER mkdir -p static/videos
sudo -u $APP_USER mkdir -p static/images
sudo -u $APP_USER mkdir -p static/templates
sudo -u $APP_USER mkdir -p instance
sudo -u $APP_USER mkdir -p flask_session

# Set permissions
chmod -R 755 static/uploads
chmod -R 755 static/videos
chmod -R 755 static/images
chmod -R 755 instance
chmod -R 755 flask_session

log "✓ Application directories created"

# Step 6: Test the setup
log "Step 6: Testing the setup..."

# Test virtual environment
if sudo -u $APP_USER venv/bin/python -c "import flask; print('Flask imported successfully')"; then
    log "✓ Virtual environment test passed"
else
    error "Virtual environment test failed"
fi

# Test directory access
if sudo -u $APP_USER test -r "$APP_DIR"; then
    log "✓ Directory access test passed"
else
    error "Directory access test failed"
fi

# Step 7: Create systemd service
log "Step 7: Creating systemd service..."

cat > /etc/systemd/system/healthyrizz.service << EOL
[Unit]
Description=HealthyRizz Flask Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8090 --access-logfile /home/healthyrizz/logs/gunicorn-access.log --error-logfile /home/healthyrizz/logs/gunicorn-error.log app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable healthyrizz.service

log "✓ Systemd service created and enabled"

# Step 8: Create Nginx configuration
log "Step 8: Creating Nginx configuration..."

cat > /etc/nginx/sites-available/healthyrizz << EOL
server {
    listen 80;
    server_name healthyrizz.in www.healthyrizz.in;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Static files
    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Flask application
    location / {
        proxy_pass http://127.0.0.1:8090;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOL

# Enable the site
ln -sf /etc/nginx/sites-available/healthyrizz /etc/nginx/sites-enabled/

# Test Nginx configuration
if nginx -t; then
    systemctl reload nginx
    log "✓ Nginx configuration created and loaded"
else
    error "Nginx configuration test failed"
fi

# Step 9: Final verification
log "Step 9: Final verification..."

# Create a simple test script
cat > test_deployment.py << EOL
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
    print("Testing HealthyRizz VPS Deployment...")
    print("=" * 40)
    
    success = True
    success &= test_imports()
    success &= test_permissions()
    
    if success:
        print("\\n✓ All tests passed! Deployment is ready.")
        sys.exit(0)
    else:
        print("\\n✗ Some tests failed. Please check the setup.")
        sys.exit(1)
EOL

chown $APP_USER:$APP_USER test_deployment.py
chmod +x test_deployment.py

# Run the test
if sudo -u $APP_USER venv/bin/python test_deployment.py; then
    log "✓ All tests passed! Deployment is complete."
else
    warning "Some tests failed. Please check the output above."
fi

# Step 10: Display final instructions
echo ""
log "Deployment completed successfully!"
echo ""
echo "🎉 HealthyRizz is now deployed on your VPS!"
echo ""
echo "📋 Next steps:"
echo "1. Update the .env file with your actual database password and settings"
echo "2. Set up PostgreSQL database and user"
echo "3. Run database migrations: sudo -u $APP_USER venv/bin/python init_db.py"
echo "4. Start the application: sudo systemctl start healthyrizz"
echo "5. Check status: sudo systemctl status healthyrizz"
echo "6. View logs: sudo journalctl -u healthyrizz -f"
echo ""
echo "🌐 Your application will be available at:"
echo "   http://healthyrizz.in (after DNS is configured)"
echo "   http://your-server-ip (immediately)"
echo ""
echo "🔧 Useful commands:"
echo "   Start service: sudo systemctl start healthyrizz"
echo "   Stop service: sudo systemctl stop healthyrizz"
echo "   Restart service: sudo systemctl restart healthyrizz"
echo "   View logs: sudo journalctl -u healthyrizz -f"
echo "   Test setup: sudo -u $APP_USER venv/bin/python test_deployment.py"
echo ""
echo "📁 Application directory: $APP_DIR"
echo "🐍 Virtual environment: $APP_DIR/venv"
echo "📝 Environment file: $APP_DIR/.env"
echo ""
echo "⚠️  Important: Don't forget to:"
echo "   - Update the database password in .env"
echo "   - Configure your domain DNS"
echo "   - Set up SSL certificate (Let's Encrypt recommended)"
echo "   - Change the default admin password" 