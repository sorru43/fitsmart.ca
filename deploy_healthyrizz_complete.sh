#!/bin/bash

# HealthyRizz Complete Deployment Script
# Supports CloudPanel, Ubuntu VPS, and general Linux deployments
# Version: 2.0
# Date: December 2024

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="healthyrizz"
DOMAIN="healthyrizz.in"
PORT="8090"
APP_USER="healthyrizz"
APP_DIR="/home/${APP_USER}/htdocs/${DOMAIN}"
PYTHON_VERSION="3.11"
BACKUP_DIR="/home/${APP_USER}/backups"

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

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
    fi
}

# Detect deployment environment
detect_environment() {
    log "Detecting deployment environment..."
    
    if [ -d "/usr/local/cloudpanel" ]; then
        DEPLOYMENT_TYPE="cloudpanel"
        log "Detected CloudPanel environment"
    elif command -v systemctl &> /dev/null; then
        DEPLOYMENT_TYPE="systemd"
        log "Detected SystemD environment (Ubuntu/Debian)"
    else
        DEPLOYMENT_TYPE="generic"
        log "Detected generic Linux environment"
    fi
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    # Update package list
    sudo apt update
    
    # Install essential packages
    sudo apt install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python${PYTHON_VERSION}-venv \
        python3-pip \
        nginx \
        redis-server \
        postgresql \
        postgresql-contrib \
        supervisor \
        git \
        curl \
        wget \
        unzip \
        build-essential \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        libjpeg-dev \
        libpng-dev \
        libwebp-dev \
        zlib1g-dev
    
    log "System dependencies installed successfully"
}

# Create application user and directories
setup_user_and_directories() {
    log "Setting up user and directories..."
    
    # Create application user if it doesn't exist
    if ! id "$APP_USER" &>/dev/null; then
        sudo useradd -m -s /bin/bash "$APP_USER"
        log "Created user: $APP_USER"
    fi
    
    # Create directories
    sudo mkdir -p "$APP_DIR"
    sudo mkdir -p "$BACKUP_DIR"
    sudo mkdir -p "/var/log/$APP_NAME"
    
    # Set ownership
    sudo chown -R "$APP_USER:$APP_USER" "/home/$APP_USER"
    sudo chown -R "$APP_USER:$APP_USER" "/var/log/$APP_NAME"
    
    log "User and directories setup completed"
}

# Backup existing installation
backup_existing() {
    if [ -d "$APP_DIR" ] && [ "$(ls -A $APP_DIR)" ]; then
        log "Backing up existing installation..."
        
        BACKUP_NAME="${APP_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
        sudo -u "$APP_USER" cp -r "$APP_DIR" "$BACKUP_DIR/$BACKUP_NAME"
        
        log "Backup created: $BACKUP_DIR/$BACKUP_NAME"
    fi
}

# Deploy application files
deploy_application() {
    log "Deploying application files..."
    
    # Copy application files (assuming we're in the source directory)
    if [ ! -f "main.py" ]; then
        error "main.py not found. Please run this script from the HealthyRizz project directory"
    fi
    
    # Create temporary deployment package
    TEMP_DIR=$(mktemp -d)
    
    # Copy essential files
    cp -r . "$TEMP_DIR/"
    
    # Remove unnecessary files
    rm -rf "$TEMP_DIR/.git" 2>/dev/null || true
    rm -rf "$TEMP_DIR/__pycache__" 2>/dev/null || true
    rm -rf "$TEMP_DIR"/*.log 2>/dev/null || true
    rm -rf "$TEMP_DIR/flask_session" 2>/dev/null || true
    rm -rf "$TEMP_DIR/.venv" 2>/dev/null || true
    rm -f "$TEMP_DIR/.env" 2>/dev/null || true
    
    # Copy to deployment directory
    sudo rm -rf "$APP_DIR"/*
    sudo cp -r "$TEMP_DIR"/* "$APP_DIR/"
    sudo chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    
    # Cleanup
    rm -rf "$TEMP_DIR"
    
    log "Application files deployed successfully"
}

# Setup Python environment
setup_python_environment() {
    log "Setting up Python virtual environment..."
    
    # Switch to app user for the rest of the setup
    sudo -u "$APP_USER" bash << EOF
cd "$APP_DIR"

# Create virtual environment
python${PYTHON_VERSION} -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn psycopg2-binary

EOF
    
    log "Python environment setup completed"
}

# Setup database
setup_database() {
    log "Setting up PostgreSQL database..."
    
    # Start PostgreSQL service
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres bash << EOF
createdb ${APP_NAME} 2>/dev/null || echo "Database already exists"
createuser ${APP_USER} 2>/dev/null || echo "User already exists"
psql -c "ALTER USER ${APP_USER} WITH PASSWORD '$(openssl rand -base64 32)';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE ${APP_NAME} TO ${APP_USER};"
EOF
    
    log "PostgreSQL database setup completed"
}

# Setup Redis
setup_redis() {
    log "Setting up Redis..."
    
    # Start Redis service
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    # Configure Redis for production
    sudo tee /etc/redis/redis.conf > /dev/null << EOF
bind 127.0.0.1
port 6379
timeout 0
tcp-keepalive 60
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
EOF
    
    sudo systemctl restart redis-server
    
    log "Redis setup completed"
}

# Generate production environment file
setup_environment() {
    log "Setting up production environment..."
    
    # Generate secure secrets
    SECRET_KEY=$(openssl rand -hex 32)
    CSRF_KEY=$(openssl rand -hex 32)
    WEBHOOK_SECRET=$(openssl rand -hex 24)
    
    # Create production .env file
    sudo -u "$APP_USER" tee "$APP_DIR/.env" > /dev/null << EOF
# HealthyRizz Production Environment
# Generated on $(date)

# Security Keys
SECRET_KEY=${SECRET_KEY}
WTF_CSRF_SECRET_KEY=${CSRF_KEY}

# Environment
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=sqlite:///healthyrizz.db

# Email Configuration (UPDATE WITH REAL VALUES)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Payment Configuration (UPDATE WITH REAL VALUES)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=${WEBHOOK_SECRET}

# Redis
REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/1

# Security Settings
SESSION_COOKIE_SECURE=False
WTF_CSRF_SSL_STRICT=False
PERMANENT_SESSION_LIFETIME=1800

# Domain
DOMAIN_NAME=${DOMAIN}
BASE_URL=https://${DOMAIN}
EOF
    
    # Set secure permissions
    sudo chmod 600 "$APP_DIR/.env"
    
    log "Production environment configured"
    warning "Please update the email and payment credentials in $APP_DIR/.env"
}

# Initialize database
initialize_database() {
    log "Initializing database..."
    
    sudo -u "$APP_USER" bash << EOF
cd "$APP_DIR"
source venv/bin/activate
python init_database.py
EOF
    
    log "Database initialized successfully"
}

# Setup Gunicorn service
setup_gunicorn() {
    log "Setting up Gunicorn service..."
    
    # Create Gunicorn config
    sudo -u "$APP_USER" tee "$APP_DIR/gunicorn.conf.py" > /dev/null << EOF
# Gunicorn configuration for HealthyRizz
import multiprocessing

bind = "127.0.0.1:${PORT}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "${APP_USER}"
group = "${APP_USER}"
pythonpath = "${APP_DIR}"
chdir = "${APP_DIR}"
daemon = False
pidfile = "/var/run/${APP_NAME}.pid"
accesslog = "/var/log/${APP_NAME}/access.log"
errorlog = "/var/log/${APP_NAME}/error.log"
loglevel = "info"
access_log_format = '%%(h)s %%(l)s %%(u)s %%(t)s "%%(r)s" %%(s)s %%(b)s "%%(f)s" "%%(a)s"'
EOF
    
    # Create systemd service file
    sudo tee "/etc/systemd/system/${APP_NAME}.service" > /dev/null << EOF
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

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable and start service
    sudo systemctl daemon-reload
    sudo systemctl enable "$APP_NAME"
    
    log "Gunicorn service configured"
}

# Setup Nginx
setup_nginx() {
    log "Setting up Nginx..."
    
    # Remove default site if it exists
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Create Nginx configuration
    sudo tee "/etc/nginx/sites-available/${APP_NAME}" > /dev/null << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # SSL Configuration (SSL certificates should be configured separately)
    # ssl_certificate /path/to/certificate.crt;
    # ssl_certificate_key /path/to/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Static files
    location /static {
        alias ${APP_DIR}/static;
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }
    
    # Media files
    location /uploads {
        alias ${APP_DIR}/static/uploads;
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:${PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
    
    # Enable site
    sudo ln -sf "/etc/nginx/sites-available/${APP_NAME}" "/etc/nginx/sites-enabled/"
    
    # Test Nginx configuration
    sudo nginx -t
    
    # Start Nginx
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    
    log "Nginx configured successfully"
}

# Setup SSL with Let's Encrypt (optional)
setup_ssl() {
    if command -v certbot &> /dev/null; then
        log "Setting up SSL with Let's Encrypt..."
        
        # Install SSL certificate
        sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN"
        
        log "SSL certificate installed"
    else
        warning "Certbot not found. SSL certificate needs to be configured manually"
    fi
}

# Setup log rotation
setup_logging() {
    log "Setting up log rotation..."
    
    sudo tee "/etc/logrotate.d/${APP_NAME}" > /dev/null << EOF
/var/log/${APP_NAME}/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0644 ${APP_USER} ${APP_USER}
    postrotate
        systemctl reload ${APP_NAME}
    endscript
}
EOF
    
    log "Log rotation configured"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up basic monitoring..."
    
    # Create monitoring script
    sudo tee "/usr/local/bin/${APP_NAME}-monitor" > /dev/null << 'EOF'
#!/bin/bash
# HealthyRizz monitoring script

APP_NAME="healthyrizz"
PORT="8090"
LOG_FILE="/var/log/${APP_NAME}/monitor.log"

check_service() {
    if ! systemctl is-active --quiet "$APP_NAME"; then
        echo "$(date): Service $APP_NAME is down, restarting..." >> "$LOG_FILE"
        systemctl restart "$APP_NAME"
    fi
}

check_port() {
    if ! nc -z localhost "$PORT"; then
        echo "$(date): Port $PORT is not responding, restarting service..." >> "$LOG_FILE"
        systemctl restart "$APP_NAME"
    fi
}

check_disk_space() {
    USAGE=$(df /home/${APP_USER} | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$USAGE" -gt 90 ]; then
        echo "$(date): Disk usage is at ${USAGE}%" >> "$LOG_FILE"
    fi
}

check_service
check_port
check_disk_space
EOF
    
    # Make monitoring script executable
    sudo chmod +x "/usr/local/bin/${APP_NAME}-monitor"
    
    # Add to crontab
    echo "*/5 * * * * /usr/local/bin/${APP_NAME}-monitor" | sudo crontab -u root -
    
    log "Basic monitoring configured"
}

# Start services
start_services() {
    log "Starting all services..."
    
    # Start Redis
    sudo systemctl start redis-server
    
    # Start PostgreSQL
    sudo systemctl start postgresql
    
    # Start application
    sudo systemctl start "$APP_NAME"
    
    # Start Nginx
    sudo systemctl start nginx
    
    # Check service status
    sleep 5
    
    if sudo systemctl is-active --quiet "$APP_NAME"; then
        log "Application service is running"
    else
        error "Application service failed to start"
    fi
    
    if sudo systemctl is-active --quiet nginx; then
        log "Nginx service is running"
    else
        error "Nginx service failed to start"
    fi
}

# Create deployment summary
create_summary() {
    log "Creating deployment summary..."
    
    sudo -u "$APP_USER" tee "$APP_DIR/DEPLOYMENT_INFO.md" > /dev/null << EOF
# HealthyRizz Deployment Summary

## Deployment Information
- **Date**: $(date)
- **Domain**: ${DOMAIN}
- **Port**: ${PORT}
- **Environment**: ${DEPLOYMENT_TYPE}
- **App Directory**: ${APP_DIR}
- **User**: ${APP_USER}

## Services
- **Application**: systemctl status ${APP_NAME}
- **Database**: PostgreSQL on localhost:5432
- **Cache**: Redis on localhost:6379
- **Web Server**: Nginx

## Important Files
- **Application**: ${APP_DIR}/
- **Environment**: ${APP_DIR}/.env
- **Logs**: /var/log/${APP_NAME}/
- **Nginx Config**: /etc/nginx/sites-available/${APP_NAME}
- **Service Config**: /etc/systemd/system/${APP_NAME}.service

## Commands
- **Start**: sudo systemctl start ${APP_NAME}
- **Stop**: sudo systemctl stop ${APP_NAME}
- **Restart**: sudo systemctl restart ${APP_NAME}
- **Logs**: sudo journalctl -u ${APP_NAME} -f
- **Status**: sudo systemctl status ${APP_NAME}

## Next Steps
1. Update email credentials in ${APP_DIR}/.env
2. Update payment gateway credentials in ${APP_DIR}/.env
3. Configure SSL certificate
4. Test all application functionality
5. Set up regular backups

## URLs
- **Application**: http://${DOMAIN}:${PORT} (or https://${DOMAIN} if SSL configured)
- **Admin Panel**: http://${DOMAIN}:${PORT}/admin
- **Health Check**: http://${DOMAIN}/health

## Admin Credentials
- **Email**: admin@healthyrizz.in
- **Password**: admin123
- **Note**: Change these credentials immediately after first login!
EOF
    
    log "Deployment summary created at $APP_DIR/DEPLOYMENT_INFO.md"
}

# Main deployment function
main() {
    log "Starting HealthyRizz deployment..."
    
    check_root
    detect_environment
    
    # Prompt for confirmation
    echo
    info "This will deploy HealthyRizz to: $APP_DIR"
    info "Domain: $DOMAIN"
    info "Port: $PORT"
    echo
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Deployment cancelled"
        exit 0
    fi
    
    install_dependencies
    setup_user_and_directories
    backup_existing
    deploy_application
    setup_python_environment
    setup_database
    setup_redis
    setup_environment
    initialize_database
    setup_gunicorn
    setup_nginx
    setup_logging
    setup_monitoring
    start_services
    create_summary
    
    echo
    log "🎉 HealthyRizz deployment completed successfully!"
    echo
    info "Application URL: http://${DOMAIN}:${PORT}"
    info "Admin credentials: admin@healthyrizz.in / admin123"
    warning "Don't forget to:"
    warning "1. Update email and payment credentials in ${APP_DIR}/.env"
    warning "2. Change admin password after first login"
    warning "3. Configure SSL certificate for production"
    echo
    log "Deployment summary available at: ${APP_DIR}/DEPLOYMENT_INFO.md"
}

# Run main function
main "$@" 