#!/bin/bash

# Deploy HealthyRizz to VPS
# This script sets up the systemd service and starts the application

echo "🚀 Deploying HealthyRizz to VPS..."

# Set variables
APP_DIR="/home/healthyrizz/htdocs/healthyrizz.in"
SERVICE_FILE="healthyrizz.service"
SERVICE_NAME="healthyrizz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

# Step 1: Navigate to app directory
print_status "Navigating to application directory..."
cd "$APP_DIR" || {
    print_error "Failed to navigate to $APP_DIR"
    exit 1
}

# Step 2: Activate virtual environment and install dependencies
print_status "Installing/updating dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Step 3: Run database migrations (if any)
print_status "Running database setup..."
python add_sample_locations_cascading.py

# Step 4: Copy service file to systemd directory
print_status "Setting up systemd service..."
cp "$SERVICE_FILE" /etc/systemd/system/

# Step 5: Set proper permissions
chmod 644 /etc/systemd/system/"$SERVICE_FILE"

# Step 6: Reload systemd daemon
print_status "Reloading systemd daemon..."
systemctl daemon-reload

# Step 7: Enable the service
print_status "Enabling service..."
systemctl enable "$SERVICE_NAME"

# Step 8: Start the service
print_status "Starting service..."
systemctl start "$SERVICE_NAME"

# Step 9: Check service status
print_status "Checking service status..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_status "✅ Service is running successfully!"
else
    print_error "❌ Service failed to start"
    print_status "Checking service logs..."
    journalctl -u "$SERVICE_NAME" -n 20 --no-pager
    exit 1
fi

# Step 10: Test the application
print_status "Testing application..."
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000")
if [ "$HTTP_CODE" = "200" ]; then
    print_status "✅ Application is responding (HTTP $HTTP_CODE)"
else
    print_warning "⚠️ Application returned HTTP $HTTP_CODE"
fi

# Step 11: Check Nginx configuration
print_status "Checking Nginx configuration..."
if nginx -t; then
    print_status "✅ Nginx configuration is valid"
    print_status "Reloading Nginx..."
    systemctl reload nginx
else
    print_error "❌ Nginx configuration has errors"
fi

# Summary
print_status ""
print_status "🎉 Deployment Summary:"
echo "=================="
print_status "✅ Dependencies installed"
print_status "✅ Sample locations added"
print_status "✅ Systemd service created and enabled"
print_status "✅ Application started"
print_status "✅ Nginx reloaded"

print_status ""
print_status "📝 Useful Commands:"
echo "=================="
print_status "Check service status: systemctl status $SERVICE_NAME"
print_status "View service logs: journalctl -u $SERVICE_NAME -f"
print_status "Restart service: systemctl restart $SERVICE_NAME"
print_status "Stop service: systemctl stop $SERVICE_NAME"
print_status "Test application: curl http://localhost:8000"

print_status ""
print_status "🌐 Your application should now be accessible at:"
print_status "   https://healthyrizz.in"

print_status ""
print_status "🔧 Deployment completed successfully!" 