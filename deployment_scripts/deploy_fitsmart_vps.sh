#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
APP_DIR="/home/healthyrizz/htdocs/www.healthyrizz.ca"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="/home/healthyrizz/logs/www.healthyrizz.ca"
DB_NAME="healthyrizz"
DB_USER="healthyrizz"
DB_HOST="localhost"
DB_PORT="5432"
APP_PORT="8000"
ERROR_LOG="$LOG_DIR/deployment_errors.log"

# Function to print section headers
section() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

# Function to print success messages
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
error() {
    echo -e "${RED}✗ $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$ERROR_LOG"
    exit 1
}

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        success "$1"
    else
        error "$2"
    fi
}

# Function to install system packages
install_system_packages() {
    section "Installing System Packages"
    
    # Update package list
    apt-get update 2>> "$ERROR_LOG"
    check_status "Package list updated" "Failed to update package list"
    
    # Install required packages
    apt-get install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx 2>> "$ERROR_LOG"
    check_status "System packages installed" "Failed to install system packages"
    
    # Install additional Python packages
    pip3 install --upgrade pip setuptools wheel 2>> "$ERROR_LOG"
    check_status "Python packages upgraded" "Failed to upgrade Python packages"
}

# Function to check prerequisites
check_prerequisites() {
    section "Checking Prerequisites"
    
    # Install system packages if needed
    if ! command -v pip3 &> /dev/null; then
        echo "pip3 not found. Installing required packages..."
        install_system_packages
    fi
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 is not installed"
    fi
    
    # Check PostgreSQL
    if ! command -v psql &> /dev/null; then
        error "PostgreSQL is not installed"
    fi
    
    # Check if PostgreSQL service is running
    if ! systemctl is-active --quiet postgresql; then
        error "PostgreSQL service is not running"
    fi
    
    # Check Redis
    if ! command -v redis-cli &> /dev/null; then
        error "Redis is not installed"
    fi
    
    # Configure Redis first
    configure_redis
    
    success "All prerequisites are satisfied"
}

# Function to create Python virtual environment
setup_python_env() {
    section "Setting up Python environment"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR" 2>> "$ERROR_LOG"
        check_status "Virtual environment created" "Failed to create virtual environment"
    fi
    
    # Activate virtual environment and install dependencies
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip 2>> "$ERROR_LOG"
    check_status "Pip upgraded" "Failed to upgrade pip"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        error "requirements.txt not found"
    fi
    
    pip install -r requirements.txt 2>> "$ERROR_LOG"
    check_status "Dependencies installed" "Failed to install dependencies"
}

# Function to configure environment variables
configure_env() {
    section "Configuring environment variables"
    
    # Check if openssl is available
    if ! command -v openssl &> /dev/null; then
        error "openssl is not installed"
    fi
    
    # Generate secure random keys
    SECRET_KEY=$(openssl rand -hex 32)
    SESSION_SECRET=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    
    # Create .env file
    if [ -f "$APP_DIR/.env" ]; then
        mv "$APP_DIR/.env" "$APP_DIR/.env.backup"
        echo "Backed up existing .env file to .env.backup"
    fi
    
    cat > "$APP_DIR/.env" << EOL
# Database Configuration
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}

# Flask Configuration
FLASK_APP=main.py
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}
SESSION_SECRET=${SESSION_SECRET}
JWT_SECRET_KEY=${JWT_SECRET}

# Admin Configuration
ADMIN_EMAIL=admin@healthyrizz.ca
ADMIN_PASSWORD=admin123

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Stripe Configuration
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=your-aws-region
AWS_BUCKET_NAME=your-bucket-name

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/0
RATELIMIT_STRATEGY=fixed-window
RATELIMIT_DEFAULT=200 per day
RATELIMIT_STORAGE_OPTIONS={"socket_timeout": 5}

# Security Configuration
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
PERMANENT_SESSION_LIFETIME=3600

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=${LOG_DIR}/app.log
EOL

    # Set proper permissions
    chmod 600 "$APP_DIR/.env"
    check_status "Environment variables configured" "Failed to configure environment variables"
}

# Function to setup database
setup_database() {
    section "Setting up database"
    
    # Check if PostgreSQL is accessible
    if ! sudo -u postgres psql -c "\l" &> /dev/null; then
        error "Cannot connect to PostgreSQL"
    fi
    
    # Create database if it doesn't exist
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>> "$ERROR_LOG" || true
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>> "$ERROR_LOG" || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>> "$ERROR_LOG"
    
    # Check if database was created successfully
    if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        error "Failed to create database"
    fi
    
    # Run database migrations
    source "$VENV_DIR/bin/activate"
    
    # Set environment variables for Flask
    export FLASK_APP=main.py
    export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    
    # Check if migrations directory exists
    if [ ! -d "migrations" ]; then
        echo "Initializing migrations..."
        # Create a temporary config file for migrations
        cat > "$APP_DIR/migrations_config.py" << EOL
SQLALCHEMY_DATABASE_URI = "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
EOL
        export FLASK_APP_CONFIG="$APP_DIR/migrations_config.py"
        flask db init 2>> "$ERROR_LOG"
        check_status "Migrations initialized" "Failed to initialize migrations"
        
        # Update alembic.ini to use PostgreSQL
        sed -i "s|sqlalchemy.url = driver://user:pass@localhost/dbname|sqlalchemy.url = postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}|" "$APP_DIR/migrations/alembic.ini"
        
        # Update env.py to use the correct database URL
        cat > "$APP_DIR/migrations/env.py" << EOL
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from flask import current_app

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except TypeError:
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine

def get_metadata():
    if hasattr(current_app.extensions['migrate'].db, 'metadatas'):
        return current_app.extensions['migrate'].db.metadatas[None]
    return current_app.extensions['migrate'].db.metadata

def run_migrations_offline() -> None:
    url = get_engine().url.render_as_string(hide_password=False)
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                print('No changes in schema detected.')

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            process_revision_directives=process_revision_directives,
            **current_app.extensions['migrate'].configure_args
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOL
    fi
    
    # Create initial migration if none exists
    if [ ! -d "migrations/versions" ] || [ -z "$(ls -A migrations/versions)" ]; then
        echo "Creating initial migration..."
        flask db migrate -m "Initial migration" 2>> "$ERROR_LOG"
        check_status "Initial migration created" "Failed to create initial migration"
    fi
    
    # Run migrations with detailed error output
    echo "Running database migrations..."
    flask db upgrade 2>&1 | tee -a "$ERROR_LOG"
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        error "Failed to run database migrations. Check $ERROR_LOG for details."
    fi
    
    # Verify database tables
    echo "Verifying database tables..."
    if ! python3 -c "
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import inspect, text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    try:
        # First check if we can connect to the database
        db.session.execute(text('SELECT 1'))
        
        # Then get the list of tables
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print('Warning: No tables found in database')
            sys.exit(1)
            
        print(f'Database tables verified successfully. Found tables: {tables}')
        
        # Check if alembic_version table exists
        if 'alembic_version' not in tables:
            print('Warning: alembic_version table not found')
            sys.exit(1)
            
    except Exception as e:
        print(f'Error verifying database tables: {str(e)}')
        sys.exit(1)
" 2>> "$ERROR_LOG"; then
        error "Failed to verify database tables"
    fi
    
    # Clean up temporary config file
    rm -f "$APP_DIR/migrations_config.py"
    
    check_status "Database setup completed" "Failed to setup database"
}

# Function to configure Gunicorn
configure_gunicorn() {
    section "Configuring Gunicorn"
    
    # Check if Gunicorn is installed
    if ! pip show gunicorn &> /dev/null; then
        pip install gunicorn 2>> "$ERROR_LOG"
        check_status "Gunicorn installed" "Failed to install Gunicorn"
    fi
    
    # Create Gunicorn configuration
    cat > "$APP_DIR/gunicorn_config.py" << EOL
bind = "0.0.0.0:${APP_PORT}"
workers = 3
timeout = 120
accesslog = "${LOG_DIR}/gunicorn-access.log"
errorlog = "${LOG_DIR}/gunicorn-error.log"
capture_output = True
loglevel = "info"
EOL

    # Create systemd service file
    sudo tee /etc/systemd/system/gunicorn.service << EOL
[Unit]
Description=Gunicorn instance to serve HealthyRizz
After=network.target

[Service]
User=healthyrizz
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/gunicorn --config gunicorn_config.py main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable gunicorn
    sudo systemctl start gunicorn
    
    # Check if service started successfully
    sleep 5
    if ! systemctl is-active --quiet gunicorn; then
        error "Failed to start Gunicorn service"
    fi
    
    check_status "Gunicorn configured and started" "Failed to configure Gunicorn"
}

# Function to setup logging
setup_logging() {
    section "Setting up logging"
    
    # Create log directory
    sudo mkdir -p "$LOG_DIR"
    sudo chown -R healthyrizz:www-data "$LOG_DIR"
    sudo chmod -R 755 "$LOG_DIR"
    
    # Create error log file
    touch "$ERROR_LOG"
    sudo chown healthyrizz:www-data "$ERROR_LOG"
    sudo chmod 644 "$ERROR_LOG"
    
    check_status "Logging setup completed" "Failed to setup logging"
}

# Function to check port availability
check_port() {
    if netstat -tuln | grep -q ":$APP_PORT "; then
        error "Port $APP_PORT is already in use"
    fi
}

# Function to configure Redis
configure_redis() {
    section "Configuring Redis"
    
    echo "Configuring Redis server..."
    
    # Backup existing Redis config
    if [ -f /etc/redis/redis.conf ]; then
        echo "Backing up existing Redis configuration..."
        sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup
    fi
    
    # Create Redis configuration directory if it doesn't exist
    echo "Creating Redis configuration directory..."
    sudo mkdir -p /etc/redis
    
    # Update Redis configuration
    echo "Writing Redis configuration..."
    sudo tee /etc/redis/redis.conf > /dev/null << EOL
bind 127.0.0.1
port 6379
daemonize yes
supervised systemd
pidfile /var/run/redis/redis-server.pid
loglevel notice
logfile /var/log/redis/redis-server.log
databases 16
maxmemory 256mb
maxmemory-policy allkeys-lru
dir /var/lib/redis
dbfilename dump.rdb
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
EOL
    
    # Create necessary directories and set permissions
    echo "Setting up Redis directories..."
    sudo mkdir -p /var/log/redis /var/lib/redis /var/run/redis
    sudo chown -R redis:redis /var/log/redis /var/lib/redis /var/run/redis
    sudo chmod 755 /var/log/redis /var/lib/redis /var/run/redis
    
    # Force stop Redis services
    echo "Stopping Redis services..."
    sudo pkill -f redis-server || true
    sudo systemctl stop redis-server 2>/dev/null || true
    sudo systemctl stop redis 2>/dev/null || true
    sleep 2
    
    # Remove any existing PID files
    sudo rm -f /var/run/redis/redis-server.pid
    
    # Start Redis service
    echo "Starting Redis server..."
    if ! sudo systemctl start redis-server; then
        echo "Failed to start redis-server, trying redis service..."
        if ! sudo systemctl start redis; then
            echo "Failed to start Redis service. Checking logs..."
            sudo journalctl -u redis-server --no-pager -n 50
            error "Failed to start Redis service"
        fi
    fi
    
    # Wait for Redis to be ready with timeout
    echo "Waiting for Redis to be ready..."
    for i in {1..10}; do
        if redis-cli ping &> /dev/null; then
            echo "Redis is ready"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "Redis failed to start within timeout period. Checking logs..."
            sudo journalctl -u redis-server --no-pager -n 50
            error "Redis failed to start within timeout period"
        fi
        echo "Waiting for Redis to be ready... ($i/10)"
        sleep 2
    done
    
    # Verify Redis is running and accessible
    if ! redis-cli ping &> /dev/null; then
        echo "Redis is not responding. Checking logs..."
        sudo journalctl -u redis-server --no-pager -n 50
        error "Redis is not responding after configuration"
    fi
    
    # Enable Redis to start on boot
    echo "Enabling Redis to start on boot..."
    sudo systemctl enable redis-server 2>/dev/null || sudo systemctl enable redis 2>/dev/null
    
    echo "Redis configuration completed successfully"
    check_status "Redis configured and running" "Failed to configure Redis"
}

# Main function
main() {
    section "Starting HealthyRizz VPS Deployment"
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        error "Please run as root"
    fi
    
    # Create necessary directories
    sudo mkdir -p "$APP_DIR"
    sudo chown -R healthyrizz:www-data "$APP_DIR"
    
    # Setup logging first
    setup_logging
    
    # Check prerequisites (this will now install packages if needed)
    check_prerequisites
    
    # Check port availability
    check_port
    
    # Prompt for database password
    read -sp "Enter database password: " DB_PASSWORD
    echo
    
    # Run setup functions
    setup_python_env
    configure_env
    setup_database
    configure_gunicorn
    
    section "Deployment Complete"
    echo "HealthyRizz has been deployed successfully!"
    echo "The application is running on port ${APP_PORT}"
    echo "Please update the following in your .env file:"
    echo "1. Email credentials"
    echo "2. Stripe keys"
    echo "3. AWS credentials"
    echo "4. Redis URL"
    echo
    echo "You can check the application status with:"
    echo "sudo systemctl status gunicorn"
    echo
    echo "View logs with:"
    echo "tail -f ${LOG_DIR}/gunicorn-access.log"
    echo "tail -f ${LOG_DIR}/gunicorn-error.log"
    echo "tail -f ${ERROR_LOG}"
}

# Run main function
main 
