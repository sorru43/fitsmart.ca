#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="healthyrizz"
APP_DIR="/var/www/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
REQUIREMENTS_FILE="requirements.txt"
GUNICORN_SERVICE="/etc/systemd/system/$APP_NAME.service"

# Create application directory
echo "Creating application directory..."
sudo rm -rf $APP_DIR
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Copy application files
echo "Copying application files..."
cp -r ./* $APP_DIR/
cp -r ./.* $APP_DIR/ 2>/dev/null || true  # Copy hidden files like .env

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
cd $APP_DIR
python3 -m venv $VENV_DIR

# Install Python dependencies
echo "Installing Python dependencies..."
$VENV_DIR/bin/python -m pip install --upgrade pip
$VENV_DIR/bin/python -m pip install gunicorn
$VENV_DIR/bin/python -m pip install -r $REQUIREMENTS_FILE

# Create Gunicorn service
echo "Creating Gunicorn service..."
sudo tee $GUNICORN_SERVICE > /dev/null << EOF
[Unit]
Description=Gunicorn instance to serve $APP_NAME
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="PYTHONPATH=$APP_DIR"
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$APP_DIR/$APP_NAME.sock -m 007 main:app --log-level debug

[Install]
WantedBy=multi-user.target
EOF

# Set proper permissions
echo "Setting proper permissions..."
sudo chown -R $USER:$USER $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod 640 $APP_DIR/.env

# Create necessary directories
echo "Creating necessary directories..."
sudo mkdir -p $APP_DIR/logs
sudo mkdir -p $APP_DIR/instance
sudo chown -R $USER:$USER $APP_DIR/logs $APP_DIR/instance

# Reload systemd and start service
echo "Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl start $APP_NAME
sudo systemctl enable $APP_NAME

echo "Deployment completed successfully!"
echo "You can check the application status with: sudo systemctl status $APP_NAME"
echo "You can check the application logs with: sudo journalctl -u $APP_NAME -f" 
