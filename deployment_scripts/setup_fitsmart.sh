#!/bin/bash

# Text formatting
BOLD="\033[1m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RESET="\033[0m"

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${RESET} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${RESET} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${RESET} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${RESET} $1"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_info "Detected Python version: $PYTHON_VERSION"

# Create virtual environment
log_info "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    log_error "Failed to create virtual environment"
    exit 1
fi
log_success "Virtual environment created"

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    log_error "Failed to activate virtual environment"
    exit 1
fi
log_success "Virtual environment activated"

# Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    log_warning "Failed to upgrade pip, continuing anyway..."
fi

# Install requirements
log_info "Installing requirements..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    log_error "Failed to install requirements"
    exit 1
fi
log_success "Requirements installed successfully"

# Create systemd service file
log_info "Creating systemd service file..."
sudo tee /etc/systemd/system/healthyrizz.service > /dev/null << EOF
[Unit]
Description=HealthyRizz Meal Delivery Service
After=network.target postgresql.service

[Service]
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
log_info "Reloading systemd..."
sudo systemctl daemon-reload

# Enable and start service
log_info "Enabling and starting HealthyRizz service..."
sudo systemctl enable healthyrizz
sudo systemctl start healthyrizz

# Check service status
log_info "Checking service status..."
if systemctl is-active --quiet healthyrizz; then
    log_success "HealthyRizz service is running"
else
    log_error "HealthyRizz service failed to start"
    echo "Checking logs:"
    sudo journalctl -u healthyrizz -n 50 --no-pager
    exit 1
fi

# Create log directory
log_info "Creating log directory..."
sudo mkdir -p /var/log/healthyrizz
sudo chown $USER:$USER /var/log/healthyrizz

# Set up database
log_info "Setting up database..."
python3 -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Final instructions
echo
echo -e "${BOLD}${GREEN}HealthyRizz Setup Complete!${RESET}"
echo "----------------------------------------"
echo
echo "Your HealthyRizz application has been set up with the following details:"
echo
echo "Application directory: $(pwd)"
echo "Virtual environment: $(pwd)/venv"
echo "Service name: healthyrizz.service"
echo
echo "To manage your application:"
echo "  - Start: sudo systemctl start healthyrizz"
echo "  - Stop: sudo systemctl stop healthyrizz"
echo "  - Restart: sudo systemctl restart healthyrizz"
echo "  - View logs: sudo journalctl -u healthyrizz -f"
echo
echo "The application should now be running on port 8000"
echo "You can access it at: http://localhost:8000"
echo
echo "If you encounter any issues, please check the application logs for detailed information."
echo 
