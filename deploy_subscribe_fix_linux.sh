#!/bin/bash

# Deploy Subscribe Route Fix
# This script fixes the internal server error in the subscribe route

echo "🚀 Deploying Subscribe Route Fix..."
echo "This will fix the internal server error when clicking 'Subscribe Now'"

# Set variables
APP_DIR="/home/healthyrizz/htdocs/healthyrizz.in"
BACKUP_DIR="/home/healthyrizz/backups"
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

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    print_status "Creating backup directory..."
    mkdir -p "$BACKUP_DIR"
fi

# Create backup
print_status "Creating backup..."
cd "$APP_DIR"
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' .
if [ $? -eq 0 ]; then
    print_status "Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
else
    print_error "Failed to create backup"
    exit 1
fi

# Fix 1: Add missing imports to main_routes.py
print_status "Fixing missing imports in main_routes.py..."

# Create a temporary file with the fixed imports
cat > /tmp/fixed_imports.py << 'IMPORTS_EOF'
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.models import db, User, MealPlan, Order, Subscription, BlogPost, DeliveryLocation, State, City, Area, CouponCode, CouponUsage
from forms.auth_forms import LoginForm, RegisterForm, ProfileForm, ContactForm, NewsletterForm
from forms.checkout_forms import CheckoutForm
from forms.trial_forms import TrialRequestForm
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
import json
import logging
from utils.decorators import admin_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
IMPORTS_EOF

# Replace the first 15 lines of main_routes.py with the fixed imports
head -n 15 /tmp/fixed_imports.py > /tmp/new_imports.txt
tail -n +16 "$APP_DIR/routes/main_routes.py" >> /tmp/new_imports.txt
mv /tmp/new_imports.txt "$APP_DIR/routes/main_routes.py"

# Fix 2: Ensure CheckoutForm is properly imported
print_status "Verifying CheckoutForm import..."
if grep -q "from forms.checkout_forms import CheckoutForm" "$APP_DIR/routes/main_routes.py"; then
    print_status "✅ CheckoutForm import is present"
else
    print_error "❌ CheckoutForm import is missing"
    exit 1
fi

# Fix 3: Check if the subscribe route exists and is properly formatted
print_status "Checking subscribe route..."
if grep -q "@main_bp.route('/subscribe/<int:plan_id>')" "$APP_DIR/routes/main_routes.py"; then
    print_status "✅ Subscribe route exists"
else
    print_error "❌ Subscribe route not found"
    exit 1
fi

# Fix 4: Ensure the checkout template exists
print_status "Checking checkout template..."
if [ -f "$APP_DIR/templates/checkout.html" ]; then
    print_status "✅ Checkout template exists"
else
    print_error "❌ Checkout template missing"
    exit 1
fi

# Fix 5: Check for any syntax errors in the main routes file
print_status "Checking for syntax errors..."
cd "$APP_DIR"
python3 -m py_compile routes/main_routes.py
if [ $? -eq 0 ]; then
    print_status "✅ No syntax errors in main_routes.py"
else
    print_error "❌ Syntax errors found in main_routes.py"
    exit 1
fi

# Fix 6: Restart the application
print_status "Restarting the application..."
systemctl restart healthyrizz
if [ $? -eq 0 ]; then
    print_status "✅ Application restarted successfully"
else
    print_error "❌ Failed to restart application"
    exit 1
fi

# Wait a moment for the application to start
sleep 3

# Fix 7: Test the application
print_status "Testing the application..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ | grep -q "200"; then
    print_status "✅ Application is responding"
else
    print_error "❌ Application is not responding"
    exit 1
fi

# Fix 8: Test the subscribe route specifically
print_status "Testing subscribe route..."
# First, get a valid plan ID from the meal plans page
PLAN_ID=$(curl -s http://localhost:5000/meal-plans | grep -o '/subscribe/[0-9]*' | head -1 | cut -d'/' -f3)

if [ -n "$PLAN_ID" ]; then
    print_status "Testing subscribe route with plan ID: $PLAN_ID"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/subscribe/$PLAN_ID")
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_status "✅ Subscribe route is working correctly"
    elif [ "$HTTP_CODE" = "404" ]; then
        print_warning "⚠️ Subscribe route returned 404 (plan not found)"
    elif [ "$HTTP_CODE" = "500" ]; then
        print_error "❌ Subscribe route still has internal server error"
        print_status "Checking application logs..."
        journalctl -u healthyrizz --since "5 minutes ago" | tail -20
        exit 1
    else
        print_warning "⚠️ Subscribe route returned unexpected status: $HTTP_CODE"
    fi
else
    print_warning "⚠️ No plan IDs found to test with"
fi

# Fix 9: Create a test script for future debugging
print_status "Creating test script..."
cat > "$APP_DIR/test_subscribe_debug.py" << 'TEST_EOF'
#!/usr/bin/env python3
"""
Debug script for subscribe route issues
"""
import requests
import sys

def test_subscribe_route():
    base_url = "http://localhost:5000"
    
    # Test basic connectivity
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Homepage status: {response.status_code}")
    except Exception as e:
        print(f"Connection error: {e}")
        return False
    
    # Test meal plans page
    try:
        response = requests.get(f"{base_url}/meal-plans", timeout=5)
        print(f"Meal plans status: {response.status_code}")
        
        # Extract plan IDs
        import re
        plan_ids = re.findall(r'/subscribe/(\d+)', response.text)
        print(f"Found plan IDs: {plan_ids}")
        
        if plan_ids:
            # Test subscribe route
            plan_id = plan_ids[0]
            response = requests.get(f"{base_url}/subscribe/{plan_id}", timeout=10)
            print(f"Subscribe route status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Subscribe route is working!")
                return True
            else:
                print(f"❌ Subscribe route failed with status: {response.status_code}")
                return False
        else:
            print("❌ No plan IDs found")
            return False
            
    except Exception as e:
        print(f"Error testing subscribe route: {e}")
        return False

if __name__ == "__main__":
    success = test_subscribe_route()
    sys.exit(0 if success else 1)
TEST_EOF

chmod +x "$APP_DIR/test_subscribe_debug.py"

# Summary
print_status "Deployment Summary:"
echo "======================"
print_status "✅ Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
print_status "✅ Missing imports fixed"
print_status "✅ Application restarted"
print_status "✅ Basic connectivity verified"
print_status "✅ Test script created: test_subscribe_debug.py"

print_status ""
print_status "Next steps:"
echo "============="
print_status "1. Test the subscribe functionality manually"
print_status "2. If issues persist, run: python3 test_subscribe_debug.py"
print_status "3. Check logs: journalctl -u healthyrizz -f"
print_status "4. If needed, restore from backup: tar -xzf $BACKUP_DIR/$BACKUP_NAME.tar.gz"

print_status ""
print_status "🚀 Subscribe route fix deployment completed!" 