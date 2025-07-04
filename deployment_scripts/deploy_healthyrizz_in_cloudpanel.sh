#!/bin/bash
#
# HealthyRizz One-Shot Deployment Script for CloudPanel
# This script sets up the entire HealthyRizz application with PWA support,
# admin notification system, virtual environment, database configuration, and systemd service.
#
# Usage: bash deploy_healthyrizz_in_cloudpanel.sh

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration for healthyrizz.in
APP_NAME="healthyrizz"
APP_USER="www-data"
APP_GROUP="www-data"
APP_DIR="/home/${APP_NAME}/htdocs/www.${APP_NAME}.in"
VENV_DIR="${APP_DIR}/venv"
REQUIREMENTS_FILE="requirements.txt"
GUNICORN_CONFIG="${APP_DIR}/gunicorn_config.py"
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
LOG_DIR="/var/log/${APP_NAME}"
SOCKET_DIR="/var/run/${APP_NAME}"
GIT_REPO="https://github.com/yourusername/healthyrizz.git"  # Replace with your actual Git repository URL
GIT_BRANCH="main"  # Replace with your default branch

# Function to print status messages
print_status() {
    echo -e "${GREEN}[+] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "${RED}[x] $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# Create application directory structure
print_status "Creating application directory structure..."
mkdir -p ${APP_DIR}
mkdir -p ${LOG_DIR}
mkdir -p ${SOCKET_DIR}
mkdir -p ${APP_DIR}/static
mkdir -p ${APP_DIR}/media
mkdir -p ${APP_DIR}/instance

# Clone or update Git repository
print_status "Setting up Git repository..."
if [ -d "${APP_DIR}/.git" ]; then
    print_status "Updating existing Git repository..."
    cd ${APP_DIR}
    git fetch origin
    git reset --hard origin/${GIT_BRANCH}
    git clean -fd
else
    print_status "Cloning Git repository..."
    git clone ${GIT_REPO} ${APP_DIR}
    cd ${APP_DIR}
    git checkout ${GIT_BRANCH}
fi

# Set up Python virtual environment
print_status "Setting up Python virtual environment..."
apt-get update
apt-get install -y python3-venv python3-dev build-essential libpq-dev git

# Create and activate virtual environment
python3 -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r ${REQUIREMENTS_FILE}
pip install gunicorn

# Create Gunicorn configuration
print_status "Creating Gunicorn configuration..."
cat > ${GUNICORN_CONFIG} << EOL
import multiprocessing
import os

# Server socket
bind = "unix:${SOCKET_DIR}/${APP_NAME}.sock"
# Alternative: bind = "0.0.0.0:8090"  # Uncomment to use port 8090 instead of socket
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '${LOG_DIR}/access.log'
errorlog = '${LOG_DIR}/error.log'
loglevel = 'info'

# Process naming
proc_name = '${APP_NAME}'

# Server mechanics
daemon = False
pidfile = '${SOCKET_DIR}/${APP_NAME}.pid'
umask = 0
user = '${APP_USER}'
group = '${APP_GROUP}'
tmp_upload_dir = None
EOL

# Create systemd service file
print_status "Creating systemd service file..."
cat > ${SERVICE_FILE} << EOL
[Unit]
Description=Gunicorn instance to serve ${APP_NAME}
After=network.target

[Service]
User=${APP_USER}
Group=${APP_GROUP}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/gunicorn --config ${GUNICORN_CONFIG} main:app

[Install]
WantedBy=multi-user.target
EOL

# Set up database
print_status "Setting up database..."
if command -v mysql &> /dev/null; then
    # MySQL setup for CloudPanel
    print_status "Configuring MySQL for CloudPanel..."
    DB_NAME="cp_${APP_NAME}_db"
    DB_USER="cp_${APP_NAME}_user"
    
    # Prompt for database password
    read -s -p "Enter database password: " DB_PASSWORD
    echo
    
    # Update database configuration - replace healthyrizz.db with MySQL
    sed -i "s|SQLALCHEMY_DATABASE_URI = 'sqlite:///healthyrizz.db'|SQLALCHEMY_DATABASE_URI = 'mysql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}'|" ${APP_DIR}/config.py
    sed -i "s|SQLALCHEMY_DATABASE_URI = 'sqlite:///healthyrizz.db'|SQLALCHEMY_DATABASE_URI = 'mysql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}'|" ${APP_DIR}/config.py
else
    print_warning "MySQL not found. Using SQLite database."
fi

# Create .env file for environment variables
print_status "Creating environment configuration..."
cat > "${APP_DIR}/.env" << EOL
# Database Configuration
DATABASE_URL=mysql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}
SQLALCHEMY_DATABASE_URI=mysql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}

# Application Settings
FLASK_APP=main.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)

# Domain Configuration
DOMAIN_NAME=www.healthyrizz.in
BASE_URL=https://www.healthyrizz.in

# CloudPanel Settings
CLOUDPANEL_SITE_ROOT=${APP_DIR}
CLOUDPANEL_DOMAIN=www.healthyrizz.in
PORT=8090
EOL

chmod 600 "${APP_DIR}/.env"

# Set permissions
print_status "Setting permissions..."
chown -R ${APP_USER}:${APP_GROUP} ${APP_DIR}
chown -R ${APP_USER}:${APP_GROUP} ${LOG_DIR}
chown -R ${APP_USER}:${APP_GROUP} ${SOCKET_DIR}
chmod -R 755 ${APP_DIR}
chmod -R 755 ${LOG_DIR}
chmod -R 755 ${SOCKET_DIR}

# Initialize database
print_status "Initializing database..."
cd ${APP_DIR}
source ${VENV_DIR}/bin/activate
flask db upgrade

# Start and enable service
print_status "Starting service..."
systemctl daemon-reload
systemctl enable ${APP_NAME}
systemctl start ${APP_NAME}

# Check service status
print_status "Checking service status..."
systemctl status ${APP_NAME}

print_status "Deployment completed successfully!"
print_status "Application is running at: http://www.healthyrizz.in"
print_status "Logs can be found in: ${LOG_DIR}"
print_status "Socket file is located at: ${SOCKET_DIR}/${APP_NAME}.sock"

# Display CloudPanel-specific instructions
print_status "CloudPanel Instructions for healthyrizz.in:"
print_status "1. Log in to your CloudPanel dashboard"
print_status "2. Go to Websites > healthyrizz"
print_status "3. Configure your domain settings for www.healthyrizz.in"
print_status "4. Set up SSL certificates for healthyrizz.in"
print_status "5. Configure PHP settings if required"
print_status "6. Update DNS records to point to your server IP"
print_status ""
print_status "Next steps:"
print_status "- Configure your domain DNS to point to this server"
print_status "- Set up SSL certificate in CloudPanel"
print_status "- Test the application at https://www.healthyrizz.in" 