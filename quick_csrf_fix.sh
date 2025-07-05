#!/bin/bash

# Quick CSRF Fix for VPS
# This script quickly fixes the immediate CSRF error

echo "🔧 Quick CSRF Fix for VPS..."

# Set variables
APP_DIR="/home/healthyrizz/htdocs/healthyrizz.in"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Quick fix: Remove any @csrf.exempt decorators from main_routes.py
print_status "Removing @csrf.exempt decorators from main_routes.py..."

# Create a backup first
cp "$APP_DIR/routes/main_routes.py" "$APP_DIR/routes/main_routes.py.backup"

# Remove @csrf.exempt lines
sed -i '/@csrf\.exempt/d' "$APP_DIR/routes/main_routes.py"

print_status "✅ Removed @csrf.exempt decorators"

# Check for syntax errors
print_status "Checking syntax..."
cd "$APP_DIR"
python3 -c "import routes.main_routes" 2>/dev/null

if [ $? -eq 0 ]; then
    print_status "✅ Syntax check passed"
    
    # Try to start the application
    print_status "Starting application..."
    cd "$APP_DIR"
    python3 app.py &
    APP_PID=$!
    
    # Wait a moment
    sleep 3
    
    # Check if it's running
    if kill -0 $APP_PID 2>/dev/null; then
        print_status "✅ Application started successfully (PID: $APP_PID)"
        print_status "Application should now be running without CSRF errors"
        print_status "You can now test the payment flow"
    else
        print_error "❌ Application failed to start"
        print_status "Check the logs for more details"
    fi
else
    print_error "❌ Syntax check failed"
    print_status "Restoring backup..."
    cp "$APP_DIR/routes/main_routes.py.backup" "$APP_DIR/routes/main_routes.py"
    print_status "Backup restored. Please check the file manually."
fi

echo ""
print_status "Quick CSRF fix completed!" 