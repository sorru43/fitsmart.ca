# PowerShell script to create deployment package

Write-Host "Creating deployment package for healthyrizz..." -ForegroundColor Yellow

# Create a temporary directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$tempDir = "healthyrizz_deployment_$timestamp"
New-Item -ItemType Directory -Path $tempDir -Force

# Copy necessary files
Write-Host "Copying project files..."
$files = @(
    "app.py",
    "blueprints.py",
    "config.py",
    "deploy_healthyrizz.sh",
    "extensions.py",
    "forms.py",
    "main.py",
    "models.py",
    "requirements.txt",
    "reset_db.py",
    "routes.py",
    "routes_api.py",
    "routes_notifications.py",
    "routes_stripe.py",
    "static",
    "templates",
    "utils"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $tempDir -Recurse -Force
    }
}

# Create necessary directories
New-Item -ItemType Directory -Path "$tempDir/logs" -Force
New-Item -ItemType Directory -Path "$tempDir/backups" -Force

# Create deployment package
Write-Host "Creating deployment package..."
Compress-Archive -Path $tempDir -DestinationPath "healthyrizz_deployment.zip" -Force

# Clean up
Write-Host "Cleaning up..."
Remove-Item -Path $tempDir -Recurse -Force

Write-Host "Deployment package created: healthyrizz_deployment.zip" -ForegroundColor Green
Write-Host "To deploy:" -ForegroundColor Yellow
Write-Host "1. Upload healthyrizz_deployment.zip to your server"
Write-Host "2. Extract: unzip healthyrizz_deployment.zip"
Write-Host "3. Navigate to the extracted directory"
Write-Host "4. Run: ./deploy_healthyrizz.sh" 