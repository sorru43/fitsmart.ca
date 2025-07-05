#!/bin/bash

# Deployment script to run on VPS server
echo "🚀 HealthyRizz Payment Flow Deployment"
echo "======================================"

# Navigate to project directory
cd /home/healthyrizz/htdocs/healthyrizz.in
source venv/bin/activate

echo "📁 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"

# Step 1: Create simple test data
echo ""
echo "🛠️ Step 1: Creating test data..."
python create_simple_test_data.py

# Step 2: Set proper permissions
echo ""
echo "🔐 Step 2: Setting permissions..."
chown -R healthyrizz:healthyrizz /home/healthyrizz/htdocs/healthyrizz.in/
chmod 644 /home/healthyrizz/htdocs/healthyrizz.in/routes/*.py
chmod 644 /home/healthyrizz/htdocs/healthyrizz.in/templates/profile.html
chmod 644 /home/healthyrizz/htdocs/healthyrizz.in/app.py

# Create admin template directory if it doesn't exist
mkdir -p /home/healthyrizz/htdocs/healthyrizz.in/templates/admin/
chmod 755 /home/healthyrizz/htdocs/healthyrizz.in/templates/admin/

# Step 3: Restart application
echo ""
echo "🔄 Step 3: Restarting application..."
supervisorctl restart healthyrizz
sleep 3
supervisorctl status healthyrizz

# Step 4: Test the routes
echo ""
echo "🧪 Step 4: Testing routes..."
echo "Testing checkout-success route:"
curl -I http://localhost:8000/checkout-success 2>/dev/null | head -1

echo "Testing profile route:"
curl -I http://localhost:8000/profile 2>/dev/null | head -1

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Login to your website with admin credentials"
echo "2. Go to /profile to see order and payment history"
echo "3. Check that payment flow works without 404 errors"
echo ""
echo "🔍 Monitor logs with:"
echo "tail -f /var/log/supervisor/healthyrizz-stderr.log" 