# Deploy Subscription Creation Fix
# This script updates the production server with fixes for subscription creation

Write-Host "🚀 Deploying Subscription Creation Fix" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Set variables
$REMOTE_HOST = "89.116.122.69"
$REMOTE_USER = "root"
$REMOTE_PATH = "/home/healthyrizz/htdocs/healthyrizz.in"
$BACKUP_PATH = "/home/healthyrizz/backups"

# Create backup
Write-Host "📦 Creating backup..." -ForegroundColor Yellow
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${BACKUP_PATH}"
ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_PATH} && tar -czf ${BACKUP_PATH}/backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').tar.gz ."

# Stop the application
Write-Host "⏹️  Stopping application..." -ForegroundColor Yellow
ssh ${REMOTE_USER}@${REMOTE_HOST} "supervisorctl stop healthyrizz"

# Update the main routes file with webhook fix
Write-Host "🔧 Updating webhook route..." -ForegroundColor Yellow
scp routes/main_routes.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/routes/

# Update the report utils with skip_date fix
Write-Host "🔧 Updating report utils..." -ForegroundColor Yellow
scp utils/report_utils.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/utils/

# Copy the test scripts
Write-Host "📄 Copying test scripts..." -ForegroundColor Yellow
scp check_daily_orders.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/
scp create_test_subscriptions.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/

# Start the application
Write-Host "▶️  Starting application..." -ForegroundColor Yellow
ssh ${REMOTE_USER}@${REMOTE_HOST} "supervisorctl start healthyrizz"

# Wait for application to start
Write-Host "⏳ Waiting for application to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test the subscription creation
Write-Host "🧪 Testing subscription creation..." -ForegroundColor Yellow
ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_PATH} && source venv/bin/activate && python create_test_subscriptions.py"

# Test daily orders
Write-Host "🧪 Testing daily orders..." -ForegroundColor Yellow
ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_PATH} && source venv/bin/activate && python check_daily_orders.py"

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 What was fixed:" -ForegroundColor Cyan
Write-Host "   1. Webhook now creates subscriptions after payment" -ForegroundColor White
Write-Host "   2. verify_payment route links subscriptions to orders" -ForegroundColor White
Write-Host "   3. Fixed skip_date bug in report_utils" -ForegroundColor White
Write-Host "   4. Added test scripts for verification" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Check admin panel for daily orders" -ForegroundColor White
Write-Host "   2. Test a new payment to verify subscription creation" -ForegroundColor White
Write-Host "   3. Monitor webhook logs for any errors" -ForegroundColor White 