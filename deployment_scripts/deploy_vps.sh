#!/bin/bash

# Deploy script for VPS
set -e

echo "Starting HealthyRizz VPS deployment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies from the VPS-specific requirements file
echo "Installing dependencies..."
pip install -r vps_requirements.txt

# Fix database schema issues
echo "Fixing database schema..."
# Check if database parameters are set as environment variables
if [ -z "$PGDATABASE" ] || [ -z "$PGUSER" ] || [ -z "$PGPASSWORD" ]; then
    echo "Database environment variables not set."
    echo "Please either set PGDATABASE, PGUSER, and PGPASSWORD environment variables"
    echo "or run fix_vps_database.py with command line arguments to provide the credentials."
    echo "For example: python fix_vps_database.py --dbname=yourdb --user=youruser --password=yourpassword"
    
    # Ask for database parameters if not set
    read -p "Would you like to enter database parameters now? (y/n): " choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        read -p "Database name: " dbname
        read -p "Database user: " dbuser
        read -s -p "Database password: " dbpass
        echo ""
        
        # Run with command line arguments
        python fix_vps_database.py --dbname="$dbname" --user="$dbuser" --password="$dbpass"
    else
        echo "Skipping database schema fix. You can run it manually later."
    fi
else
    # Environment variables are set, use them
    python fix_vps_database.py
fi

# Run database migrations if needed
echo "Running database setup..."
python init_database.py

# Restart the application
echo "Restarting the application..."
# Replace the following line with your actual service restart command
# For systemd: sudo systemctl restart healthyrizz
# For supervisor: sudo supervisorctl restart healthyrizz

echo "Deployment completed successfully!"
