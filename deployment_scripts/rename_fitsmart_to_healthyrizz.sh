#!/bin/bash
#
# Script to rename all healthyrizz references to healthyrizz
# This script will update file names, database names, service names, and content references
#

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print status messages
print_status() {
    echo -e "${GREEN}[+] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "${RED}[x] $1${NC}"
}

print_status "Starting rename process from healthyrizz to healthyrizz..."

# 1. Rename files and directories
print_status "Renaming files and directories..."

# Rename main files
if [ -f "healthyrizz.db" ]; then
    mv healthyrizz.db healthyrizz.db
    print_status "Renamed healthyrizz.db to healthyrizz.db"
fi

if [ -f "healthyrizz.service" ]; then
    mv healthyrizz.service healthyrizz.service
    print_status "Renamed healthyrizz.service to healthyrizz.service"
fi

# Rename deployment scripts
for file in deploy_healthyrizz*.sh; do
    if [ -f "$file" ]; then
        new_name=$(echo "$file" | sed 's/healthyrizz/healthyrizz/g')
        mv "$file" "$new_name"
        print_status "Renamed $file to $new_name"
    fi
done

for file in deploy_healthyrizz*.ps1; do
    if [ -f "$file" ]; then
        new_name=$(echo "$file" | sed 's/healthyrizz/healthyrizz/g')
        mv "$file" "$new_name"
        print_status "Renamed $file to $new_name"
    fi
done

# Rename test files
for file in test_*healthyrizz*.py; do
    if [ -f "$file" ]; then
        new_name=$(echo "$file" | sed 's/healthyrizz/healthyrizz/g')
        mv "$file" "$new_name"
        print_status "Renamed $file to $new_name"
    fi
done

# Rename config files
for file in *healthyrizz*.conf; do
    if [ -f "$file" ]; then
        new_name=$(echo "$file" | sed 's/healthyrizz/healthyrizz/g')
        mv "$file" "$new_name"
        print_status "Renamed $file to $new_name"
    fi
done

for file in *healthyrizz*.txt; do
    if [ -f "$file" ]; then
        new_name=$(echo "$file" | sed 's/healthyrizz/healthyrizz/g')
        mv "$file" "$new_name"
        print_status "Renamed $file to $new_name"
    fi
done

# 2. Update content in Python files
print_status "Updating content in Python files..."

# Find all Python files and update content
find . -name "*.py" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*.py" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;
find . -name "*.py" -type f -exec sed -i 's/healthyrizz/HEALTHYRIZZ/g' {} \;

# 3. Update content in configuration files
print_status "Updating content in configuration files..."

# Update .env files
find . -name ".env*" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name ".env*" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;

# Update requirements files
find . -name "requirements*.txt" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;

# Update config files
find . -name "*.conf" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*.cfg" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;

# 4. Update HTML templates
print_status "Updating content in HTML templates..."

find . -name "*.html" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*.html" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;

# 5. Update JavaScript files
print_status "Updating content in JavaScript files..."

find . -name "*.js" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*.js" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;

# 6. Update CSS files
print_status "Updating content in CSS files..."

find . -name "*.css" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*.css" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;

# 7. Update documentation files
print_status "Updating content in documentation files..."

find . -name "*.md" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*.md" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;
find . -name "*.txt" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*.txt" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;

# 8. Update JSON files
print_status "Updating content in JSON files..."

find . -name "*.json" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*.json" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;

# 9. Update shell scripts
print_status "Updating content in shell scripts..."

find . -name "*.sh" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*.sh" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;

# 10. Update PowerShell scripts
print_status "Updating content in PowerShell scripts..."

find . -name "*.ps1" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*.ps1" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;

# 11. Update specific database references
print_status "Updating database references..."

# Update config.py specifically
if [ -f "config.py" ]; then
    sed -i 's/healthyrizz\.db/healthyrizz.db/g' config.py
    sed -i 's/healthyrizz/HealthyRizz/g' config.py
    print_status "Updated config.py"
fi

# Update main.py specifically
if [ -f "main.py" ]; then
    sed -i 's/healthyrizz/healthyrizz/g' main.py
    sed -i 's/healthyrizz/HealthyRizz/g' main.py
    print_status "Updated main.py"
fi

# Update app.py specifically
if [ -f "app.py" ]; then
    sed -i 's/healthyrizz/healthyrizz/g' app.py
    sed -i 's/healthyrizz/HealthyRizz/g' app.py
    print_status "Updated app.py"
fi

# 12. Update service files
print_status "Updating service files..."

if [ -f "healthyrizz.service" ]; then
    sed -i 's/healthyrizz/healthyrizz/g' healthyrizz.service
    sed -i 's/healthyrizz/HealthyRizz/g' healthyrizz.service
    print_status "Updated healthyrizz.service"
fi

# 13. Update nginx configurations
print_status "Updating nginx configurations..."

find . -name "*nginx*" -type f -exec sed -i 's/healthyrizz/healthyrizz/g' {} \;
find . -name "*nginx*" -type f -exec sed -i 's/healthyrizz/HealthyRizz/g' {} \;

# 14. Update manifest.json for PWA
print_status "Updating PWA manifest..."

if [ -f "static/manifest.json" ]; then
    sed -i 's/healthyrizz/healthyrizz/g' static/manifest.json
    sed -i 's/healthyrizz/HealthyRizz/g' static/manifest.json
    print_status "Updated PWA manifest"
fi

# 15. Update robots.txt
print_status "Updating robots.txt..."

if [ -f "robots.txt" ]; then
    sed -i 's/healthyrizz/healthyrizz/g' robots.txt
    sed -i 's/healthyrizz/HealthyRizz/g' robots.txt
    print_status "Updated robots.txt"
fi

# 16. Update sitemap.xml
print_status "Updating sitemap.xml..."

if [ -f "sitemap.xml" ]; then
    sed -i 's/healthyrizz/healthyrizz/g' sitemap.xml
    sed -i 's/healthyrizz/HealthyRizz/g' sitemap.xml
    print_status "Updated sitemap.xml"
fi

print_status "Rename process completed successfully!"
print_status ""
print_status "Summary of changes:"
print_status "- All file names containing 'healthyrizz' have been renamed to 'healthyrizz'"
print_status "- All content references have been updated"
print_status "- Database names updated to use 'healthyrizz'"
print_status "- Service names updated to use 'healthyrizz'"
print_status "- Configuration files updated"
print_status ""
print_status "Next steps:"
print_status "1. Review the changes to ensure everything is correct"
print_status "2. Test the application to make sure it still works"
print_status "3. Update any external references or documentation"
print_status "4. Commit the changes to your version control system" 