# HealthyRizz PWA Fix Deployment Script
# This script packages the PWA-related files that were missing

Write-Host "Creating HealthyRizz PWA Fix deployment package..." -ForegroundColor Green

# Create deployment directory
$deployDir = "healthyrizz_pwa_fix_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null

# Create static/js directory structure
New-Item -ItemType Directory -Path "$deployDir/static/js" -Force | Out-Null

# Copy the new PWA files
Copy-Item "static/js/register-sw.js" "$deployDir/static/js/" -Force
Copy-Item "static/js/service-worker.js" "$deployDir/static/js/" -Force
Copy-Item "routes_pwa.py" "$deployDir/" -Force

# Copy the updated main.py
Copy-Item "main.py" "$deployDir/" -Force

Write-Host "PWA Fix files packaged in: $deployDir" -ForegroundColor Green
Write-Host ""
Write-Host "Files included:" -ForegroundColor Yellow
Write-Host "- static/js/register-sw.js (Service worker registration)" -ForegroundColor White
Write-Host "- static/js/service-worker.js (Service worker for offline functionality)" -ForegroundColor White
Write-Host "- routes_pwa.py (PWA routes for service worker and manifest)" -ForegroundColor White
Write-Host "- main.py (Updated with PWA routes import)" -ForegroundColor White
Write-Host ""
Write-Host "Deployment instructions:" -ForegroundColor Cyan
Write-Host "1. Upload these files to your server" -ForegroundColor White
Write-Host "2. Restart your Flask application" -ForegroundColor White
Write-Host "3. The 404 error for register-sw.js should be resolved" -ForegroundColor White 