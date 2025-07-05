# HealthyRizz Clean Deployment Script for CloudPanel
# This script creates a minimal deployment package with all import fixes

Write-Host "Creating clean deployment package for HealthyRizz..." -ForegroundColor Green

# Create deployment directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$deployDir = "healthyrizz_clean_deploy_$timestamp"
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null

# Copy essential files
Write-Host "Copying essential files..." -ForegroundColor Yellow

# Core application files
Copy-Item "app.py" $deployDir/
Copy-Item "main.py" $deployDir/
Copy-Item "config.py" $deployDir/
Copy-Item "extensions.py" $deployDir/
Copy-Item "models.py" $deployDir/
Copy-Item "commands.py" $deployDir/
Copy-Item "contact_forms.py" $deployDir/
Copy-Item "requirements.txt" $deployDir/

# Routes
New-Item -ItemType Directory -Path "$deployDir/routes" -Force | Out-Null
Copy-Item "routes/__init__.py" "$deployDir/routes/"
Copy-Item "routes/main_routes.py" "$deployDir/routes/"
Copy-Item "routes/admin_routes.py" "$deployDir/routes/"
Copy-Item "routes/user_routes.py" "$deployDir/routes/"
Copy-Item "routes/routes_api.py" "$deployDir/routes/"
Copy-Item "routes/routes_stripe.py" "$deployDir/routes/"
Copy-Item "routes/subscription_routes.py" "$deployDir/routes/"
Copy-Item "routes/routes_notifications.py" "$deployDir/routes/"

# Forms
New-Item -ItemType Directory -Path "$deployDir/forms" -Force | Out-Null
Copy-Item "forms/__init__.py" "$deployDir/forms/"
Copy-Item "forms/auth_forms.py" "$deployDir/forms/"
Copy-Item "forms/checkout_forms.py" "$deployDir/forms/"
Copy-Item "forms/trial_forms.py" "$deployDir/forms/"
Copy-Item "forms/video_forms.py" "$deployDir/forms/"

# Utils
New-Item -ItemType Directory -Path "$deployDir/utils" -Force | Out-Null
Copy-Item "utils/__init__.py" "$deployDir/utils/"
Copy-Item "utils/filters.py" "$deployDir/utils/"
Copy-Item "utils/email_utils.py" "$deployDir/utils/"
Copy-Item "utils/security_utils.py" "$deployDir/utils/"
Copy-Item "utils/validation_utils.py" "$deployDir/utils/"
Copy-Item "utils/token_utils.py" "$deployDir/utils/"
Copy-Item "utils/file_utils.py" "$deployDir/utils/"
Copy-Item "utils/crypto_utils.py" "$deployDir/utils/"
Copy-Item "utils/notification_utils.py" "$deployDir/utils/"
Copy-Item "utils/payment_utils.py" "$deployDir/utils/"
Copy-Item "utils/report_utils.py" "$deployDir/utils/"
Copy-Item "utils/sms_utils.py" "$deployDir/utils/"
Copy-Item "utils/stripe_utils.py" "$deployDir/utils/"
Copy-Item "utils/razorpay_utils.py" "$deployDir/utils/"

# Calculator utils
New-Item -ItemType Directory -Path "$deployDir/utils/calculator" -Force | Out-Null
Copy-Item "utils/calculator/__init__.py" "$deployDir/utils/calculator/"
Copy-Item "utils/calculator/lifestyle_calculator.py" "$deployDir/utils/calculator/"

# Templates
Copy-Item -Recurse "templates" $deployDir/

# Static files
Copy-Item -Recurse "static" $deployDir/

# Database
New-Item -ItemType Directory -Path "$deployDir/database" -Force | Out-Null
Copy-Item "database/__init__.py" "$deployDir/database/"
Copy-Item "database/db_config.py" "$deployDir/database/"
Copy-Item "database/init_db.py" "$deployDir/database/"
Copy-Item "database/reset_db.py" "$deployDir/database/"

# Migrations
Copy-Item -Recurse "migrations" $deployDir/

# PWA files
Copy-Item -Recurse "pwa" $deployDir/

# Config files
New-Item -ItemType Directory -Path "$deployDir/config" -Force | Out-Null
Copy-Item "config/requirements.txt" "$deployDir/config/"
Copy-Item "config/fitsmart_requirements.txt" "$deployDir/config/"

# Documentation
if (Test-Path "README.md") { Copy-Item "README.md" $deployDir/ }
if (Test-Path "robots.txt") { Copy-Item "robots.txt" $deployDir/ }
if (Test-Path "sitemap.xml") { Copy-Item "sitemap.xml" $deployDir/ }

# Create deployment script
$deployScript = @'
#!/bin/bash

# HealthyRizz Deployment Script for CloudPanel
# Domain: healthyrizz.in
# Port: 8090

echo "Starting HealthyRizz deployment..."

# Set variables
DOMAIN="healthyrizz.in"
PORT="8090"
APP_NAME="healthyrizz"
APP_DIR="/home/cloudpanel/htdocs/$DOMAIN"
VENV_DIR="$APP_DIR/venv"

# Create app directory if it doesn't exist
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install additional dependencies if needed
pip install flask-limiter flask-session

# Initialize database
echo "Initializing database..."
export FLASK_APP=main.py
export FLASK_ENV=production
flask init-db

# Create admin user
echo "Creating admin user..."
flask create-admin --username admin --email admin@healthyrizz.in --password admin123

# Seed sample data
echo "Seeding sample data..."
flask seed-data

# Set permissions
chmod +x deploy.sh
chmod 755 -R "$APP_DIR"

# Create systemd service file
sudo tee /etc/systemd/system/healthyrizz.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=HealthyRizz Flask Application
After=network.target

[Service]
Type=simple
User=cloudpanel
Group=cloudpanel
WorkingDirectory=/home/cloudpanel/htdocs/healthyrizz.in
Environment=PATH=/home/cloudpanel/htdocs/healthyrizz.in/venv/bin
Environment=FLASK_APP=main.py
Environment=FLASK_ENV=production
ExecStart=/home/cloudpanel/htdocs/healthyrizz.in/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8090 main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable healthyrizz
sudo systemctl start healthyrizz

# Check service status
sudo systemctl status healthyrizz

echo "Deployment completed!"
echo "Application should be running on http://$DOMAIN:$PORT"
echo "Admin panel: http://$DOMAIN:$PORT/admin"
echo "Admin credentials: admin@healthyrizz.in / admin123"
'@

$deployScript | Out-File -FilePath "$deployDir/deploy.sh" -Encoding UTF8

# Create zip file
Write-Host "Creating deployment package..." -ForegroundColor Yellow
Compress-Archive -Path $deployDir -DestinationPath "${deployDir}.zip" -Force

# Clean up
Remove-Item -Recurse -Force $deployDir

Write-Host "✅ Clean deployment package created: ${deployDir}.zip" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Deployment Instructions:" -ForegroundColor Cyan
Write-Host "1. Upload ${deployDir}.zip to your CloudPanel server"
Write-Host "2. Extract the zip file in /home/cloudpanel/htdocs/"
Write-Host "3. SSH into your server and navigate to the extracted directory"
Write-Host "4. Run: chmod +x deploy.sh; ./deploy.sh"
Write-Host "5. Configure CloudPanel to proxy to localhost:8090"
Write-Host ""
Write-Host "🔧 CloudPanel Configuration:" -ForegroundColor Cyan
Write-Host "- Domain: healthyrizz.in"
Write-Host "- Port: 8090"
Write-Host "- Proxy to: http://127.0.0.1:8090"
Write-Host ""
Write-Host "📝 Important Notes:" -ForegroundColor Yellow
Write-Host "- All import errors have been fixed"
Write-Host "- Missing models have been commented out"
Write-Host "- Coupon functionality is temporarily disabled"
Write-Host "- Newsletter functionality is simplified" 