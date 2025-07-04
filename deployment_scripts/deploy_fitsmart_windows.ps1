# healthyrizz Windows Deployment Script
# -----------------------------------
# This script automates the deployment of the healthyrizz application on Windows

# Configuration
$DomainName = "healthyrizz.ca"
$AppName = "healthyrizz"
$Environment = "production"
$DebugMode = "False"
$AppPort = 8000
$UseSSL = $true
$SSLEmail = "admin@healthyrizz.ca"

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Create .env file
$envContent = @"
# Domain Configuration
DOMAIN_NAME=$DomainName
SERVER_NAME=$DomainName

# Security
SECRET_KEY=$(New-Guid)
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_DOMAIN=$DomainName

# Database
DATABASE_URL=sqlite:///healthyrizz.db

# Environment
FLASK_ENV=$Environment
FLASK_APP=app.py
DEBUG=$DebugMode

# Mail Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=noreply@$DomainName
"@

Set-Content -Path ".env" -Value $envContent

# Initialize database
Write-Host "Initializing database..."
flask db upgrade

# Create admin user
Write-Host "Creating admin user..."
python -c "
from app import create_app
from database.models import User
from extensions import db

app = create_app()
with app.app_context():
    admin = User.create_user(
        email='admin@$DomainName',
        username='admin',
        password='admin123',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
"

# Start the application
Write-Host "Starting healthyrizz application..."
Write-Host "The application will be available at http://localhost:$AppPort"
Write-Host "Press Ctrl+C to stop the server"

# Run the Flask application
flask run --host=0.0.0.0 --port=$AppPort 