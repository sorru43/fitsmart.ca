# HealthyRizz - PowerShell Startup Script
Write-Host "🏥 HealthyRizz - Starting Application..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python and add it to PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "main.py") -and -not (Test-Path "app.py")) {
    Write-Host "❌ main.py or app.py not found" -ForegroundColor Red
    Write-Host "Please run this script from the HealthyRizz directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Kill any existing Python processes
Write-Host "🔧 Checking for existing processes..." -ForegroundColor Yellow
try {
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "✅ Killed existing Python processes" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ No existing Python processes found" -ForegroundColor Blue
}

# Start the application
Write-Host "🚀 Starting HealthyRizz..." -ForegroundColor Green
try {
    python start_app_windows.py
} catch {
    Write-Host "❌ Failed to start application: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Make sure Python is installed and in PATH" -ForegroundColor White
    Write-Host "2. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "3. Check database configuration" -ForegroundColor White
    Write-Host "4. Ensure all required files are present" -ForegroundColor White
}

Read-Host "Press Enter to exit" 