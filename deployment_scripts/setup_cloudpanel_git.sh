#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
APP_NAME="healthyrizz"
APP_DIR="/home/${APP_NAME}/htdocs/www.${APP_NAME}.ca"
GIT_REPO="https://github.com/yourusername/healthyrizz.git"  # Replace with your actual Git repository URL
GIT_BRANCH="main"  # Replace with your default branch
CLOUDPANEL_DB_PREFIX="cp_"

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

# Function to check CloudPanel installation
check_cloudpanel() {
    print_status "Checking CloudPanel installation..."
    if [ -d "/etc/cloudpanel" ] || [ -d "/opt/cloudpanel" ]; then
        print_status "CloudPanel detected"
        return 0
    else
        print_error "CloudPanel not found. Please install CloudPanel first."
        exit 1
    fi
}

# Function to install and configure Redis
setup_redis() {
    print_status "Setting up Redis..."
    
    # Install Redis if not present
    if ! command -v redis-server &> /dev/null; then
        print_status "Installing Redis..."
        apt-get update
        apt-get install -y redis-server
    fi
    
    # Configure Redis for Flask-Limiter
    cat > "/etc/redis/redis.conf.d/flask-limiter.conf" << EOL
maxmemory 256mb
maxmemory-policy allkeys-lru
appendonly yes
appendfilename "flask-limiter.aof"
EOL
    
    # Restart Redis to apply changes
    systemctl restart redis-server
    
    # Enable Redis to start on boot
    systemctl enable redis-server
}

# Function to set up Git repository
setup_git() {
    print_status "Setting up Git repository..."
    
    # Check if Git is installed
    if ! command -v git &> /dev/null; then
        print_status "Installing Git..."
        apt-get update
        apt-get install -y git
    fi
    
    # Configure Git
    git config --global user.name "HealthyRizz Deploy"
    git config --global user.email "deploy@healthyrizz.ca"
    
    # Initialize Git repository if it doesn't exist
    if [ ! -d "${APP_DIR}/.git" ]; then
        print_status "Initializing Git repository..."
        cd ${APP_DIR}
        git init
        git add .
        git commit -m "Initial commit"
        
        # Add remote if provided
        if [ ! -z "$GIT_REPO" ]; then
            git remote add origin ${GIT_REPO}
            git push -u origin ${GIT_BRANCH}
        fi
    else
        print_status "Git repository already exists"
    fi
}

# Function to set up CloudPanel website
setup_cloudpanel_website() {
    print_status "Setting up CloudPanel website..."
    
    # Create website directory if it doesn't exist
    mkdir -p ${APP_DIR}
    
    # Set proper permissions
    chown -R www-data:www-data ${APP_DIR}
    chmod -R 755 ${APP_DIR}
    
    # Create .htaccess file for PHP configuration
    cat > "${APP_DIR}/.htaccess" << EOL
# PHP Configuration
php_value upload_max_filesize 64M
php_value post_max_size 64M
php_value max_execution_time 300
php_value max_input_time 300

# Security Headers
Header set X-Content-Type-Options "nosniff"
Header set X-Frame-Options "SAMEORIGIN"
Header set X-XSS-Protection "1; mode=block"
Header set Referrer-Policy "strict-origin-when-cross-origin"

# Enable CORS
Header set Access-Control-Allow-Origin "*"
EOL
    
    # Create robots.txt
    cat > "${APP_DIR}/robots.txt" << EOL
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
EOL
}

# Function to set up database
setup_database() {
    print_status "Setting up database..."
    
    # Get database credentials from CloudPanel
    DB_NAME="${CLOUDPANEL_DB_PREFIX}${APP_NAME}_db"
    DB_USER="${CLOUDPANEL_DB_PREFIX}${APP_NAME}_user"
    
    # Prompt for database password
    read -s -p "Enter database password: " DB_PASSWORD
    echo
    
    # Create .env file
    cat > "${APP_DIR}/.env" << EOL
# Database Configuration
DATABASE_URL=mysql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}
SQLALCHEMY_DATABASE_URI=mysql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}

# Application Settings
FLASK_APP=main.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
FLASK_LIMITER_STORAGE_URI=redis://localhost:6379/1

# CloudPanel Settings
CLOUDPANEL_SITE_ROOT=${APP_DIR}
CLOUDPANEL_DOMAIN=www.${APP_NAME}.ca
PORT=8000
EOL
    
    chmod 600 "${APP_DIR}/.env"
}

# Function to create deployment script
create_deployment_script() {
    print_status "Creating deployment script..."
    
    cat > "${APP_DIR}/deploy.sh" << EOL
#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
APP_DIR="${APP_DIR}"
VENV_DIR="\${APP_DIR}/venv"
GIT_BRANCH="${GIT_BRANCH}"

# Function to print status messages
print_status() {
    echo -e "\${GREEN}[+] \$1\${NC}"
}

print_warning() {
    echo -e "\${YELLOW}[!] \$1\${NC}"
}

print_error() {
    echo -e "\${RED}[x] \$1\${NC}"
}

# Pull latest changes
print_status "Pulling latest changes..."
cd \${APP_DIR}
git fetch origin
git reset --hard origin/\${GIT_BRANCH}
git clean -fd

# Update Python dependencies
print_status "Updating Python dependencies..."
source \${VENV_DIR}/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
print_status "Running database migrations..."
flask db upgrade

# Restart services
print_status "Restarting services..."
systemctl restart redis-server
systemctl restart ${APP_NAME}

print_status "Deployment completed successfully!"
EOL
    
    chmod +x "${APP_DIR}/deploy.sh"
}

# Main execution
print_status "Starting CloudPanel and Git setup..."

# Check CloudPanel installation
check_cloudpanel

# Set up Redis
setup_redis

# Set up Git repository
setup_git

# Set up CloudPanel website
setup_cloudpanel_website

# Set up database
setup_database

# Create deployment script
create_deployment_script

print_status "Setup completed successfully!"
print_status "Next steps:"
print_status "1. Log in to CloudPanel dashboard"
print_status "2. Go to Websites > ${APP_NAME}"
print_status "3. Configure your domain settings"
print_status "4. Set up SSL certificates"
print_status "5. Configure PHP settings"
print_status ""
print_status "To deploy updates, use: ${APP_DIR}/deploy.sh" 
