# HealthyRizz Windows Deployment Script
# PowerShell script for deploying on Windows servers/IIS
# Version: 1.0

param(
    [string]$Domain = "healthyrizz.in",
    [int]$Port = 8090,
    [string]$DeployPath = "C:\inetpub\wwwroot\healthyrizz",
    [switch]$Help
)

if ($Help) {
    Write-Host @"
HealthyRizz Windows Deployment Script

Usage: .\deploy_healthyrizz_windows.ps1 [options]

Options:
  -Domain <string>     Domain name (default: healthyrizz.in)
  -Port <int>          Port number (default: 8090)
  -DeployPath <string> Deployment directory (default: C:\inetpub\wwwroot\healthyrizz)
  -Help               Show this help message

Example:
  .\deploy_healthyrizz_windows.ps1 -Domain "mysite.com" -Port 5000
"@
    exit 0
}

# Colors for output
function Write-Success($Message) {
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error($Message) {
    Write-Host "❌ ERROR: $Message" -ForegroundColor Red
    exit 1
}

function Write-Warning($Message) {
    Write-Host "⚠️  WARNING: $Message" -ForegroundColor Yellow
}

function Write-Info($Message) {
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Step($Message) {
    Write-Host "🔧 $Message" -ForegroundColor Blue
}

Write-Host "🚀 HealthyRizz Windows Deployment Script" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Magenta

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
}

# Check if Python is installed
Write-Step "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        Write-Success "Found $pythonVersion"
    } else {
        Write-Error "Python not found. Please install Python 3.8 or higher"
    }
} catch {
    Write-Error "Python not found. Please install Python 3.8 or higher"
}

# Check if we're in the right directory
if (-not (Test-Path "main.py")) {
    Write-Error "main.py not found. Please run this script from the HealthyRizz project directory"
}

Write-Info "Deployment Configuration:"
Write-Info "  Domain: $Domain"
Write-Info "  Port: $Port"
Write-Info "  Deploy Path: $DeployPath"
Write-Info ""

$confirmation = Read-Host "Continue with deployment? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Info "Deployment cancelled"
    exit 0
}

# Create deployment directory
Write-Step "Creating deployment directory..."
if (Test-Path $DeployPath) {
    $backup = "${DeployPath}_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Info "Backing up existing installation to: $backup"
    Move-Item $DeployPath $backup
}

New-Item -ItemType Directory -Path $DeployPath -Force | Out-Null
Write-Success "Deployment directory created: $DeployPath"

# Copy application files
Write-Step "Copying application files..."
$excludePatterns = @('.git', '__pycache__', '*.pyc', '.venv', 'flask_session', '*.log', '.env')

Get-ChildItem -Path . | Where-Object {
    $item = $_
    $shouldExclude = $false
    foreach ($pattern in $excludePatterns) {
        if ($item.Name -like $pattern) {
            $shouldExclude = $true
            break
        }
    }
    return -not $shouldExclude
} | Copy-Item -Destination $DeployPath -Recurse -Force

Write-Success "Application files copied successfully"

# Change to deployment directory
Set-Location $DeployPath

# Create virtual environment
Write-Step "Setting up Python virtual environment..."
python -m venv venv
if (Test-Path "venv\Scripts\activate.ps1") {
    & "venv\Scripts\activate.ps1"
    Write-Success "Virtual environment created and activated"
} else {
    Write-Error "Failed to create virtual environment"
}

# Install dependencies
Write-Step "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-Success "Dependencies installed successfully"

# Generate secure secrets
Write-Step "Generating secure environment configuration..."
$secretKey = -join ((1..64) | ForEach-Object { '{0:X}' -f (Get-Random -Maximum 16) })
$csrfKey = -join ((1..64) | ForEach-Object { '{0:X}' -f (Get-Random -Maximum 16) })
$webhookSecret = -join ((1..48) | ForEach-Object { '{0:X}' -f (Get-Random -Maximum 16) })

# Create .env file
$envContent = @"
# HealthyRizz Windows Production Environment
# Generated on $(Get-Date)

# Security Keys
SECRET_KEY=$secretKey
WTF_CSRF_SECRET_KEY=$csrfKey

# Environment
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=sqlite:///healthyrizz.db

# Email Configuration (UPDATE WITH REAL VALUES)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Payment Configuration (UPDATE WITH REAL VALUES)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=$webhookSecret

# Redis (if available)
REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/1

# Security Settings
SESSION_COOKIE_SECURE=False
WTF_CSRF_SSL_STRICT=False
PERMANENT_SESSION_LIFETIME=1800

# Domain Configuration
DOMAIN_NAME=$Domain
BASE_URL=https://$Domain
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Success "Environment file created"

# Initialize database
Write-Step "Initializing database..."
try {
    python init_database.py
    Write-Success "Database initialized successfully"
} catch {
    Write-Warning "Database initialization failed. You may need to run it manually."
}

# Create startup scripts
Write-Step "Creating startup scripts..."

# Create batch file for starting the application
$startBatch = @"
@echo off
cd /d "$DeployPath"
call venv\Scripts\activate.bat
python main.py
pause
"@

$startBatch | Out-File -FilePath "start_healthyrizz.bat" -Encoding ASCII

# Create PowerShell startup script
$startPS = @"
# HealthyRizz Startup Script
Set-Location "$DeployPath"
& "venv\Scripts\activate.ps1"
python main.py
"@

$startPS | Out-File -FilePath "start_healthyrizz.ps1" -Encoding UTF8

Write-Success "Startup scripts created"

# Create IIS configuration (if IIS is available)
if (Get-WindowsFeature -Name "IIS-WebServer" -ErrorAction SilentlyContinue) {
    Write-Step "Creating IIS configuration..."
    
    $webConfig = @"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="httpPlatformHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified" />
    </handlers>
    <httpPlatform processPath="$DeployPath\venv\Scripts\python.exe"
                  arguments="$DeployPath\main.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="$DeployPath\logs\stdout.log"
                  startupTimeLimit="60"
                  requestTimeout="23:00:00">
      <environmentVariables>
        <environmentVariable name="PYTHONPATH" value="$DeployPath" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
"@
    
    $webConfig | Out-File -FilePath "web.config" -Encoding UTF8
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    
    Write-Success "IIS configuration created"
}

# Create Windows Service script (optional)
$serviceScript = @"
# Install HealthyRizz as Windows Service
# Run this script as Administrator

`$serviceName = "HealthyRizz"
`$serviceDisplayName = "HealthyRizz Web Application"
`$servicePath = "$DeployPath\venv\Scripts\python.exe"
`$serviceArgs = "$DeployPath\main.py"

# Install NSSM (Non-Sucking Service Manager) first
# Download from: https://nssm.cc/download

# Then run:
# nssm install `$serviceName `$servicePath `$serviceArgs
# nssm set `$serviceName AppDirectory "$DeployPath"
# nssm set `$serviceName DisplayName "`$serviceDisplayName"
# nssm start `$serviceName

Write-Host "To install as Windows Service:"
Write-Host "1. Download NSSM from https://nssm.cc/download"
Write-Host "2. Extract nssm.exe to a directory in your PATH"
Write-Host "3. Run the commands above in an Administrator PowerShell"
"@

$serviceScript | Out-File -FilePath "install_service.ps1" -Encoding UTF8

# Create deployment summary
$summary = @"
# HealthyRizz Windows Deployment Summary

## Deployment Information
- **Date**: $(Get-Date)
- **Domain**: $Domain
- **Port**: $Port
- **Installation Path**: $DeployPath
- **Python Environment**: $DeployPath\venv

## Files Created
- **Environment Config**: .env
- **Startup Scripts**: start_healthyrizz.bat, start_healthyrizz.ps1
- **IIS Config**: web.config (if IIS available)
- **Service Script**: install_service.ps1

## Starting the Application

### Option 1: Direct Start
1. Double-click: start_healthyrizz.bat
2. Or run: .\start_healthyrizz.ps1

### Option 2: Manual Start
1. Open PowerShell as Administrator
2. Navigate to: $DeployPath
3. Activate environment: venv\Scripts\activate.ps1
4. Start application: python main.py

### Option 3: Windows Service
1. Install NSSM from https://nssm.cc/download
2. Run: .\install_service.ps1 (follow instructions)

## Configuration Required
1. **Update .env file** with real credentials:
   - Email settings (MAIL_USERNAME, MAIL_PASSWORD)
   - Payment gateway (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)

2. **Admin Login**:
   - URL: http://$Domain`:$Port
   - Email: admin@healthyrizz.in
   - Password: admin123
   - **Change password immediately after first login!**

## Firewall Configuration
Make sure port $Port is open in Windows Firewall:
```
netsh advfirewall firewall add rule name="HealthyRizz" dir=in action=allow protocol=TCP localport=$Port
```

## Troubleshooting
- Check logs in: $DeployPath\logs\
- Python path: $DeployPath\venv\Scripts\python.exe
- Application path: $DeployPath\main.py

Generated on: $(Get-Date)
"@

$summary | Out-File -FilePath "DEPLOYMENT_SUMMARY.md" -Encoding UTF8

Write-Host ""
Write-Success "🎉 HealthyRizz Windows deployment completed successfully!"
Write-Host ""
Write-Info "📋 Deployment Summary:"
Write-Info "  Installation Path: $DeployPath"
Write-Info "  Application URL: http://$Domain`:$Port"
Write-Info "  Admin Login: admin@healthyrizz.in / admin123"
Write-Host ""
Write-Warning "⚠️  IMPORTANT NEXT STEPS:"
Write-Warning "  1. Update credentials in $DeployPath\.env"
Write-Warning "  2. Start the application using one of the startup scripts"
Write-Warning "  3. Change admin password after first login"
Write-Warning "  4. Configure firewall to allow port $Port"
Write-Host ""
Write-Info "📖 See DEPLOYMENT_SUMMARY.md for detailed instructions"

# Open deployment directory
$openDir = Read-Host "Open deployment directory in Explorer? (y/N)"
if ($openDir -eq 'y' -or $openDir -eq 'Y') {
    Start-Process explorer.exe -ArgumentList $DeployPath
} 