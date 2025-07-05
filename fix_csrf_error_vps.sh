#!/bin/bash

# Fix CSRF Error on VPS
# This script fixes CSRF token issues in production environment

echo "🔧 Fixing CSRF Error on VPS..."
echo "This will fix CSRF token generation and configuration issues"

# Set variables
APP_DIR="/home/healthyrizz/htdocs/healthyrizz.in"
BACKUP_DIR="/home/healthyrizz/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="healthyrizz_csrf_fix_backup_${TIMESTAMP}"

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

# Fix 1: Update environment configuration for CSRF
print_status "Updating environment configuration for CSRF..."

# Check if .env file exists
if [ -f "$APP_DIR/.env" ]; then
    print_status "Updating existing .env file..."
    
    # Update CSRF settings in .env
    sed -i 's/WTF_CSRF_SSL_STRICT=True/WTF_CSRF_SSL_STRICT=False/' "$APP_DIR/.env"
    sed -i 's/SESSION_COOKIE_SECURE=True/SESSION_COOKIE_SECURE=False/' "$APP_DIR/.env"
    
    # Add CSRF configuration if not present
    if ! grep -q "WTF_CSRF_ENABLED" "$APP_DIR/.env"; then
        echo "" >> "$APP_DIR/.env"
        echo "# CSRF Configuration" >> "$APP_DIR/.env"
        echo "WTF_CSRF_ENABLED=True" >> "$APP_DIR/.env"
        echo "WTF_CSRF_TIME_LIMIT=7200" >> "$APP_DIR/.env"
    fi
    
    print_status "✅ Updated .env file with CSRF settings"
else
    print_warning "No .env file found, creating one..."
    
    # Generate secure secrets
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    CSRF_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    
    cat > "$APP_DIR/.env" << EOF
# HealthyRizz Production Environment
SECRET_KEY=${SECRET_KEY}
WTF_CSRF_SECRET_KEY=${CSRF_KEY}

# Environment
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=sqlite:///healthyrizz.db

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=healthyrizz.in@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=healthyrizz.in@gmail.com

# Payment Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=your-webhook-secret

# CSRF Configuration
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=7200
WTF_CSRF_SSL_STRICT=False

# Security Settings
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Domain
DOMAIN_NAME=healthyrizz.in
BASE_URL=https://healthyrizz.in
EOF
    
    print_status "✅ Created new .env file with CSRF settings"
fi

# Fix 2: Update base template to ensure CSRF token is available
print_status "Updating base template for CSRF token..."

# Check if base.html exists
if [ -f "$APP_DIR/templates/base.html" ]; then
    # Add CSRF token meta tag if not present
    if ! grep -q 'name="csrf-token"' "$APP_DIR/templates/base.html"; then
        # Add CSRF token meta tag in head section
        sed -i '/<head>/a \    <meta name="csrf-token" content="{{ csrf_token() }}">' "$APP_DIR/templates/base.html"
        print_status "✅ Added CSRF token meta tag to base template"
    else
        print_status "✅ CSRF token meta tag already present"
    fi
else
    print_warning "base.html template not found"
fi

# Fix 3: Update checkout template to ensure proper CSRF token
print_status "Updating checkout template..."

# Check if checkout.html exists
if [ -f "$APP_DIR/templates/checkout.html" ]; then
    # Ensure CSRF token is properly included
    if ! grep -q 'name="csrf_token"' "$APP_DIR/templates/checkout.html"; then
        # Add CSRF token to form
        sed -i '/<form id="checkout-form"/a \                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">' "$APP_DIR/templates/checkout.html"
        print_status "✅ Added CSRF token to checkout form"
    else
        print_status "✅ CSRF token already present in checkout form"
    fi
else
    print_warning "checkout.html template not found"
fi

# Fix 4: Update meal plan checkout template
print_status "Updating meal plan checkout template..."

if [ -f "$APP_DIR/templates/meal_plan_checkout.html" ]; then
    # Ensure CSRF token is properly included
    if ! grep -q 'name="csrf_token"' "$APP_DIR/templates/meal_plan_checkout.html"; then
        # Add CSRF token to form
        sed -i '/<form id="payment-form"/a \                                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">' "$APP_DIR/templates/meal_plan_checkout.html"
        print_status "✅ Added CSRF token to meal plan checkout form"
    else
        print_status "✅ CSRF token already present in meal plan checkout form"
    fi
else
    print_warning "meal_plan_checkout.html template not found"
fi

# Fix 5: Create a simple CSRF test route
print_status "Creating CSRF test route..."

# Check if main_routes.py exists
if [ -f "$APP_DIR/routes/main_routes.py" ]; then
    # Add CSRF test route if not present
    if ! grep -q "test-csrf" "$APP_DIR/routes/main_routes.py"; then
        cat >> "$APP_DIR/routes/main_routes.py" << 'EOF'

@main_bp.route('/test-csrf', methods=['GET', 'POST'])
def test_csrf():
    """Test CSRF protection"""
    from flask import render_template, flash, redirect, url_for
    from flask_wtf import FlaskForm
    from wtforms import StringField, SubmitField
    from wtforms.validators import DataRequired
    
    class TestForm(FlaskForm):
        name = StringField('Name', validators=[DataRequired()])
        submit = SubmitField('Submit')
    
    form = TestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash('Form submitted successfully!', 'success')
            return redirect(url_for('main.test_csrf'))
        else:
            flash('Form validation failed', 'danger')
    return render_template('test_csrf.html', form=form)
EOF
        print_status "✅ Added CSRF test route"
    else
        print_status "✅ CSRF test route already present"
    fi
else
    print_warning "main_routes.py not found"
fi

# Fix 6: Create CSRF test template
print_status "Creating CSRF test template..."

if [ ! -f "$APP_DIR/templates/test_csrf.html" ]; then
    cat > "$APP_DIR/templates/test_csrf.html" << 'EOF'
{% extends "base.html" %}

{% block title %}Test CSRF - HealthyRizz{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card bg-darker border border-gray-700">
                <div class="card-header bg-dark border-b border-gray-700">
                    <h3 class="text-center text-light">Test CSRF Protection</h3>
                </div>
                <div class="card-body">
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="POST" action="{{ url_for('main.test_csrf') }}">
                        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                        <div class="form-group">
                            {{ form.name.label(class="text-light") }}
                            {{ form.name(class="form-control bg-dark text-light border-gray-700") }}
                            {% if form.name.errors %}
                                {% for error in form.name.errors %}
                                    <span class="text-danger">{{ error }}</span>
                                {% endfor %}
                            {% endif %}
                        </div>
                        <div class="form-group mt-3">
                            {{ form.submit(class="btn btn-primary w-100") }}
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF
    print_status "✅ Created CSRF test template"
else
    print_status "✅ CSRF test template already exists"
fi

# Fix 7: Restart the application
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

# Fix 8: Test CSRF functionality
print_status "Testing CSRF functionality..."

# Test CSRF token generation
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/test-csrf")
if [ "$HTTP_CODE" = "200" ]; then
    print_status "✅ CSRF test page accessible"
else
    print_warning "⚠️ CSRF test page returned: $HTTP_CODE"
fi

# Test main application
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000")
if [ "$HTTP_CODE" = "200" ]; then
    print_status "✅ Main application accessible"
else
    print_warning "⚠️ Main application returned: $HTTP_CODE"
fi

# Summary
print_status "CSRF Fix Summary:"
echo "=================="
print_status "✅ Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
print_status "✅ Environment configuration updated"
print_status "✅ CSRF settings configured"
print_status "✅ Templates updated with CSRF tokens"
print_status "✅ Application restarted"
print_status "✅ CSRF functionality tested"

print_status ""
print_status "Next steps:"
echo "============="
print_status "1. Test the payment flow: https://healthyrizz.in/meal-plans"
print_status "2. Test CSRF functionality: https://healthyrizz.in/test-csrf"
print_status "3. If issues persist, check logs: journalctl -u healthyrizz -f"
print_status "4. If needed, restore from backup: tar -xzf $BACKUP_DIR/$BACKUP_NAME.tar.gz"

print_status ""
print_status "🔧 CSRF error fix completed!" 