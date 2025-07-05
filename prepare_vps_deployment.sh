#!/bin/bash

# Prepare HealthyRizz for VPS Deployment
echo "🚀 Preparing HealthyRizz for VPS Deployment..."

# Create deployment package directory
mkdir -p healthyrizz_vps_deploy

# Copy essential files
echo "📁 Copying application files..."
cp -r routes/ healthyrizz_vps_deploy/
cp -r templates/ healthyrizz_vps_deploy/
cp -r static/ healthyrizz_vps_deploy/
cp -r forms/ healthyrizz_vps_deploy/
cp -r utils/ healthyrizz_vps_deploy/
cp -r migrations/ healthyrizz_vps_deploy/ 2>/dev/null || echo "No migrations directory found"

# Copy core Python files
cp main.py healthyrizz_vps_deploy/
cp app.py healthyrizz_vps_deploy/ 2>/dev/null || echo "No app.py found"
cp config.py healthyrizz_vps_deploy/
cp models.py healthyrizz_vps_deploy/
cp extensions.py healthyrizz_vps_deploy/
cp run.py healthyrizz_vps_deploy/ 2>/dev/null || echo "No run.py found"

# Copy deployment files
cp deploy_healthyrizz_vps.sh healthyrizz_vps_deploy/
cp VPS_DEPLOYMENT_GUIDE.md healthyrizz_vps_deploy/
cp requirements.txt healthyrizz_vps_deploy/
cp env_template.txt healthyrizz_vps_deploy/

# Copy configuration files
cp -r config/ healthyrizz_vps_deploy/ 2>/dev/null || echo "No config directory found"

# Create a simple requirements.txt for VPS if it doesn't exist
if [ ! -f requirements.txt ]; then
    echo "📦 Creating requirements.txt..."
    cat > healthyrizz_vps_deploy/requirements.txt << 'EOF'
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-Login==0.6.3
Flask-WTF==1.1.1
Flask-Limiter==3.5.0
WTForms==3.0.1
Werkzeug==2.3.7
Jinja2==3.1.2
email-validator==2.0.0
psycopg2-binary==2.9.7
redis==5.0.0
gunicorn==21.2.0
python-dotenv==1.0.0
bcrypt==4.0.1
cryptography==41.0.4
itsdangerous==2.1.2
MarkupSafe==2.1.3
click==8.1.7
greenlet==2.0.2
SQLAlchemy==2.0.20
alembic==1.12.0
Mako==1.2.4
blinker==1.6.2
limits==3.6.0
packaging==23.1
typing_extensions==4.8.0
EOF
fi

# Create .env template
echo "⚙️ Creating environment template..."
cat > healthyrizz_vps_deploy/.env.template << 'EOF'
# Flask Configuration
FLASK_APP=main.py
FLASK_ENV=production
SECRET_KEY=your_secret_key_here

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://healthyrizz:your_password@localhost/healthyrizz

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Admin Configuration
ADMIN_EMAIL=admin@healthyrizz.in
ADMIN_PASSWORD=admin123

# Security Configuration
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
WTF_CSRF_ENABLED=True

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
RATELIMIT_DEFAULT=200 per day

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Payment Configuration (Optional)
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
EOF

# Create README for deployment
echo "📝 Creating deployment README..."
cat > healthyrizz_vps_deploy/README.md << 'EOF'
# HealthyRizz VPS Deployment Package

This package contains everything needed to deploy HealthyRizz on a VPS.

## Quick Deployment

1. Upload this entire folder to your VPS
2. Run the deployment script:
   ```bash
   chmod +x deploy_healthyrizz_vps.sh
   sudo ./deploy_healthyrizz_vps.sh
   ```

## Manual Setup

See `VPS_DEPLOYMENT_GUIDE.md` for detailed manual installation instructions.

## What's Included

- Complete HealthyRizz application
- Automated deployment script
- Configuration templates
- Comprehensive deployment guide
- Requirements and dependencies

## Default Admin Access

- Email: admin@healthyrizz.in
- Password: admin123

**Important**: Change the default password after first login!

## Support

For deployment issues, check the troubleshooting section in `VPS_DEPLOYMENT_GUIDE.md`.
EOF

# Create a simple check script
echo "🔍 Creating deployment check script..."
cat > healthyrizz_vps_deploy/check_deployment.sh << 'EOF'
#!/bin/bash

echo "=== HealthyRizz Deployment Check ==="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "✓ Running as root"
else
    echo "✗ Not running as root (required for deployment)"
    exit 1
fi

# Check system requirements
echo -e "\nSystem Requirements:"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2)
    echo "✓ Python 3: $PYTHON_VERSION"
else
    echo "✗ Python 3: Not installed"
fi

# Check pip
if command -v pip3 &> /dev/null; then
    echo "✓ pip3: Installed"
else
    echo "✗ pip3: Not installed"
fi

# Check disk space
DISK_SPACE=$(df / | awk 'NR==2{printf "%.1f", $4/1024/1024}')
echo "✓ Available disk space: ${DISK_SPACE}GB"

# Check memory
MEMORY=$(free -h | awk 'NR==2{printf "%.1f", $2}')
echo "✓ Total memory: ${MEMORY}"

echo -e "\nReady for deployment!"
echo "Run: sudo ./deploy_healthyrizz_vps.sh"
EOF

chmod +x healthyrizz_vps_deploy/check_deployment.sh

# Create archive
echo "📦 Creating deployment archive..."
tar -czf healthyrizz_vps_deploy.tar.gz healthyrizz_vps_deploy/

echo "✅ VPS deployment package created!"
echo ""
echo "📁 Package contents:"
echo "   • healthyrizz_vps_deploy/ - Complete deployment package"
echo "   • healthyrizz_vps_deploy.tar.gz - Compressed archive"
echo ""
echo "🚀 To deploy on your VPS:"
echo "   1. Upload healthyrizz_vps_deploy.tar.gz to your VPS"
echo "   2. Extract: tar -xzf healthyrizz_vps_deploy.tar.gz"
echo "   3. Run: cd healthyrizz_vps_deploy && sudo ./deploy_healthyrizz_vps.sh"
echo ""
echo "📖 For detailed instructions, see VPS_DEPLOYMENT_GUIDE.md" 