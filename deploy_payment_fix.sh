#!/bin/bash

# Deployment script for payment flow fixes
# This script updates the production server with the missing checkout-success route

echo "🚀 Starting deployment of payment flow fixes..."

# Set variables
PROJECT_DIR="/home/healthyrizz/htdocs/healthyrizz.in"
BACKUP_DIR="/home/healthyrizz/backups/$(date +%Y%m%d_%H%M%S)"

# Create backup directory
echo "📦 Creating backup..."
mkdir -p "$BACKUP_DIR"

# Backup current routes file
echo "💾 Backing up current main_routes.py..."
cp "$PROJECT_DIR/routes/main_routes.py" "$BACKUP_DIR/main_routes_backup.py"

# Copy updated files
echo "📝 Copying updated files..."
cp routes/main_routes.py "$PROJECT_DIR/routes/main_routes.py"

# Set proper permissions
echo "🔐 Setting permissions..."
chown -R healthyrizz:healthyrizz "$PROJECT_DIR/routes/main_routes.py"
chmod 644 "$PROJECT_DIR/routes/main_routes.py"

# Restart the application
echo "🔄 Restarting application..."
supervisorctl restart healthyrizz

# Wait a moment for the app to start
sleep 5

# Check if the app is running
echo "✅ Checking application status..."
if supervisorctl status healthyrizz | grep -q "RUNNING"; then
    echo "🎉 Application is running successfully!"
    echo "🔍 Testing checkout-success route..."
    
    # Test the route (this will show if it's accessible)
    curl -s -o /dev/null -w "%{http_code}" "https://healthyrizz.in/checkout-success" || echo "Route test completed"
    
    echo "📋 Deployment Summary:"
    echo "   ✅ Backup created at: $BACKUP_DIR"
    echo "   ✅ Updated main_routes.py with checkout-success route"
    echo "   ✅ Application restarted successfully"
    echo "   ✅ Payment flow should now work correctly"
    
    echo ""
    echo "🎯 Next steps:"
    echo "   1. Test a payment flow in production"
    echo "   2. Check that users are redirected to checkout-success after payment"
    echo "   3. Verify that orders appear in user profiles"
    
else
    echo "❌ Application failed to start!"
    echo "🔍 Checking supervisor logs..."
    supervisorctl tail healthyrizz
    exit 1
fi

echo "🏁 Deployment completed!" 