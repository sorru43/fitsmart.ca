#!/bin/bash
#
# PostgreSQL Database Setup Script for CloudPanel
# ----------------------------------------------
# This script creates a PostgreSQL database and user for HealthyRizz
# with admin credentials, specifically designed for CloudPanel environments
# where the postgres user might not be available via sudo.
#
# Run as root or with sudo.
#

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

# Check for PostgreSQL client
if ! command -v psql &> /dev/null; then
    log_error "PostgreSQL client (psql) not found. Installing..."
    apt-get update
    apt-get install -y postgresql-client
    
    if ! command -v psql &> /dev/null; then
        log_error "Failed to install PostgreSQL client. Please install it manually."
        exit 1
    else
        log_success "PostgreSQL client installed successfully."
    fi
fi

# Check if PostgreSQL server is installed
if ! systemctl is-active --quiet postgresql; then
    log_warning "PostgreSQL server is not running. Checking if it's installed..."
    
    if ! dpkg -l | grep -q "postgresql.*server"; then
        log_warning "PostgreSQL server not found. Installing..."
        apt-get update
        apt-get install -y postgresql postgresql-contrib
        
        # Start and enable PostgreSQL
        systemctl start postgresql
        systemctl enable postgresql
        log_success "PostgreSQL server installed and started."
    else
        log_warning "PostgreSQL server is installed but not running. Starting..."
        systemctl start postgresql
        log_success "PostgreSQL server started."
    fi
fi

# Database configuration variables
echo -e "${BOLD}PostgreSQL Database Setup${RESET}"
echo "----------------------------------------"
echo

read -p "Database name (default: cp_healthyrizz_db): " DB_NAME
DB_NAME=${DB_NAME:-cp_healthyrizz_db}

read -p "Database user (default: cp_healthyrizz_user): " DB_USER
DB_USER=${DB_USER:-cp_healthyrizz_user}

read -s -p "Database password: " DB_PASSWORD
echo
if [ -z "$DB_PASSWORD" ]; then
    log_error "Password cannot be empty!"
    exit 1
fi

read -p "Database host (default: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Database port (default: 5432): " DB_PORT
DB_PORT=${DB_PORT:-5432}

# Admin credentials
echo
echo -e "${BOLD}PostgreSQL Admin Credentials${RESET}"
echo "----------------------------------------"
echo "These are needed to create the database and user."
echo

read -p "PostgreSQL admin username (default: postgres): " PGADMIN_USER
PGADMIN_USER=${PGADMIN_USER:-postgres}

read -s -p "PostgreSQL admin password: " PGADMIN_PASSWORD
echo

# Check admin connection
echo "Testing admin connection to PostgreSQL..."
if PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h $DB_HOST -p $DB_PORT -c "SELECT 1" > /dev/null 2>&1; then
    log_success "Admin connection successful!"
else
    log_error "Could not connect to PostgreSQL with provided admin credentials."
    
    # Attempt postgres user connection
    if id -u postgres &> /dev/null; then
        log_warning "Trying connection as postgres system user..."
        if sudo -u postgres psql -c "SELECT 1" > /dev/null 2>&1; then
            log_success "Connection as postgres system user successful!"
            USE_POSTGRES_USER=true
        else
            log_error "Could not connect as postgres system user either."
            log_error "Please check your PostgreSQL installation and credentials."
            exit 1
        fi
    else
        log_error "Please check your PostgreSQL installation and credentials."
        exit 1
    fi
fi

# Create database and user
echo "Creating database and user..."

if [ "$USE_POSTGRES_USER" = true ]; then
    # Using postgres system user
    if sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
        log_warning "Database $DB_NAME already exists."
        read -p "Drop and recreate? (y/n): " RECREATE
        if [[ $RECREATE =~ ^[Yy]$ ]]; then
            sudo -u postgres psql -c "DROP DATABASE $DB_NAME;"
            log_info "Dropped existing database $DB_NAME"
        else
            log_info "Using existing database $DB_NAME"
        fi
    else
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
        log_success "Database $DB_NAME created."
    fi
    
    if sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        log_warning "User $DB_USER already exists."
        read -p "Drop and recreate? (y/n): " RECREATE
        if [[ $RECREATE =~ ^[Yy]$ ]]; then
            sudo -u postgres psql -c "DROP USER $DB_USER;"
            sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
            log_info "Recreated user $DB_USER"
        else
            sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
            log_info "Updated password for user $DB_USER"
        fi
    else
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        log_success "User $DB_USER created."
    fi
    
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    log_success "Granted privileges to $DB_USER on $DB_NAME"
else
    # Using admin credentials
    if PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h $DB_HOST -p $DB_PORT -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
        log_warning "Database $DB_NAME already exists."
        read -p "Drop and recreate? (y/n): " RECREATE
        if [[ $RECREATE =~ ^[Yy]$ ]]; then
            PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h $DB_HOST -p $DB_PORT -c "DROP DATABASE $DB_NAME;"
            log_info "Dropped existing database $DB_NAME"
        else
            log_info "Using existing database $DB_NAME"
        fi
    else
        PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h $DB_HOST -p $DB_PORT -c "CREATE DATABASE $DB_NAME;"
        log_success "Database $DB_NAME created."
    fi
    
    if PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h $DB_HOST -p $DB_PORT -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        log_warning "User $DB_USER already exists."
        read -p "Drop and recreate? (y/n): " RECREATE
        if [[ $RECREATE =~ ^[Yy]$ ]]; then
            PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h $DB_HOST -p $DB_PORT -c "DROP USER $DB_USER;"
            PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h $DB_HOST -p $DB_PORT -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
            log_info "Recreated user $DB_USER"
        else
            PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h $DB_HOST -p $DB_PORT -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
            log_info "Updated password for user $DB_USER"
        fi
    else
        PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h $DB_HOST -p $DB_PORT -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
        log_success "User $DB_USER created."
    fi
    
    PGPASSWORD=$PGADMIN_PASSWORD psql -U $PGADMIN_USER -h $DB_HOST -p $DB_PORT -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    log_success "Granted privileges to $DB_USER on $DB_NAME"
fi

# Create .env file template
cat > ".env.postgres.template" << EOF
# PostgreSQL Database Environment Variables
# Generated by setup_postgres_db.sh

# Database Connection
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
SQLALCHEMY_DATABASE_URI=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
PGDATABASE=$DB_NAME
PGUSER=$DB_USER
PGPASSWORD=$DB_PASSWORD
PGHOST=$DB_HOST
PGPORT=$DB_PORT
EOF

log_success "Created .env.postgres.template file with database connection variables."
log_info "You can copy these into your application's .env file."

# Verify connection
echo "Verifying database connection..."
if PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "SELECT 1" > /dev/null 2>&1; then
    log_success "Connection to database successful!"
    log_success "PostgreSQL database setup completed successfully!"
    
    echo
    echo -e "${BOLD}Database Connection Details:${RESET}"
    echo "----------------------------------------"
    echo "Database: $DB_NAME"
    echo "User: $DB_USER"
    echo "Password: [HIDDEN]"
    echo "Host: $DB_HOST"
    echo "Port: $DB_PORT"
    echo
    echo -e "${BOLD}Connection String:${RESET}"
    echo "postgresql://$DB_USER:[PASSWORD]@$DB_HOST:$DB_PORT/$DB_NAME"
    echo
    echo "You can now use these settings in your HealthyRizz application."
else
    log_error "Failed to connect to database with new credentials."
    log_warning "Please check your PostgreSQL configuration and try again."
fi
