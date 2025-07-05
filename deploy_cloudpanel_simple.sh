#!/bin/bash

# HealthyRizz CloudPanel Deployment Script
# Optimized for CloudPanel environment with root access
# Domain: healthyrizz.in
# Port: 8090

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration for CloudPanel
APP_NAME="healthyrizz"
DOMAIN="healthyrizz.in"
PORT="8090"
APP_USER="healthyrizz"
APP_DIR="/home/${APP_USER}/htdocs/${DOMAIN}"
PYTHON_VERSION="3.11"

# Logging function
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

# CloudPanel environment check
check_cloudpanel() {
    if [ ! -d "/usr/local/cloudpanel" ]; then
        warning "CloudPanel not detected, but continuing with deployment..."
    else
        log "CloudPanel environment detected"
    fi
}

# Main deployment function
main() {
    log "Starting HealthyRizz CloudPanel deployment..."
    
    # Check if we're in the right directory
    if [ ! -f "main.py" ]; then
        error "main.py not found. Please run this script from the HealthyRizz project directory"
    fi
    
    # Basic system updates
    log "Updating system packages..."
    apt update
    apt install -y python3-pip python3-venv python3-dev build-essential libpq-dev redis-server
    
    # Ensure we're in the app directory
    cd "$APP_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    log "Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn psycopg2-binary
    
    # Generate environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        log "Creating production environment file..."
        SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
        CSRF_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
        
        cat > .env << EOF
# HealthyRizz Production Environment
SECRET_KEY=${SECRET_KEY}
WTF_CSRF_SECRET_KEY=${CSRF_KEY}

# Environment
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=sqlite:///healthyrizz.db

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=admin@healthyrizz.in
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=admin@healthyrizz.in

# Payment Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Redis
REDIS_URL=redis://localhost:6379/0

# Security Settings
SESSION_COOKIE_SECURE=False
WTF_CSRF_SSL_STRICT=False

# Domain
DOMAIN_NAME=${DOMAIN}
BASE_URL=https://${DOMAIN}
EOF
        chmod 600 .env
        chown $APP_USER:$APP_USER .env
    fi
    
    # Initialize database
    log "Initializing database..."
    source venv/bin/activate
    if [ -f "init_database.py" ]; then
        python init_database.py
    else
        python -c "
from main import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
    fi
    
    # Create Gunicorn configuration
    log "Creating Gunicorn configuration..."
    cat > gunicorn.conf.py << EOF
import multiprocessing

bind = "127.0.0.1:${PORT}"
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
preload_app = True
chdir = "${APP_DIR}"
EOF
    
    # Create systemd service
    log "Creating systemd service..."
    cat > /etc/systemd/system/healthyrizz.service << EOF
[Unit]
Description=HealthyRizz Gunicorn Application
After=network.target

[Service]
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/venv/bin
ExecStart=${APP_DIR}/venv/bin/gunicorn --config gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # Set proper permissions
    chown -R $APP_USER:$APP_USER $APP_DIR
    chmod +x gunicorn.conf.py
    
    # Start Redis
    log "Starting Redis service..."
    systemctl enable redis-server
    systemctl start redis-server
    
    # Enable and start the service
    log "Starting HealthyRizz service..."
    systemctl daemon-reload
    systemctl enable healthyrizz
    systemctl restart healthyrizz
    
    # Check service status
    sleep 3
    if systemctl is-active --quiet healthyrizz; then
        log "✅ HealthyRizz service is running successfully!"
        log "🌐 Application should be available at: http://${DOMAIN}:${PORT}"
        log "🔧 Configure CloudPanel to proxy to localhost:${PORT}"
    else
        error "❌ HealthyRizz service failed to start"
        systemctl status healthyrizz
    fi
    
    # Display useful information
    info "Deployment completed! Next steps:"
    echo "1. Configure CloudPanel to proxy ${DOMAIN} to localhost:${PORT}"
    echo "2. Update email and payment credentials in .env file"
    echo "3. Set up SSL certificate for HTTPS"
    echo ""
    echo "Service management commands:"
    echo "- View logs: journalctl -u healthyrizz -f"
    echo "- Restart: systemctl restart healthyrizz"
    echo "- Status: systemctl status healthyrizz"
}

# Run main function
check_cloudpanel
main 