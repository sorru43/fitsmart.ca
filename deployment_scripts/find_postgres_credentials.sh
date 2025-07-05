#!/bin/bash
# Script to help find PostgreSQL credentials on your VPS

echo "========================="
echo "HealthyRizz Database Credential Finder"
echo "========================="
echo "This script will search for database credentials in common locations."
echo ""

APP_DIR="/home/healthyrizz/htdocs/www.healthyrizz.ca"

echo "Checking for database connection info in common files..."

# Check for environment variables in files
echo "Looking for DATABASE_URL or connection params in configuration files:"
grep -r "DATABASE_URL\|PGDATABASE\|PGUSER\|PGPASSWORD" $APP_DIR --include="*.py" --include="*.sh" --include="*.env" --include="*.conf" 2>/dev/null
echo ""

# Check .env files
echo "Checking for .env files:"
if [ -f "$APP_DIR/.env" ]; then
    echo "Found .env file:"
    cat "$APP_DIR/.env" | grep -i "DB_\|DATABASE\|PG" 2>/dev/null
else
    echo "No .env file found."
fi
echo ""

# Check Python files for database connection
echo "Checking Python files for database configuration:"
grep -r "db.*connect\|SQLAlchemy.*URI\|create_engine" $APP_DIR --include="*.py" 2>/dev/null
echo ""

# Check for database config in main application files
echo "Looking in main application files:"
for file in "$APP_DIR/app.py" "$APP_DIR/main.py" "$APP_DIR/config.py" "$APP_DIR/db_config.py"; do
    if [ -f "$file" ]; then
        echo "Contents of $file:"
        grep -i "database\|sqlalchemy\|psycopg\|postgresql\|engine" "$file" 2>/dev/null
    fi
done
echo ""

# Check systemd service files if they exist
echo "Checking systemd service files:"
for service in healthyrizz healthyrizz-web healthyrizz-app; do
    if [ -f "/etc/systemd/system/$service.service" ]; then
        echo "Found service file: $service.service"
        grep -i "environment\|pg\|database" "/etc/systemd/system/$service.service" 2>/dev/null
    fi
done
echo ""

# Check if PostgreSQL is running
echo "Checking if PostgreSQL is running on this server:"
if pgrep -x "postgres" > /dev/null; then
    echo "PostgreSQL is running on this server."
    
    # Check PostgreSQL version
    postgres_version=$(psql --version 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "PostgreSQL client version: $postgres_version"
    fi
    
    echo ""
    echo "To list PostgreSQL databases (requires postgres access):"
    echo "    sudo -u postgres psql -c '\l'"
    echo ""
    echo "To list PostgreSQL users (requires postgres access):"
    echo "    sudo -u postgres psql -c '\du'"
else
    echo "PostgreSQL does not appear to be running on this server."
    echo "The database might be hosted on a separate server."
fi

echo ""
echo "========================="
echo "Credential Search Complete"
echo "========================="
echo ""
echo "Next steps:"
echo "1. Based on the information found, try to identify your database credentials"
echo "2. If you can't find them, you may need to contact your server administrator"
echo "3. Once you have the credentials, run the fix script with:"
echo "   python fix_vps_database.py --dbname=your_db_name --user=your_db_user --password=your_password"
echo ""
echo "Alternatively, if you have sudo access, you can run the direct fix script:"
echo "   bash fix_postgres_direct.sh"
