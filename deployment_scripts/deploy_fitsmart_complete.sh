#!/bin/bash
#
# HealthyRizz Complete Deployment Script
# -----------------------------------
# This script completely automates the deployment of the HealthyRizz application
# on a Hostinger VPS with CloudPanel, configuring all necessary components:
# - Python environment & dependencies
# - PostgreSQL database
# - Nginx configuration
# - SSL certificates
# - Gunicorn service
# - Application settings & migrations
#
# Compatible with Python 3.8-3.12 and Ubuntu 20.04/22.04/24.04
#

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error

# Text formatting
BOLD="\033[1m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RESET="\033[0m"

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${RESET} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${RESET} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${RESET} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${RESET} $1"
}

prompt_yes_no() {
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes (y) or no (n).";;
        esac
    done
}

check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Function to detect OS
detect_os() {
    log_info "Detecting operating system..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME=$NAME
        OS_VERSION=$VERSION_ID
        log_success "Detected: $OS_NAME $OS_VERSION"
    else
        log_error "Unable to detect operating system"
        exit 1
    fi
    
    # Check if running on Ubuntu
    if [[ "$OS_NAME" != *"Ubuntu"* ]]; then
        log_warning "This script is optimized for Ubuntu. Your OS: $OS_NAME"
        if ! prompt_yes_no "Continue anyway?"; then
            log_info "Exiting by user request"
            exit 0
        fi
    fi
}

# Function to detect CloudPanel
detect_cloudpanel() {
    log_info "Checking for CloudPanel..."
    
    # Check for CloudPanel in multiple ways
    if [ -d "/etc/cloudpanel" ] || [ -d "/opt/cloudpanel" ] || [ -d "/home/cloudpanel" ]; then
        CLOUDPANEL_INSTALLED=true
        
        # Try to get version
        if [ -f "/etc/cloudpanel/version" ]; then
            CLOUDPANEL_VERSION=$(grep -oP 'version=\K[0-9.]+' /etc/cloudpanel/version 2>/dev/null || echo "unknown")
        else
            CLOUDPANEL_VERSION="detected"
        fi
        
        log_success "CloudPanel detected (version $CLOUDPANEL_VERSION)"
        
        # Check if this is Hostinger VPS with CloudPanel
        if [ -d "/home/healthyrizz" ] || [[ $(hostname) == *"srv"* ]]; then
            log_success "Detected Hostinger VPS with CloudPanel"
            HOSTINGER_VPS=true
        else
            HOSTINGER_VPS=false
        fi
    else
        CLOUDPANEL_INSTALLED=false
        HOSTINGER_VPS=false
        log_warning "CloudPanel not detected. This script works best with CloudPanel."
        if ! prompt_yes_no "Continue without CloudPanel?"; then
            log_info "Exiting by user request"
            exit 0
        fi
    fi
}

# Function to detect Python version
detect_python() {
    log_info "Checking for Python installation..."
    
    # Check for Python 3 executable
    PYTHON_CMD=""
    for cmd in python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
        if command -v $cmd &> /dev/null; then
            PYTHON_CMD=$cmd
            PYTHON_VERSION=$($cmd -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
            log_success "Found $PYTHON_CMD (version $PYTHON_VERSION)"
            break
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        log_warning "Python 3 not found. Will install Python 3.10."
    elif [ "$(echo $PYTHON_VERSION | cut -d. -f1)" -lt 3 ] || [ "$(echo $PYTHON_VERSION | cut -d. -f2)" -lt 8 ]; then
        log_warning "Python version $PYTHON_VERSION is too old. HealthyRizz requires Python 3.8+."
        PYTHON_CMD=""
    fi
}

# Function to get deployment information
get_deployment_info() {
    echo
    echo -e "${BOLD}HealthyRizz Deployment Configuration${RESET}"
    echo "----------------------------------------"
    echo
    
    # Get application information
    read -p "Domain name (e.g., healthyrizz.example.com): " DOMAIN_NAME
    read -p "Application name (default: healthyrizz): " APP_NAME
    APP_NAME=${APP_NAME:-healthyrizz}
    
    # Database configuration
    echo
    echo -e "${BOLD}Database Configuration${RESET}"
    if $CLOUDPANEL_INSTALLED; then
        log_info "Using CloudPanel database naming convention"
        DB_NAME="cp_${APP_NAME}_db"
        DB_USER="cp_${APP_NAME}_user"
    else
        read -p "Database name (default: ${APP_NAME}_db): " DB_NAME_INPUT
        DB_NAME=${DB_NAME_INPUT:-${APP_NAME}_db}
        read -p "Database user (default: ${APP_NAME}_user): " DB_USER_INPUT
        DB_USER=${DB_USER_INPUT:-${APP_NAME}_user}
    fi
    
    read -s -p "Database password: " DB_PASSWORD
    echo
    read -p "Database host (default: localhost): " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    read -p "Database port (default: 5432): " DB_PORT
    DB_PORT=${DB_PORT:-5432}
    
    # Environment type
    echo
    if prompt_yes_no "Is this a production deployment?"; then
        ENVIRONMENT="production"
        DEBUG_MODE="False"
    else
        ENVIRONMENT="development"
        DEBUG_MODE="True"
    fi
    
    # Web server configuration
    echo
    echo -e "${BOLD}Web Server Configuration${RESET}"
    read -p "Application port (default: 8000): " APP_PORT
    APP_PORT=${APP_PORT:-8000}
    
    # SSL configuration
    if prompt_yes_no "Configure SSL with Let's Encrypt?"; then
        USE_SSL=true
        read -p "Email for Let's Encrypt certificate (default: admin@${DOMAIN_NAME}): " SSL_EMAIL
        SSL_EMAIL=${SSL_EMAIL:-admin@${DOMAIN_NAME}}
    else
        USE_SSL=false
    fi
    
    # Advanced options
    echo
    echo -e "${BOLD}Advanced Configuration${RESET}"
    read -p "Gunicorn workers (default: 4): " GUNICORN_WORKERS
    GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
    read -p "Session lifetime in seconds (default: 1800): " SESSION_LIFETIME
    SESSION_LIFETIME=${SESSION_LIFETIME:-1800}
    
    # API keys and services
    echo
    echo -e "${BOLD}External Services${RESET}"
    
    if prompt_yes_no "Configure Stripe payment processing?"; then
        read -s -p "Stripe secret key: " STRIPE_SECRET_KEY
        echo
        read -s -p "Stripe webhook secret: " STRIPE_WEBHOOK_SECRET
        echo
    else
        STRIPE_SECRET_KEY=""
        STRIPE_WEBHOOK_SECRET=""
    fi
    
    if prompt_yes_no "Configure Twilio SMS notifications?"; then
        read -s -p "Twilio account SID: " TWILIO_ACCOUNT_SID
        echo
        read -s -p "Twilio auth token: " TWILIO_AUTH_TOKEN
        echo
        read -p "Twilio phone number: " TWILIO_PHONE_NUMBER
    else
        TWILIO_ACCOUNT_SID=""
        TWILIO_AUTH_TOKEN=""
        TWILIO_PHONE_NUMBER=""
    fi
    
    if prompt_yes_no "Configure SendGrid email service?"; then
        read -s -p "SendGrid API key: " SENDGRID_API_KEY
        echo
    else
        SENDGRID_API_KEY=""
    fi
    
    # Generate random secret key for session
    SESSION_SECRET=$(openssl rand -hex 32)
    
    # Confirm deployment
    echo
    echo -e "${BOLD}Deployment Summary${RESET}"
    echo "----------------------------------------"
    echo "Domain: $DOMAIN_NAME"
    echo "Application: $APP_NAME"
    echo "Environment: $ENVIRONMENT"
    echo "Database: $DB_NAME on $DB_HOST:$DB_PORT"
    echo "SSL enabled: $USE_SSL"
    echo "Application port: $APP_PORT"
    echo "Debug mode: $DEBUG_MODE"
    echo
    
    if ! prompt_yes_no "Proceed with deployment?"; then
        log_info "Exiting by user request"
        exit 0
    fi
}

# Function to install system dependencies
install_system_dependencies() {
    log_info "Installing system dependencies..."
    
    apt-get update
    
    # Install Python if not found
    if [ -z "$PYTHON_CMD" ]; then
        log_info "Installing Python 3.10..."
        apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip
        PYTHON_CMD="python3.10"
        PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        log_success "Installed Python $PYTHON_VERSION"
    fi
    
    # Install PostgreSQL if not already installed
    if ! command -v psql &> /dev/null; then
        log_info "Installing PostgreSQL..."
        apt-get install -y postgresql postgresql-contrib
        log_success "Installed PostgreSQL"
    fi
    
    # Install Nginx if not already installed
    if ! command -v nginx &> /dev/null && ! $CLOUDPANEL_INSTALLED; then
        log_info "Installing Nginx..."
        apt-get install -y nginx
        log_success "Installed Nginx"
    fi
    
    # Install other dependencies
    log_info "Installing additional dependencies..."
    apt-get install -y build-essential libpq-dev python3-dev supervisor certbot acl
    
    log_success "System dependencies installed"
}

# Function to set up Python environment
setup_python_environment() {
    log_info "Setting up Python environment..."
    
    # Create application directory if it doesn't exist
    if [ ! -d "$APP_DIR" ]; then
        mkdir -p "$APP_DIR"
        log_info "Created application directory: $APP_DIR"
    fi
    
    # Set ownership if not using CloudPanel
    if ! $CLOUDPANEL_INSTALLED; then
        chown -R www-data:www-data "$APP_DIR"
    fi
    
    # Create and activate virtual environment
    if [ ! -d "$APP_DIR/venv" ]; then
        $PYTHON_CMD -m venv "$APP_DIR/venv"
        log_info "Created virtual environment at $APP_DIR/venv"
    fi
    
    # Upgrade pip
    "$APP_DIR/venv/bin/pip" install --upgrade pip
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    "$APP_DIR/venv/bin/pip" install flask flask-sqlalchemy flask-wtf gunicorn psycopg2-binary python-dotenv email-validator flask-limiter flask-mail fpdf pandas cryptography
    
    # Install external service libraries if configured
    if [ ! -z "$STRIPE_SECRET_KEY" ]; then
        "$APP_DIR/venv/bin/pip" install stripe
    fi
    
    if [ ! -z "$TWILIO_ACCOUNT_SID" ]; then
        "$APP_DIR/venv/bin/pip" install twilio
    fi
    
    if [ ! -z "$SENDGRID_API_KEY" ]; then
        "$APP_DIR/venv/bin/pip" install sendgrid
    fi
    
    log_success "Python environment set up successfully"
}

# Function to set up the PostgreSQL database
setup_database() {
    log_info "Setting up PostgreSQL database..."
    
    # Check if we're on Hostinger CloudPanel
    if $HOSTINGER_VPS; then
        log_info "Using CloudPanel PostgreSQL management..."
        
        # Check if database exists
        if mysqlshow -u root cp_admin | grep -qw "$DB_NAME"; then
            log_warning "Database $DB_NAME already exists in CloudPanel"
            log_info "Using existing database. Make sure your database settings match your CloudPanel configuration."
        else
            log_warning "Please create the database through CloudPanel's interface"
            log_warning "Database name: $DB_NAME"
            log_warning "Database user: $DB_USER"
            log_warning "Once created, update the .env file with the correct credentials"
            
            # Check if .env already exists
            if [ -f "$APP_DIR/.env" ]; then
                log_info "The .env file will be created in the next step with the provided database settings"
                log_info "You can adjust it later if needed"
            fi
        fi
        
        log_warning "On CloudPanel, database management is typically done through the control panel"
        log_warning "Please ensure your database is set up correctly in CloudPanel"
        log_success "Database setup for CloudPanel completed"
        return
    fi
    
    # Standard PostgreSQL setup for non-CloudPanel environments
    # Check if we can connect to PostgreSQL with postgres user
    if command -v psql &> /dev/null && id -u postgres &> /dev/null; then
        # Check if database already exists
        if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
            log_warning "Database $DB_NAME already exists"
            if prompt_yes_no "Drop existing database and recreate?"; then
                sudo -u postgres psql -c "DROP DATABASE $DB_NAME;"
                log_info "Dropped existing database $DB_NAME"
            else
                log_info "Using existing database $DB_NAME"
                return
            fi
        fi
        
        # Check if user already exists
        if sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
            log_warning "Database user $DB_USER already exists"
            if prompt_yes_no "Drop existing user and recreate?"; then
                sudo -u postgres psql -c "DROP USER $DB_USER;"
                log_info "Dropped existing user $DB_USER"
            else
                log_info "Using existing user $DB_USER"
                # Update password
                sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
                log_info "Updated password for user $DB_USER"
                return
            fi
        fi
        
        # Create database user
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        
        # Create database
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        
        # Grant privileges
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
        
        log_success "Database setup completed"
    else
        # Direct PostgreSQL access
        log_warning "Could not access PostgreSQL with standard postgres user"
        log_info "Attempting to connect to PostgreSQL directly..."
        
        # Check if psql is available
        if command -v psql &> /dev/null; then
            # Create directly with admin credentials
            log_warning "Please enter PostgreSQL admin credentials when prompted"
            
            # Prompt for admin credentials
            read -p "PostgreSQL admin username (default: postgres): " PGADMIN_USER
            PGADMIN_USER=${PGADMIN_USER:-postgres}
            read -s -p "PostgreSQL admin password: " PGADMIN_PASSWORD
            echo
            
            # Create database
            PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h localhost -c "CREATE DATABASE $DB_NAME;"
            PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h localhost -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
            PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
            
            log_success "Database setup completed"
        else
            log_error "PostgreSQL client (psql) not found"
            log_warning "Cannot automatically set up the database"
            log_warning "Please set up the database manually with these settings:"
            log_warning "Database name: $DB_NAME"
            log_warning "Database user: $DB_USER"
            log_warning "Database password: [as provided]"
            
            if prompt_yes_no "Continue with deployment anyway?"; then
                log_info "Continuing deployment without database setup"
                return
            else
                log_error "Deployment aborted"
                exit 1
            fi
        fi
    fi
}

# Function to create application configuration
create_app_config() {
    log_info "Creating application configuration..."
    
    # Create .env file
    cat > "$APP_DIR/.env" << EOF
# HealthyRizz Environment Configuration
# Generated by deploy_healthyrizz_complete.sh

# Application Settings
FLASK_APP=main.py
FLASK_ENV=$ENVIRONMENT
DEBUG=$DEBUG_MODE
SESSION_SECRET=$SESSION_SECRET
SESSION_LIFETIME=$SESSION_LIFETIME

# Database Connection
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
SQLALCHEMY_DATABASE_URI=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
PGDATABASE=$DB_NAME
PGUSER=$DB_USER
PGPASSWORD=$DB_PASSWORD
PGHOST=$DB_HOST
PGPORT=$DB_PORT

# Web Server
PORT=$APP_PORT
HOST=0.0.0.0
DOMAIN=$DOMAIN_NAME

# External Services
EOF

    # Add external service credentials if provided
    if [ ! -z "$STRIPE_SECRET_KEY" ]; then
        cat >> "$APP_DIR/.env" << EOF
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET
EOF
    fi
    
    if [ ! -z "$TWILIO_ACCOUNT_SID" ]; then
        cat >> "$APP_DIR/.env" << EOF
TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER
EOF
    fi
    
    if [ ! -z "$SENDGRID_API_KEY" ]; then
        cat >> "$APP_DIR/.env" << EOF
SENDGRID_API_KEY=$SENDGRID_API_KEY
EOF
    fi
    
    chmod 600 "$APP_DIR/.env"
    log_success "Created application environment file ($APP_DIR/.env)"
    
    # Create Gunicorn configuration
    cat > "$APP_DIR/gunicorn.conf.py" << EOF
# Gunicorn configuration file
# Generated by deploy_healthyrizz_complete.sh

# Server socket
bind = "0.0.0.0:$APP_PORT"
backlog = 2048

# Worker processes
workers = $GUNICORN_WORKERS
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%({X-Real-IP}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'gunicorn-healthyrizz'

# Server hooks
def on_starting(server):
    pass

def on_reload(server):
    pass

def when_ready(server):
    pass
EOF

    log_success "Created Gunicorn configuration ($APP_DIR/gunicorn.conf.py)"
}

# Function to set up systemd service
setup_systemd_service() {
    log_info "Setting up systemd service..."
    
    cat > "/etc/systemd/system/${APP_NAME}.service" << EOF
[Unit]
Description=Gunicorn instance for HealthyRizz application
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --config $APP_DIR/gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=5
StartLimitIntervalSec=0

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd daemon
    systemctl daemon-reload
    
    # Enable and start service
    systemctl enable "${APP_NAME}.service"
    
    log_success "Systemd service configured (${APP_NAME}.service)"
}

# Function to configure Nginx
configure_nginx() {
    log_info "Configuring Nginx..."
    
    # Skip if using CloudPanel
    if $CLOUDPANEL_INSTALLED; then
        log_info "Using CloudPanel for Nginx configuration"
        return
    fi
    
    # Create Nginx configuration
    cat > "/etc/nginx/sites-available/${DOMAIN_NAME}.conf" << EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};
    
    # Redirect HTTP to HTTPS if SSL is enabled
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";
    
    # Application proxy
    location / {
        proxy_pass http://127.0.0.1:${APP_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # Logs
    access_log /var/log/nginx/${DOMAIN_NAME}-access.log;
    error_log /var/log/nginx/${DOMAIN_NAME}-error.log;
}
EOF
    
    # Enable site
    ln -sf "/etc/nginx/sites-available/${DOMAIN_NAME}.conf" "/etc/nginx/sites-enabled/"
    
    # Test Nginx configuration
    nginx -t
    
    # Reload Nginx
    systemctl reload nginx
    
    log_success "Nginx configured for ${DOMAIN_NAME}"
}

# Function to set up SSL with Let's Encrypt
setup_ssl() {
    log_info "Setting up SSL with Let's Encrypt..."
    
    # Skip if not using SSL
    if ! $USE_SSL; then
        log_info "SSL setup skipped as per configuration"
        return
    fi
    
    # Skip if using CloudPanel
    if $CLOUDPANEL_INSTALLED; then
        log_info "Using CloudPanel for SSL configuration"
        return
    fi
    
    # Check if certificate already exists
    if [ -d "/etc/letsencrypt/live/${DOMAIN_NAME}" ]; then
        log_warning "SSL certificate already exists for ${DOMAIN_NAME}"
        if prompt_yes_no "Renew SSL certificate?"; then
            certbot renew --nginx --quiet
            log_success "SSL certificate renewed"
        else
            log_info "Using existing SSL certificate"
        fi
        return
    fi
    
    # Obtain certificate
    certbot --nginx -d "${DOMAIN_NAME}" -d "www.${DOMAIN_NAME}" --non-interactive --agree-tos --email "${SSL_EMAIL}" --redirect
    
    log_success "SSL certificate obtained and configured"
}

# Function to deploy application
deploy_application() {
    log_info "Deploying HealthyRizz application..."
    
    # Check if we need to pull from git or copy files
    if [ -d ".git" ]; then
        log_info "Detected Git repository. Copying to deployment directory..."
        
        # Create temporary archive of current directory (excluding venv, node_modules, etc)
        tar --exclude='venv' --exclude='node_modules' --exclude='.git' -czf /tmp/healthyrizz-deploy.tar.gz .
        
        # Extract to target directory
        tar -xzf /tmp/healthyrizz-deploy.tar.gz -C "$APP_DIR"
        
        # Clean up
        rm /tmp/healthyrizz-deploy.tar.gz
    else
        log_info "No Git repository detected. Copying current directory..."
        
        # Copy application files
        cp -r * "$APP_DIR/"
    fi
    
    # Ensure proper ownership
    chown -R www-data:www-data "$APP_DIR"
    
    log_success "Application files deployed to $APP_DIR"
}

# Function to run database migrations
run_database_migrations() {
    log_info "Running database migrations..."
    
    PYTHON="$APP_DIR/venv/bin/python"
    
    # Run migrations
    cd "$APP_DIR"
    MIGRATIONS_OUTPUT=$($PYTHON migrations.py 2>&1)
    
    # Check for success
    if [[ $MIGRATIONS_OUTPUT == *"Database migrations completed"* ]]; then
        log_success "Database migrations completed successfully"
    else
        log_error "Database migrations failed. Output:"
        echo "$MIGRATIONS_OUTPUT"
        
        if prompt_yes_no "Try running migrations again with more verbose output?"; then
            cd "$APP_DIR"
            echo "import logging; logging.basicConfig(level=logging.DEBUG); from migrations import run_migrations; run_migrations()" | $PYTHON
        fi
    fi
}

# Function to check application status
check_application_status() {
    log_info "Checking application status..."
    
    # Start the application if not already running
    systemctl start "${APP_NAME}.service"
    
    # Check if service is running
    if systemctl is-active --quiet "${APP_NAME}.service"; then
        log_success "Application service is running"
    else
        log_error "Application service failed to start"
        echo "Checking logs:"
        journalctl -u "${APP_NAME}.service" -n 50 --no-pager
    fi
    
    # Check if application is responding
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:${APP_PORT}/" | grep -q "200\|301\|302"; then
        log_success "Application is responding on port ${APP_PORT}"
    else
        log_warning "Application is not responding on port ${APP_PORT}"
    fi
    
    # If using Nginx, check if site is accessible
    if ! $CLOUDPANEL_INSTALLED; then
        if curl -s -o /dev/null -w "%{http_code}" -H "Host: ${DOMAIN_NAME}" "http://localhost/" | grep -q "200\|301\|302"; then
            log_success "Nginx is properly proxying requests"
        else
            log_warning "Nginx is not properly proxying requests"
        fi
    fi
}

# Function to display final instructions
display_final_instructions() {
    echo
    echo -e "${BOLD}${GREEN}HealthyRizz Deployment Complete!${RESET}"
    echo "----------------------------------------"
    echo
    echo "Your HealthyRizz application has been deployed with the following details:"
    echo
    echo "Application URL: ${USE_SSL:+https://}${USE_SSL:-http://}${DOMAIN_NAME}"
    echo "Application directory: ${APP_DIR}"
    echo "Environment file: ${APP_DIR}/.env"
    echo "Service name: ${APP_NAME}.service"
    echo
    echo "To manage your application:"
    echo "  - Start: sudo systemctl start ${APP_NAME}.service"
    echo "  - Stop: sudo systemctl stop ${APP_NAME}.service"
    echo "  - Restart: sudo systemctl restart ${APP_NAME}.service"
    echo "  - View logs: sudo journalctl -u ${APP_NAME}.service -f"
    echo
    
    if $CLOUDPANEL_INSTALLED; then
        echo "CloudPanel is managing your web server. You may need to configure your website in the CloudPanel interface."
    fi
    
    echo "If you encounter any issues, please check the application logs for detailed information."
    echo
}

# Function to set the application directory
set_app_directory() {
    # Set appropriate application directory based on environment
    if $HOSTINGER_VPS; then
        APP_DIR="/home/${APP_NAME}/htdocs/www.${DOMAIN_NAME}"
        log_info "Using Hostinger CloudPanel directory structure: $APP_DIR"
    else
        APP_DIR="/var/www/${APP_NAME}"
        log_info "Using standard directory structure: $APP_DIR"
    fi
    
    # Export the APP_DIR for use in other functions
    export APP_DIR
}

# Main function
main() {
    echo -e "${BOLD}${BLUE}HealthyRizz Complete Deployment Script${RESET}"
    echo "=========================================="
    echo
    
    # Initialize variables
    HOSTINGER_VPS=false
    CLOUDPANEL_INSTALLED=false
    
    # Check if running as root
    check_root
    
    # Detect system information
    detect_os
    detect_cloudpanel
    detect_python
    
    # Get deployment information
    get_deployment_info
    
    # Set application directory
    set_app_directory
    
    # Install system dependencies
    install_system_dependencies
    
    # Set up Python environment
    setup_python_environment
    
    # Set up database
    setup_database
    
    # Create application configuration
    create_app_config
    
    # Set up systemd service
    setup_systemd_service
    
    # Configure Nginx
    if ! $CLOUDPANEL_INSTALLED; then
        configure_nginx
        
        # Set up SSL
        if $USE_SSL; then
            setup_ssl
        fi
    fi
    
    # Deploy application
    deploy_application
    
    # Run database migrations
    run_database_migrations
    
    # Check application status
    check_application_status
    
    # Display final instructions
    display_final_instructions
}

# Run main function
main
