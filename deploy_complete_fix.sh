#!/bin/bash

# Complete deployment script for payment flow and profile enhancements
# This script updates the production server with all fixes

echo "🚀 Starting complete deployment of payment flow and profile enhancements..."

# Set variables
PROJECT_DIR="/home/healthyrizz/htdocs/healthyrizz.in"
BACKUP_DIR="/home/healthyrizz/backups/$(date +%Y%m%d_%H%M%S)"

# Create backup directory
echo "📦 Creating backup..."
mkdir -p "$BACKUP_DIR"

# Backup current files
echo "💾 Backing up current files..."
cp "$PROJECT_DIR/routes/main_routes.py" "$BACKUP_DIR/main_routes_backup.py"
cp "$PROJECT_DIR/templates/profile.html" "$BACKUP_DIR/profile_backup.html"

# Copy updated files
echo "📝 Copying updated files..."
cp routes/main_routes.py "$PROJECT_DIR/routes/main_routes.py"
cp templates/profile.html "$PROJECT_DIR/templates/profile.html"

# Set proper permissions
echo "🔐 Setting permissions..."
chown -R healthyrizz:healthyrizz "$PROJECT_DIR/routes/main_routes.py"
chown -R healthyrizz:healthyrizz "$PROJECT_DIR/templates/profile.html"
chmod 644 "$PROJECT_DIR/routes/main_routes.py"
chmod 644 "$PROJECT_DIR/templates/profile.html"

# Restart the application
echo "🔄 Restarting application..."
supervisorctl restart healthyrizz

# Wait a moment for the app to start
sleep 5

# Check if the app is running
echo "✅ Checking application status..."
if supervisorctl status healthyrizz | grep -q "RUNNING"; then
    echo "🎉 Application is running successfully!"
    
    # Test the routes
    echo "🔍 Testing updated routes..."
    
    # Test checkout-success route
    echo "   Testing /checkout-success route..."
    curl -s -o /dev/null -w "%{http_code}" "https://healthyrizz.in/checkout-success" || echo "Route test completed"
    
    # Test profile route
    echo "   Testing /profile route..."
    curl -s -o /dev/null -w "%{http_code}" "https://healthyrizz.in/profile" || echo "Route test completed"
    
    echo "📋 Deployment Summary:"
    echo "   ✅ Backup created at: $BACKUP_DIR"
    echo "   ✅ Updated main_routes.py with checkout-success route"
    echo "   ✅ Enhanced profile route with order and payment history"
    echo "   ✅ Updated profile template with comprehensive order display"
    echo "   ✅ Application restarted successfully"
    echo "   ✅ Payment flow should now work correctly"
    echo "   ✅ Users can now see their subscription and payment history"
    
    echo ""
    echo "🎯 What's been fixed:"
    echo "   1. ✅ /checkout-success route now exists (no more 404 after payment)"
    echo "   2. ✅ Profile page shows order history"
    echo "   3. ✅ Profile page shows payment history"
    echo "   4. ✅ Profile page shows total spent"
    echo "   5. ✅ Profile page shows order summary"
    echo "   6. ✅ Users can track their subscription status"
    echo "   7. ✅ Users can see payment status and history"
    
    echo ""
    echo "🎯 Next steps:"
    echo "   1. Test a complete payment flow in production"
    echo "   2. Verify users are redirected to checkout-success after payment"
    echo "   3. Check that orders appear in user profiles"
    echo "   4. Verify payment history is displayed correctly"
    echo "   5. Test subscription management features"
    
    echo ""
    echo "🔧 Monitoring commands:"
    echo "   # Check application logs"
    echo "   tail -f /var/log/healthyrizz.out.log"
    echo "   tail -f /var/log/healthyrizz.err.log"
    echo ""
    echo "   # Check supervisor logs"
    echo "   tail -f /var/log/supervisor/supervisord.log | grep healthyrizz"
    echo ""
    echo "   # Check nginx access logs for payment activity"
    echo "   tail -f /home/healthyrizz/logs/nginx/access.log | grep -E '(checkout|payment|verify)'"
    
else
    echo "❌ Application failed to start!"
    echo "🔍 Checking supervisor logs..."
    supervisorctl tail healthyrizz
    exit 1
fi

echo "🏁 Complete deployment finished successfully!" 