#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
print_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$ERROR_LOG"
}

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        print_success "$1"
    else
        print_error "$2"
        exit 1
    fi
}

# Function to install system packages
install_system_packages() {
    print_header "Installing System Packages"
    
    # Update package list
    apt-get update
    check_status "Package list updated" "Failed to update package list"
    
    # Install required packages including python3-full
    apt-get install -y python3-full python3-pip python3-venv postgresql postgresql-contrib redis-server nginx supervisor
    check_status "System packages installed" "Failed to install system packages"
    
    # Clean up any unnecessary packages
    apt-get autoremove -y
    check_status "System cleanup completed" "Failed to clean up system packages"
}

# Function to set up Python environment
setup_python_env() {
    print_header "Setting up Python Environment"
    
    # Remove existing virtual environment if it exists
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
        print_success "Removed existing virtual environment"
    fi
    
    # Create virtual environment
    python3 -m venv "$VENV_DIR"
    check_status "Virtual environment created" "Failed to create virtual environment"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    check_status "Virtual environment activated" "Failed to activate virtual environment"
    
    # Upgrade pip in virtual environment
    "$VENV_DIR/bin/pip" install --upgrade pip
    check_status "Pip upgraded in virtual environment" "Failed to upgrade pip"
    
    # Install required packages using the virtual environment's pip
    "$VENV_DIR/bin/pip" install gunicorn flask flask-sqlalchemy flask-migrate flask-login flask-wtf email-validator psycopg2-binary redis stripe boto3 python-dotenv flask-limiter limits gevent flask-mail twilio
    check_status "Python packages installed" "Failed to install Python packages"
    
    # Verify critical packages
    local required_packages=(
        "flask-login"
        "flask-wtf"
        "flask-limiter"
        "flask-sqlalchemy"
        "flask-migrate"
        "flask-mail"
        "twilio"
    )
    
    for package in "${required_packages[@]}"; do
        if ! "$VENV_DIR/bin/pip" show "$package" > /dev/null; then
            print_error "$package not found in virtual environment"
            exit 1
        fi
    done
    
    print_success "Python environment setup completed"
}

# Function to configure environment variables
configure_env() {
    print_header "Configuring Environment Variables"
    
    # Generate secure random keys
    SECRET_KEY=$(openssl rand -hex 64)
    SESSION_SECRET=$(openssl rand -hex 64)
    JWT_SECRET=$(openssl rand -hex 64)
    CSRF_SECRET=$(openssl rand -hex 64)
    API_SECRET=$(openssl rand -hex 64)
    
    # Create .env file
    cat > "$APP_DIR/.env" << EOL
# Database Configuration
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
DATABASE_TEST_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/${DB_NAME}_test

# Application Configuration
SECRET_KEY=$SECRET_KEY
SESSION_SECRET=$SESSION_SECRET
JWT_SECRET=$JWT_SECRET
CSRF_SECRET=$CSRF_SECRET
API_SECRET=$API_SECRET
FLASK_APP=main.py
FLASK_ENV=production
FLASK_DEBUG=0

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Stripe Configuration
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=your-aws-region
S3_BUCKET=your-s3-bucket

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
RATELIMIT_STRATEGY=fixed-window
RATELIMIT_DEFAULT=200 per day
RATELIMIT_HEADERS_ENABLED=true
RATELIMIT_STORAGE_OPTIONS={"socket_timeout": 5}
EOL
    
    check_status "Environment variables configured" "Failed to configure environment variables"
}

# Function to set up database
setup_database() {
    print_header "Setting up Database"
    
    # Check if PostgreSQL is running
    if ! systemctl is-active --quiet postgresql; then
        systemctl start postgresql
        check_status "PostgreSQL started" "Failed to start PostgreSQL"
    fi
    
    # Drop existing database and user if they exist
    su - postgres -c "psql -c \"DROP DATABASE IF EXISTS $DB_NAME;\""
    su - postgres -c "psql -c \"DROP USER IF EXISTS $DB_USER;\""
    
    # Create database and user
    su - postgres -c "psql -c \"CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';\""
    su - postgres -c "psql -c \"CREATE DATABASE $DB_NAME OWNER $DB_USER;\""
    su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;\""
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Change to application directory
    cd "$APP_DIR"
    
    # Initialize database migrations
    export FLASK_APP=main.py
    export FLASK_ENV=production
    export DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    
    # Remove existing migrations directory if it exists
    if [ -d "migrations" ]; then
        rm -rf migrations
        print_success "Removed existing migrations directory"
    fi
    
    # Initialize migrations
    "$VENV_DIR/bin/flask" db init
    check_status "Migrations initialized" "Failed to initialize migrations"
    
    # Update alembic.ini to use PostgreSQL
    sed -i "s|sqlalchemy.url = driver://user:pass@localhost/dbname|sqlalchemy.url = postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME|" "$APP_DIR/migrations/alembic.ini"
    
    # Update env.py to use PostgreSQL
    cat > "$APP_DIR/migrations/env.py" << EOL
from logging.config import fileConfig
import os
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Load environment variables
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with environment variable
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from models import db
target_metadata = db.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Handle the configuration up here
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv('DATABASE_URL')
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOL
    
    # Create initial migration
    "$VENV_DIR/bin/flask" db migrate -m "Initial migration"
    check_status "Initial migration created" "Failed to create initial migration"
    
    # Run database migrations
    "$VENV_DIR/bin/flask" db upgrade
    check_status "Database migrations applied" "Failed to apply database migrations"
    
    print_success "Database setup completed"
}

# Function to configure Gunicorn
configure_gunicorn() {
    print_header "Configuring Gunicorn"

    # Create log directory if it doesn't exist
    mkdir -p "$LOG_DIR"
    chown -R healthyrizz:healthyrizz "$LOG_DIR"

    # Create Gunicorn configuration file
    cat > "$APP_DIR/gunicorn_config.py" << EOL
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:$APP_PORT"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
errorlog = "$LOG_DIR/gunicorn_error.log"
accesslog = "$LOG_DIR/gunicorn_access.log"
loglevel = "debug"  # Changed to debug for more detailed logs
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "healthyrizz"

# Server mechanics
daemon = False
pidfile = "$LOG_DIR/gunicorn.pid"
umask = 0
user = "healthyrizz"
group = "healthyrizz"
tmp_upload_dir = None

# Server hooks
def on_starting(server):
    pass

def on_reload(server):
    pass

def on_exit(server):
    pass
EOL
    
    # Create systemd service file
    cat > /etc/systemd/system/healthyrizz.service << EOL
[Unit]
Description=HealthyRizz Gunicorn Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=healthyrizz
Group=healthyrizz
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="FLASK_APP=main.py"
Environment="FLASK_ENV=production"
Environment="DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
Environment="RATELIMIT_STORAGE_URL=redis://localhost:6379/1"
Environment="RATELIMIT_STRATEGY=fixed-window"
Environment="RATELIMIT_DEFAULT=200 per day"
Environment="RATELIMIT_HEADERS_ENABLED=true"
Environment="RATELIMIT_STORAGE_OPTIONS={\"socket_timeout\": 5}"
Environment="PYTHONPATH=$APP_DIR"
Environment="PYTHONUNBUFFERED=1"
Environment="GUNICORN_CMD_ARGS=--log-level debug"
ExecStart=$VENV_DIR/bin/gunicorn -c gunicorn_config.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
ExecStop=/bin/kill -s TERM \$MAINPID
Restart=always
RestartSec=5
StartLimitInterval=0
StandardOutput=append:$LOG_DIR/gunicorn.log
StandardError=append:$LOG_DIR/gunicorn_error.log

[Install]
WantedBy=multi-user.target
EOL

    # Set proper permissions
    chown -R healthyrizz:healthyrizz "$APP_DIR"
    chmod -R 755 "$APP_DIR"
    chmod 644 "$APP_DIR/gunicorn_config.py"
    chmod 644 /etc/systemd/system/healthyrizz.service

    # Create a temporary test file to verify Redis connection
    cat > "$APP_DIR/test_redis.py" << EOL
import redis
import sys

try:
    r = redis.Redis(host='localhost', port=6379, db=1)
    r.ping()
    print("Redis connection successful")
    sys.exit(0)
except Exception as e:
    print(f"Redis connection failed: {str(e)}")
    sys.exit(1)
EOL

    # Test Redis connection
    print_header "Testing Redis Connection"
    if "$VENV_DIR/bin/python" "$APP_DIR/test_redis.py"; then
        print_success "Redis connection verified"
    else
        print_error "Redis connection failed"
        exit 1
    fi

    # Remove test file
    rm "$APP_DIR/test_redis.py"

    # Create a test file to verify the application
    cat > "$APP_DIR/test_app.py" << EOL
from main import app
import sys

try:
    with app.app_context():
        print("Application context created successfully")
        sys.exit(0)
except Exception as e:
    print(f"Application context creation failed: {str(e)}")
    sys.exit(1)
EOL

    # Test application
    print_header "Testing Application"
    if "$VENV_DIR/bin/python" "$APP_DIR/test_app.py"; then
        print_success "Application test successful"
    else
        print_error "Application test failed"
        exit 1
    fi

    # Remove test file
    rm "$APP_DIR/test_app.py"

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable healthyrizz
    
    # Start the service and check its status
    print_header "Starting Gunicorn Service"
    systemctl start healthyrizz
    sleep 5  # Give the service time to start
    
    if systemctl is-active --quiet healthyrizz; then
        print_success "Gunicorn service started successfully"
        
        # Check service logs for any errors
        if grep -i "error" "$LOG_DIR/gunicorn_error.log" > /dev/null; then
            print_error "Found errors in Gunicorn logs"
            tail -n 50 "$LOG_DIR/gunicorn_error.log"
            exit 1
        fi
        
        # Check if the service is responding
        if curl -s http://127.0.0.1:$APP_PORT/health > /dev/null; then
            print_success "Service is responding to requests"
        else
            print_error "Service is not responding to requests"
            journalctl -u healthyrizz -n 50 --no-pager
            exit 1
        fi
    else
        print_error "Failed to start Gunicorn service"
        journalctl -u healthyrizz -n 50 --no-pager
        exit 1
    fi
}

# Function to set up logging
setup_logging() {
    print_header "Setting up Logging"
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    chown -R healthyrizz:healthyrizz "$LOG_DIR"
    
    # Create error log file
    touch "$ERROR_LOG"
    chown healthyrizz:healthyrizz "$ERROR_LOG"
    
    check_status "Logging setup completed" "Failed to set up logging"
}

# Function to set up development environment
setup_dev_env() {
    print_header "Setting up Development Environment"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python -m venv venv
        check_status "Virtual environment created" "Failed to create virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install required packages
    pip install -r requirements.txt
    check_status "Development packages installed" "Failed to install development packages"
    
    # Create .env file for development
    cat > .env << EOL
# Development Configuration
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
DATABASE_TEST_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/${DB_NAME}_test

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
RATELIMIT_STRATEGY=fixed-window
RATELIMIT_DEFAULT=200 per day
RATELIMIT_HEADERS_ENABLED=true
RATELIMIT_STORAGE_OPTIONS={"socket_timeout": 5}

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Stripe Configuration
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=your-aws-region
S3_BUCKET=your-s3-bucket
EOL
    
    print_success "Development environment setup completed"
    echo -e "\n${YELLOW}To start the development server:${NC}"
    echo "1. Activate the virtual environment:"
    echo "   - Windows: .\\venv\\Scripts\\activate"
    echo "   - Linux/Mac: source venv/bin/activate"
    echo "2. Run the application:"
    echo "   python main.py"
}

# Function to create requirements.txt
create_requirements() {
    print_header "Creating requirements.txt"
    
    cat > requirements.txt << EOL
flask==3.0.2
flask-sqlalchemy==3.1.1
flask-migrate==4.0.5
flask-login==0.6.3
flask-wtf==1.2.1
flask-mail==0.9.1
flask-limiter==3.5.0
email-validator==2.1.0.post1
psycopg2-binary==2.9.9
redis==5.0.1
stripe==7.11.0
boto3==1.34.34
python-dotenv==1.0.1
twilio==8.12.0
gunicorn==21.2.0
gevent==24.2.1
limits==3.7.0
EOL
    
    print_success "requirements.txt created"
}

# Main function
main() {
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root"
        exit 1
    fi
    
    # Create error log file
    mkdir -p "$LOG_DIR"
    touch "$ERROR_LOG"
    
    # Generate secure random database password
    DB_PASSWORD=$(openssl rand -base64 32)
    
    # Create requirements.txt
    create_requirements
    
    # Run setup functions
    install_system_packages
    setup_python_env
    configure_env
    setup_database
    configure_gunicorn
    setup_logging
    setup_dev_env
    
    print_success "Deployment completed successfully!"
    echo -e "\n${YELLOW}Important:${NC}"
    echo "1. Update email credentials in .env file"
    echo "2. Add Stripe keys in .env file"
    echo "3. Configure AWS credentials if needed"
    echo -e "\nDatabase password: $DB_PASSWORD"
    echo "Please save this password securely!"
}

# Run main function
main
