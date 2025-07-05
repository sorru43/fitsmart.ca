#!/bin/bash

# Fix Dependencies Script for VPS Deployment
# This script resolves dependency conflicts and installs compatible versions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    error "Virtual environment is not activated. Please activate it first."
fi

log "Starting dependency fix for HealthyRizz VPS deployment..."

# Upgrade pip first
log "Upgrading pip..."
pip install --upgrade pip

# Install core dependencies first
log "Installing core dependencies..."
pip install Flask==3.0.2 Flask-SQLAlchemy==3.1.1 Flask-Login==0.6.3 Flask-WTF==1.2.1

# Install database dependencies
log "Installing database dependencies..."
pip install SQLAlchemy==2.0.27 psycopg2-binary==2.9.9 alembic==1.13.1 redis==5.0.1

# Install PDF generation with compatible versions
log "Installing PDF generation dependencies..."
pip install reportlab==4.1.0 PyPDF2==3.0.1 fpdf2==2.7.8

# Install email and notification dependencies
log "Installing email and notification dependencies..."
pip install sendgrid==6.11.0 twilio==8.12.0 email-validator==2.1.0

# Install security dependencies
log "Installing security dependencies..."
pip install bcrypt==4.1.2 PyJWT==2.8.0 cryptography==42.0.2 python-dotenv==1.0.1 itsdangerous==2.1.2

# Install utility dependencies
log "Installing utility dependencies..."
pip install python-dateutil==2.8.2 pytz==2024.1 requests==2.31.0 Pillow==10.2.0 Werkzeug==3.0.1

# Install production server dependencies
log "Installing production server dependencies..."
pip install gunicorn==21.2.0 gevent==24.2.1

# Install payment processing dependencies
log "Installing payment processing dependencies..."
pip install razorpay==1.4.1 stripe==7.11.0

# Install data processing dependencies
log "Installing data processing dependencies..."
pip install pandas==2.2.0

# Install monitoring dependencies
log "Installing monitoring dependencies..."
pip install sentry-sdk==1.40.4 python-json-logger==2.0.7

# Install caching and performance dependencies
log "Installing caching and performance dependencies..."
pip install cachetools==5.3.3 ujson==5.9.0

# Install production tools
log "Installing production tools..."
pip install supervisor==4.2.5

# Install remaining Flask extensions
log "Installing remaining Flask extensions..."
pip install Flask-Mail==0.9.1 Flask-Migrate==4.0.5 Flask-CORS==4.0.0 Flask-Admin==1.6.1 Flask-Limiter==3.5.0

# Verify installation
log "Verifying installation..."
python -c "import flask, sqlalchemy, fpdf2, pandas, gunicorn; print('✅ All core dependencies installed successfully')"

log "Dependency installation completed successfully!"
log "You can now proceed with the VPS deployment."

# Optional: Show installed packages
info "Installed packages:"
pip list | grep -E "(Flask|SQLAlchemy|fpdf|pandas|gunicorn)" 