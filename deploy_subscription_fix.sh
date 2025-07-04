#!/bin/bash

# Deploy Subscription Creation Fix
# This script updates the production server with fixes for subscription creation

echo "🚀 Deploying Subscription Creation Fix"
echo "======================================"

# Set variables
REMOTE_HOST="89.116.122.69"
REMOTE_USER="root"
REMOTE_PATH="/home/healthyrizz/htdocs/healthyrizz.in"
BACKUP_PATH="/home/healthyrizz/backups"

# Create backup
echo "📦 Creating backup..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${BACKUP_PATH}"
ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_PATH} && tar -czf ${BACKUP_PATH}/backup_$(date +%Y%m%d_%H%M%S).tar.gz ."

# Stop the application
echo "⏹️  Stopping application..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "supervisorctl stop healthyrizz"

# Update the main routes file with webhook fix
echo "🔧 Updating webhook route..."
scp routes/main_routes.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/routes/

# Update the report utils with skip_date fix
echo "🔧 Updating report utils..."
scp utils/report_utils.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/utils/

# Copy the test scripts
echo "📄 Copying test scripts..."
scp check_daily_orders.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/
scp create_test_subscriptions.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/

# Start the application
echo "▶️  Starting application..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "supervisorctl start healthyrizz"

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 5

# Test the subscription creation
echo "🧪 Testing subscription creation..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_PATH} && source venv/bin/activate && python create_test_subscriptions.py"

# Test daily orders
echo "🧪 Testing daily orders..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_PATH} && source venv/bin/activate && python check_daily_orders.py"

echo "✅ Deployment completed!"
echo ""
echo "📝 What was fixed:"
echo "   1. Webhook now creates subscriptions after payment"
echo "   2. verify_payment route links subscriptions to orders"
echo "   3. Fixed skip_date bug in report_utils"
echo "   4. Added test scripts for verification"
echo ""
echo "🔍 Next steps:"
echo "   1. Check admin panel for daily orders"
echo "   2. Test a new payment to verify subscription creation"
echo "   3. Monitor webhook logs for any errors" 