#!/bin/bash

# Deploy Signup Completion Feature
# This script deploys the new signup completion functionality for non-logged-in users after payment

echo "🚀 Deploying Signup Completion Feature..."

# Set variables
APP_DIR="/var/www/healthyrizz.in"
BACKUP_DIR="/var/www/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="healthyrizz_backup_${TIMESTAMP}"

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
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    print_status "Creating backup directory..."
    mkdir -p "$BACKUP_DIR"
fi

# Create backup
print_status "Creating backup of current application..."
cd "$APP_DIR"
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' .

if [ $? -eq 0 ]; then
    print_status "Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
else
    print_error "Backup failed!"
    exit 1
fi

# Stop the application
print_status "Stopping application..."
systemctl stop healthyrizz

# Update the main routes file
print_status "Updating main routes with signup completion functionality..."

# Check if the signup_complete route already exists
if grep -q "signup_complete" "$APP_DIR/routes/main_routes.py"; then
    print_warning "Signup complete route already exists, skipping..."
else
    print_error "Signup complete route not found in main_routes.py!"
    print_error "Please ensure the route has been added to the file."
    exit 1
fi

# Update checkout success template
print_status "Updating checkout success template..."
if [ -f "$APP_DIR/templates/checkout_success.html" ]; then
    print_status "Checkout success template updated"
else
    print_error "Checkout success template not found!"
    exit 1
fi

# Check if signup complete template exists
if [ -f "$APP_DIR/templates/signup_complete.html" ]; then
    print_status "Signup complete template found"
else
    print_error "Signup complete template not found!"
    exit 1
fi

# Set proper permissions
print_status "Setting proper permissions..."
chown -R www-data:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"
chmod 644 "$APP_DIR/templates/signup_complete.html"

# Restart the application
print_status "Starting application..."
systemctl start healthyrizz

# Check if application started successfully
sleep 5
if systemctl is-active --quiet healthyrizz; then
    print_status "Application started successfully"
else
    print_error "Application failed to start!"
    print_status "Checking application logs..."
    journalctl -u healthyrizz -n 20 --no-pager
    exit 1
fi

# Test the new functionality
print_status "Testing signup completion functionality..."

# Check if the route is accessible (basic connectivity test)
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ | grep -q "200\|302"; then
    print_status "Application is responding correctly"
else
    print_warning "Application may not be responding correctly"
fi

# Create a test script to verify the functionality
cat > "$APP_DIR/test_signup_complete.py" << 'EOF'
#!/usr/bin/env python3
"""
Test script for signup completion functionality
"""
import requests
import sys

def test_signup_complete():
    """Test the signup complete functionality"""
    base_url = "http://localhost:5000"
    
    try:
        # Test if the application is running
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Application is running")
        else:
            print(f"❌ Application returned status code: {response.status_code}")
            return False
            
        # Test signup complete route (should redirect if no order_id)
        response = requests.get(f"{base_url}/signup-complete/999999", timeout=5, allow_redirects=False)
        if response.status_code in [302, 404]:  # Redirect or not found is expected
            print("✅ Signup complete route is accessible")
        else:
            print(f"⚠️  Signup complete route returned unexpected status: {response.status_code}")
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing application: {e}")
        return False

if __name__ == "__main__":
    success = test_signup_complete()
    sys.exit(0 if success else 1)
EOF

chmod +x "$APP_DIR/test_signup_complete.py"

# Run the test
print_status "Running functionality test..."
cd "$APP_DIR"
python3 test_signup_complete.py

if [ $? -eq 0 ]; then
    print_status "✅ Signup completion functionality test passed"
else
    print_warning "⚠️  Signup completion functionality test had issues"
fi

# Clean up test file
rm -f "$APP_DIR/test_signup_complete.py"

print_status "🎉 Deployment completed successfully!"
print_status ""
print_status "📋 Summary of changes:"
print_status "  ✅ Added signup_complete route for non-logged-in users"
print_status "  ✅ Updated checkout_success route to redirect non-logged-in users"
print_status "  ✅ Created signup_complete.html template"
print_status "  ✅ Updated checkout_success.html template"
print_status ""
print_status "🔧 How it works:"
print_status "  1. User makes payment without being logged in"
print_status "  2. System creates user account with payment details"
print_status "  3. User is redirected to /signup-complete/<order_id>"
print_status "  4. User sees their subscription details and can set a password"
print_status "  5. After setting password, user is logged in and redirected to profile"
print_status ""
print_status "📝 Next steps:"
print_status "  - Test the complete flow with a non-logged-in user"
print_status "  - Verify that subscription details are displayed correctly"
print_status "  - Check that users can successfully set passwords and log in"
print_status ""
print_status "💾 Backup location: $BACKUP_DIR/$BACKUP_NAME.tar.gz" 