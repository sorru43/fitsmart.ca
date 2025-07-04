# PowerShell script to set up healthyrizz development environment

# Function to print colored messages
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Function to check command status
function Check-Status {
    param($SuccessMessage, $ErrorMessage)
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput Green "✓ $SuccessMessage"
    }
    else {
        Write-ColorOutput Red "✗ $ErrorMessage"
        exit 1
    }
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-ColorOutput Yellow "Creating virtual environment..."
    python -m venv venv
    Check-Status "Virtual environment created" "Failed to create virtual environment"
}

# Activate virtual environment
Write-ColorOutput Yellow "Activating virtual environment..."
.\venv\Scripts\Activate.ps1
Check-Status "Virtual environment activated" "Failed to activate virtual environment"

# Install required packages
Write-ColorOutput Yellow "Installing required packages..."
pip install -r requirements.txt
Check-Status "Packages installed" "Failed to install packages"

# Create .env file
Write-ColorOutput Yellow "Creating .env file..."
$envContent = @"
# Development Configuration
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URL=postgresql://healthyrizz:WZQEc3we3r4t5yuio0p]\- 0.@localhost:5432/healthyrizz
DATABASE_TEST_URL=postgresql://healthyrizz:WZQEc3we3r4t5yuio0p]\- 0.@localhost:5432/healthyrizz_test

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
RATELIMIT_STRATEGY=fixed-window
RATELIMIT_DEFAULT=200 per day
RATELIMIT_HEADERS_ENABLED=true
RATELIMIT_STORAGE_OPTIONS={"socket_timeout": 5}

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Stripe Configuration
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=your-aws-region
S3_BUCKET=your-s3-bucket
"@

$envContent | Out-File -FilePath .env -Encoding UTF8
Check-Status "Environment file created" "Failed to create environment file"

Write-ColorOutput Green "`nDevelopment environment setup completed!"
Write-ColorOutput Yellow "`nTo start the development server:"
Write-ColorOutput White "1. Make sure Redis is running"
Write-ColorOutput White "2. Run the application:"
Write-ColorOutput White "   python main.py" 