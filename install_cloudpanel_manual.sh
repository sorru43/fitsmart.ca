#!/bin/bash

# Manual CloudPanel Installation for HealthyRizz
# Run these commands step by step on your CloudPanel server

echo "=== HealthyRizz CloudPanel Manual Installation ==="
echo "Domain: healthyrizz.in"
echo "Port: 8090"
echo ""

# Check current directory
echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la

# Step 1: Update system packages
echo ""
echo "Step 1: Updating system packages..."
apt update
apt install -y python3-pip python3-venv python3-dev build-essential libpq-dev redis-server

# Step 2: Create virtual environment
echo ""
echo "Step 2: Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Step 3: Install Python dependencies
echo ""
echo "Step 3: Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Step 4: Create environment file
echo ""
echo "Step 4: Creating environment file..."
if [ ! -f ".env" ]; then
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    CSRF_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    
    cat > .env << EOF
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
MAIL_USERNAME=admin@healthyrizz.in
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=admin@healthyrizz.in

# Payment Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Redis
REDIS_URL=redis://localhost:6379/0

# Security Settings
SESSION_COOKIE_SECURE=False
WTF_CSRF_SSL_STRICT=False

# Domain
DOMAIN_NAME=healthyrizz.in
BASE_URL=https://healthyrizz.in
EOF
    chmod 600 .env
    chown healthyrizz:healthyrizz .env
    echo ".env file created"
else
    echo ".env file already exists"
fi

# Step 5: Initialize database
echo ""
echo "Step 5: Initializing database..."
source venv/bin/activate
if [ -f "init_database.py" ]; then
    python init_database.py
else
    python -c "
from main import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
fi

# Step 6: Create Gunicorn configuration
echo ""
echo "Step 6: Creating Gunicorn configuration..."
cat > gunicorn.conf.py << EOF
import multiprocessing

bind = "127.0.0.1:8090"
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
preload_app = True
chdir = "/home/healthyrizz/htdocs/healthyrizz.in"
EOF

# Step 7: Create systemd service
echo ""
echo "Step 7: Creating systemd service..."
cat > /etc/systemd/system/healthyrizz.service << EOF
[Unit]
Description=HealthyRizz Gunicorn Application
After=network.target

[Service]
User=healthyrizz
Group=healthyrizz
WorkingDirectory=/home/healthyrizz/htdocs/healthyrizz.in
Environment=PATH=/home/healthyrizz/htdocs/healthyrizz.in/venv/bin
ExecStart=/home/healthyrizz/htdocs/healthyrizz.in/venv/bin/gunicorn --config gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

# Step 8: Set proper permissions
echo ""
echo "Step 8: Setting permissions..."
chown -R healthyrizz:healthyrizz /home/healthyrizz/htdocs/healthyrizz.in
chmod +x gunicorn.conf.py

# Step 9: Start Redis
echo ""
echo "Step 9: Starting Redis service..."
systemctl enable redis-server
systemctl start redis-server

# Step 10: Start the application service
echo ""
echo "Step 10: Starting HealthyRizz service..."
systemctl daemon-reload
systemctl enable healthyrizz
systemctl restart healthyrizz

# Step 11: Check service status
echo ""
echo "Step 11: Checking service status..."
sleep 3
if systemctl is-active --quiet healthyrizz; then
    echo "✅ HealthyRizz service is running successfully!"
    echo "🌐 Application should be available at: http://healthyrizz.in:8090"
    echo "🔧 Configure CloudPanel to proxy healthyrizz.in to localhost:8090"
else
    echo "❌ HealthyRizz service failed to start"
    echo "Checking service status..."
    systemctl status healthyrizz
    echo ""
    echo "Checking logs..."
    journalctl -u healthyrizz --no-pager -n 20
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Configure CloudPanel to proxy healthyrizz.in to localhost:8090"
echo "2. Update email and payment credentials in .env file"
echo "3. Set up SSL certificate for HTTPS"
echo ""
echo "Service management commands:"
echo "- View logs: journalctl -u healthyrizz -f"
echo "- Restart: systemctl restart healthyrizz"
echo "- Status: systemctl status healthyrizz"
echo "- Stop: systemctl stop healthyrizz" 