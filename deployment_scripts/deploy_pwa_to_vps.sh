#!/bin/bash
# Deploy PWA functionality to VPS

# VPS details (replace with your actual VPS info)
VPS_USER="root"
VPS_HOST="your.vps.ip.address"
APP_DIR="/home/healthyrizz/htdocs/www.healthyrizz.ca"

# Create directories if they don't exist
echo "Creating directories..."
ssh $VPS_USER@$VPS_HOST "mkdir -p $APP_DIR/static/js $APP_DIR/static/icons"

# Transfer PWA files
echo "Transferring PWA files..."
scp static/manifest.json $VPS_USER@$VPS_HOST:$APP_DIR/static/
scp static/js/service-worker.js $VPS_USER@$VPS_HOST:$APP_DIR/static/js/
scp static/js/register-sw.js $VPS_USER@$VPS_HOST:$APP_DIR/static/js/
scp static/offline.html $VPS_USER@$VPS_HOST:$APP_DIR/static/
scp static/icons/* $VPS_USER@$VPS_HOST:$APP_DIR/static/icons/
scp static/favicon.ico $VPS_USER@$VPS_HOST:$APP_DIR/static/

# Copy route files
echo "Transferring PWA route files..."
scp routes_pwa.py $VPS_USER@$VPS_HOST:$APP_DIR/

# Update base template
echo "Updating templates..."
scp templates/base.html $VPS_USER@$VPS_HOST:$APP_DIR/templates/

# Update main.py to import routes_pwa
echo "Updating main.py to import PWA routes..."
ssh $VPS_USER@$VPS_HOST "grep -q 'import routes_pwa' $APP_DIR/main.py || cat >> $APP_DIR/main.py << 'EOF'

# Import PWA routes
try:
    import routes_pwa
    print(\"✅ PWA routes imported successfully\")
except Exception as e:
    print(f\"❌ Error importing PWA routes: {str(e)}\")
EOF"

echo "Deployment completed!"
echo "Now restart your application with 'sudo systemctl restart healthyrizz'"
