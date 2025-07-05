#!/bin/bash

# Fix CSRF Error on VPS
# This script removes any remaining @csrf.exempt decorators and ensures proper CSRF imports

echo "🔧 Fixing CSRF Error on VPS..."
echo "This will remove any remaining @csrf.exempt decorators and ensure proper CSRF imports"

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

# Fix 1: Remove any remaining @csrf.exempt decorators from main_routes.py
print_status "Removing @csrf.exempt decorators from main_routes.py..."

# Create a temporary file with the fixed content
sed '/@csrf\.exempt/d' "$APP_DIR/routes/main_routes.py" > /tmp/fixed_main_routes.py

# Check if the file was modified
if ! cmp -s "$APP_DIR/routes/main_routes.py" /tmp/fixed_main_routes.py; then
    mv /tmp/fixed_main_routes.py "$APP_DIR/routes/main_routes.py"
    print_status "✅ Removed @csrf.exempt decorators from main_routes.py"
else
    print_status "✅ No @csrf.exempt decorators found in main_routes.py"
fi

# Fix 2: Ensure proper CSRF imports in main_routes.py
print_status "Ensuring proper CSRF imports in main_routes.py..."

# Check if CSRFProtect is imported
if ! grep -q "from flask_wtf.csrf import CSRFProtect" "$APP_DIR/routes/main_routes.py"; then
    print_status "Adding CSRFProtect import..."
    # Add import after other flask imports
    sed -i '/from flask import/a from flask_wtf.csrf import CSRFProtect' "$APP_DIR/routes/main_routes.py"
    print_status "✅ Added CSRFProtect import"
else
    print_status "✅ CSRFProtect import already present"
fi

# Fix 3: Check for any other files with @csrf.exempt
print_status "Checking other files for @csrf.exempt decorators..."

# Find all Python files with @csrf.exempt
CSRF_FILES=$(grep -r "@csrf\.exempt" "$APP_DIR" --include="*.py" | cut -d: -f1 | sort | uniq)

if [ -n "$CSRF_FILES" ]; then
    print_warning "Found @csrf.exempt in the following files:"
    echo "$CSRF_FILES"
    
    # Remove @csrf.exempt from all found files
    for file in $CSRF_FILES; do
        if [ -f "$file" ]; then
            print_status "Removing @csrf.exempt from $file"
            sed -i '/@csrf\.exempt/d' "$file"
        fi
    done
    print_status "✅ Removed @csrf.exempt from all files"
else
    print_status "✅ No @csrf.exempt decorators found in any files"
fi

# Fix 4: Check for any remaining csrf references that might cause issues
print_status "Checking for any remaining csrf references..."

# Look for any undefined csrf references
CSRF_UNDEFINED=$(grep -r "csrf\." "$APP_DIR" --include="*.py" | grep -v "from flask_wtf.csrf" | grep -v "CSRFProtect" | grep -v "csrf_token" | grep -v "csrf.exempt" | head -10)

if [ -n "$CSRF_UNDEFINED" ]; then
    print_warning "Found potential undefined csrf references:"
    echo "$CSRF_UNDEFINED"
    print_warning "These will be removed..."
    
    # Remove any remaining csrf. references
    find "$APP_DIR" -name "*.py" -exec sed -i '/csrf\./d' {} \;
    print_status "✅ Removed undefined csrf references"
else
    print_status "✅ No undefined csrf references found"
fi

# Fix 5: Check for syntax errors
print_status "Checking for syntax errors..."
cd "$APP_DIR"
python3 -m py_compile routes/main_routes.py
if [ $? -eq 0 ]; then
    print_status "✅ No syntax errors in main_routes.py"
else
    print_error "❌ Syntax errors found in main_routes.py"
    print_status "Attempting to fix syntax errors..."
    
    # Try to fix common syntax issues
    sed -i 's/^[[:space:]]*@csrf\.exempt.*$//' routes/main_routes.py
    sed -i '/^[[:space:]]*$/d' routes/main_routes.py
    
    # Check again
    python3 -m py_compile routes/main_routes.py
    if [ $? -eq 0 ]; then
        print_status "✅ Syntax errors fixed"
    else
        print_error "❌ Could not fix syntax errors automatically"
        exit 1
    fi
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
    print_status "Checking application logs..."
    journalctl -u healthyrizz --since "2 minutes ago" | tail -20
    exit 1
fi

# Fix 8: Test specific routes that might have had CSRF issues
print_status "Testing routes that might have had CSRF issues..."

# Test meal calculator route
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/meal-calculator")
if [ "$HTTP_CODE" = "200" ]; then
    print_status "✅ Meal calculator route working"
else
    print_warning "⚠️ Meal calculator route returned: $HTTP_CODE"
fi

# Test meal plans route
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/meal-plans")
if [ "$HTTP_CODE" = "200" ]; then
    print_status "✅ Meal plans route working"
else
    print_warning "⚠️ Meal plans route returned: $HTTP_CODE"
fi

# Test subscribe route
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5000/subscribe/1")
if [ "$HTTP_CODE" = "200" ]; then
    print_status "✅ Subscribe route working"
else
    print_warning "⚠️ Subscribe route returned: $HTTP_CODE"
fi

# Summary
print_status "CSRF Fix Summary:"
echo "=================="
print_status "✅ Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
print_status "✅ @csrf.exempt decorators removed"
print_status "✅ CSRF imports verified"
print_status "✅ Syntax errors checked"
print_status "✅ Application restarted"
print_status "✅ Basic connectivity verified"

print_status ""
print_status "Next steps:"
echo "============="
print_status "1. Test the complete payment flow manually"
print_status "2. If issues persist, check logs: journalctl -u healthyrizz -f"
print_status "3. If needed, restore from backup: tar -xzf $BACKUP_DIR/$BACKUP_NAME.tar.gz"

print_status ""
print_status "🔧 CSRF error fix completed!" 