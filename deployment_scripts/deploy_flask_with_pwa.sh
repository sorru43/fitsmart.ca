#!/bin/bash
# Integrated deployment script for Flask with PWA functionality

# VPS connection details (edit these)
VPS_USER="root"
VPS_HOST="your.vps.ip.address"
APP_DIR="/home/healthyrizz/htdocs/www.healthyrizz.ca"

echo "===== DEPLOYING HEALTHYRIZZ WITH PWA FUNCTIONALITY ====="

# Create required directories
echo "Creating directories if needed..."
ssh $VPS_USER@$VPS_HOST "mkdir -p $APP_DIR/static/js $APP_DIR/static/icons $APP_DIR/static/css $APP_DIR/templates"

# 1. Deploy core Flask application files
echo "Deploying core application files..."
scp -r *.py $VPS_USER@$VPS_HOST:$APP_DIR/
scp -r templates/*.html $VPS_USER@$VPS_HOST:$APP_DIR/templates/
scp -r static/css/* $VPS_USER@$VPS_HOST:$APP_DIR/static/css/
scp -r static/js/*.js $VPS_USER@$VPS_HOST:$APP_DIR/static/js/
scp -r static/favicon.ico $VPS_USER@$VPS_HOST:$APP_DIR/static/

# 2. Deploy PWA specific files
echo "Deploying PWA files..."
scp static/manifest.json $VPS_USER@$VPS_HOST:$APP_DIR/static/
scp static/offline.html $VPS_USER@$VPS_HOST:$APP_DIR/static/
scp static/js/service-worker.js $VPS_USER@$VPS_HOST:$APP_DIR/static/js/
scp static/js/register-sw.js $VPS_USER@$VPS_HOST:$APP_DIR/static/js/
scp -r static/icons/* $VPS_USER@$VPS_HOST:$APP_DIR/static/icons/

# 3. Make sure PWA routes are included in main.py
echo "Ensuring PWA routes are integrated..."
ssh $VPS_USER@$VPS_HOST "grep -q 'import routes_pwa' $APP_DIR/main.py || cat >> $APP_DIR/main.py << 'EOF'

# Import PWA routes
try:
    import routes_pwa
    print(\"✅ PWA routes imported successfully\")
except Exception as e:
    print(f\"❌ Error importing PWA routes: {str(e)}\")
EOF"

# 4. Ensure healthyrizz.service is properly configured
echo "Checking systemd service file..."
ssh $VPS_USER@$VPS_HOST "cat > /etc/systemd/system/healthyrizz.service << 'EOF'
[Unit]
Description=HealthyRizz Gunicorn Service
After=network.target

[Service]
User=healthyrizz
Group=healthyrizz
WorkingDirectory=/home/healthyrizz/htdocs/www.healthyrizz.ca
ExecStart=/home/healthyrizz/htdocs/www.healthyrizz.ca/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8090 main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

# 5. Update permissions if needed
echo "Setting proper permissions..."
ssh $VPS_USER@$VPS_HOST "chown -R healthyrizz:healthyrizz $APP_DIR"
ssh $VPS_USER@$VPS_HOST "chmod -R 755 $APP_DIR"

# 6. Reload systemd and restart the service
echo "Reloading systemd and restarting service..."
ssh $VPS_USER@$VPS_HOST "systemctl daemon-reload"
ssh $VPS_USER@$VPS_HOST "systemctl restart healthyrizz"

echo "===== DEPLOYMENT COMPLETED SUCCESSFULLY ====="
echo "HealthyRizz is now running with PWA functionality at https://healthyrizz.ca"
echo "You can check the logs with: ssh $VPS_USER@$VPS_HOST 'journalctl -u healthyrizz -n 50'"
