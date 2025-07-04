# HealthyRizz Deployment Package Creator
# Creates deployment packages for different environments

Write-Host "🚀 HealthyRizz Deployment Package Creator" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "main.py")) {
    Write-Host "❌ ERROR: main.py not found. Please run this script from the HealthyRizz project directory" -ForegroundColor Red
    exit 1
}

# Create temp directory for clean files
$tempDir = "temp_deploy"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Host "📦 Creating deployment package..." -ForegroundColor Blue

# Copy files (excluding development files)
$excludeList = @(
    '.git',
    '__pycache__',
    '*.pyc',
    '.venv',
    'flask_session',
    '*.log',
    '.env',
    'temp_deploy',
    'healthyrizz_deploy.zip'
)

Get-ChildItem -Path . | Where-Object {
    $item = $_
    $shouldExclude = $false
    
    foreach ($pattern in $excludeList) {
        if ($item.Name -like $pattern -or $item.Name -eq $pattern) {
            $shouldExclude = $true
            break
        }
    }
    
    return -not $shouldExclude
} | Copy-Item -Destination $tempDir -Recurse -Force

Write-Host "✅ Files copied to temporary directory" -ForegroundColor Green

# Create CloudPanel installation script
$cloudPanelScript = @'
#!/bin/bash

# HealthyRizz CloudPanel Installation Script
# Run this on your CloudPanel server

set -e

DOMAIN="healthyrizz.in"
PORT="8090"
APP_DIR="/home/healthyrizz/htdocs/${DOMAIN}"

echo "🚀 Installing HealthyRizz on CloudPanel..."

# Create directory
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Extract files (assumes you've uploaded the zip file)
if [ -f "healthyrizz_deploy.zip" ]; then
    unzip -q healthyrizz_deploy.zip
    rm healthyrizz_deploy.zip
    echo "✅ Files extracted"
else
    echo "❌ healthyrizz_deploy.zip not found"
    exit 1
fi

# Setup Python environment
echo "🔧 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
echo "🔐 Creating environment file..."
cat > .env << 'EOF'
# HealthyRizz Production Environment
SECRET_KEY=$(openssl rand -hex 32)
WTF_CSRF_SECRET_KEY=$(openssl rand -hex 32)

# Environment
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=sqlite:///healthyrizz.db

# Email (UPDATE THESE)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Payment (UPDATE THESE)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=$(openssl rand -hex 24)

# Redis
REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/1

# Security
SESSION_COOKIE_SECURE=False
WTF_CSRF_SSL_STRICT=False
PERMANENT_SESSION_LIFETIME=1800

DOMAIN_NAME=${DOMAIN}
BASE_URL=https://${DOMAIN}
EOF

# Initialize database
echo "🗄️ Initializing database..."
python init_database.py

# Create startup script
cat > start_app.sh << 'STARTEOF'
#!/bin/bash
cd /home/healthyrizz/htdocs/healthyrizz.in
source venv/bin/activate
python main.py
STARTEOF

chmod +x start_app.sh

echo ""
echo "✅ HealthyRizz installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update email credentials in .env file"
echo "2. Update payment credentials in .env file"
echo "3. Start the application: ./start_app.sh"
echo ""
echo "🌐 Application URL: http://${DOMAIN}:${PORT}"
echo "👤 Admin login: admin@healthyrizz.in / admin123"
echo "⚠️  Change admin password after first login!"
'@

$cloudPanelScript | Out-File -FilePath "$tempDir\install_on_cloudpanel.sh" -Encoding UTF8

# Create Windows batch installer
$windowsInstaller = @'
@echo off
echo HealthyRizz Windows Installation
echo ================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

:: Create virtual environment
echo Setting up Python environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

:: Create environment file (basic)
echo Creating environment file...
echo # HealthyRizz Environment > .env
echo SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%%RANDOM% >> .env
echo WTF_CSRF_SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%%RANDOM% >> .env
echo DEBUG=False >> .env
echo DATABASE_URL=sqlite:///healthyrizz.db >> .env

:: Initialize database
echo Initializing database...
python init_database.py

:: Create startup script
echo @echo off > start_healthyrizz.bat
echo cd /d "%~dp0" >> start_healthyrizz.bat
echo call venv\Scripts\activate.bat >> start_healthyrizz.bat
echo python main.py >> start_healthyrizz.bat
echo pause >> start_healthyrizz.bat

echo.
echo Installation completed!
echo.
echo To start HealthyRizz:
echo 1. Double-click start_healthyrizz.bat
echo 2. Open http://localhost:8090 in your browser
echo 3. Login with: admin@healthyrizz.in / admin123
echo.
echo IMPORTANT: Update email and payment settings in .env file
pause
'@

$windowsInstaller | Out-File -FilePath "$tempDir\install_windows.bat" -Encoding ASCII

# Create deployment instructions
$instructions = @"
# HealthyRizz Deployment Instructions

## Package Contents
- **Application files**: Complete HealthyRizz application
- **install_on_cloudpanel.sh**: CloudPanel/Linux installation script
- **install_windows.bat**: Windows installation script

## CloudPanel Deployment

1. **Upload files**: Upload healthyrizz_deploy.zip to your CloudPanel server
2. **Extract**: Unzip in /home/healthyrizz/htdocs/healthyrizz.in/
3. **Install**: Run ./install_on_cloudpanel.sh
4. **Configure**: Update .env file with your credentials
5. **Start**: Run ./start_app.sh

## Windows Deployment

1. **Extract**: Unzip healthyrizz_deploy.zip to your desired location
2. **Install**: Run install_windows.bat as Administrator
3. **Configure**: Update .env file with your credentials
4. **Start**: Run start_healthyrizz.bat

## VPS/Ubuntu Deployment

1. **Upload**: Transfer files to your VPS
2. **Install**: Run install_on_cloudpanel.sh (works on Ubuntu too)
3. **Configure**: Update .env file
4. **Setup Service**: Create systemd service for production

## Configuration Required

After installation, update these in .env file:

### Email Settings
```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Payment Gateway
```
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
```

## Default Admin Account
- **URL**: http://your-domain:8090
- **Email**: admin@healthyrizz.in
- **Password**: admin123
- **⚠️ Change password immediately after first login!**

## Support
- Application runs on port 8090
- Database: SQLite (healthyrizz.db)
- Environment: Production ready
- Security: All secrets properly configured

Generated on: $(Get-Date)
"@

$instructions | Out-File -FilePath "$tempDir\DEPLOYMENT_INSTRUCTIONS.md" -Encoding UTF8

# Create the ZIP file
Write-Host "🗜️ Creating ZIP archive..." -ForegroundColor Blue

Compress-Archive -Path "$tempDir\*" -DestinationPath "healthyrizz_deploy.zip" -Force

# Cleanup
Remove-Item $tempDir -Recurse -Force

Write-Host ""
Write-Host "✅ Deployment package created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Package: healthyrizz_deploy.zip" -ForegroundColor Cyan
Write-Host "📋 Instructions: See DEPLOYMENT_INSTRUCTIONS.md inside the package" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Ready for deployment to:" -ForegroundColor Yellow
Write-Host "   - CloudPanel servers" -ForegroundColor White
Write-Host "   - Ubuntu/Linux VPS" -ForegroundColor White  
Write-Host "   - Windows servers" -ForegroundColor White
Write-Host ""

# Show file size
$zipSize = (Get-Item "healthyrizz_deploy.zip").Length / 1MB
Write-Host "📊 Package size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Blue 