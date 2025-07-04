# PowerShell Script to Clean Up HealthyRizz Project
# This script will remove all test, deployment, and auxiliary files
# and keep only the essential application files

# Function to print status messages
function Write-Status {
    param([string]$Message)
    Write-Host "[+] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[x] $Message" -ForegroundColor Red
}

Write-Status "Starting project cleanup for HealthyRizz..."

# Create backup directory
$backupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir | Out-Null
Write-Status "Created backup directory: $backupDir"

# Files to keep (essential application files)
$filesToKeep = @(
    "main.py",
    "app.py", 
    "config.py",
    "models.py",
    "extensions.py",
    "blueprints.py",
    "requirements.txt",
    "run.py",
    "healthyrizz.db",
    "robots.txt",
    "sitemap.xml"
)

# Directories to keep
$dirsToKeep = @(
    "static",
    "templates", 
    "forms",
    "routes",
    "utils",
    "migrations",
    "instance"
)

# Move files to backup (except essential ones)
Write-Status "Moving non-essential files to backup..."

Get-ChildItem -File | Where-Object { 
    $filesToKeep -notcontains $_.Name -and 
    $_.Name -notlike "*.ps1" -and 
    $_.Name -notlike "*.sh" -and
    $_.Name -notlike "*.md" -and
    $_.Name -notlike "*.txt" -and
    $_.Name -notlike "*.py" -and
    $_.Name -notlike "*.db" -and
    $_.Name -notlike "*.xml" -and
    $_.Name -notlike "*.html"
} | ForEach-Object {
    Move-Item $_.FullName "$backupDir/"
    Write-Status "Moved $($_.Name) to backup"
}

# Move test files to backup
Get-ChildItem -File -Filter "test_*.py" | ForEach-Object {
    Move-Item $_.FullName "$backupDir/"
    Write-Status "Moved test file $($_.Name) to backup"
}

# Move deployment scripts to backup
Get-ChildItem -File -Filter "deploy*.sh" | ForEach-Object {
    Move-Item $_.FullName "$backupDir/"
    Write-Status "Moved deployment script $($_.Name) to backup"
}

Get-ChildItem -File -Filter "deploy*.ps1" | ForEach-Object {
    Move-Item $_.FullName "$backupDir/"
    Write-Status "Moved deployment script $($_.Name) to backup"
}

# Move utility scripts to backup
Get-ChildItem -File -Filter "*.py" | Where-Object {
    $_.Name -like "*test*" -or
    $_.Name -like "*debug*" -or
    $_.Name -like "*check*" -or
    $_.Name -like "*verify*" -or
    $_.Name -like "*update*" -or
    $_.Name -like "*reset*" -or
    $_.Name -like "*migrate*" -or
    $_.Name -like "*init*" -or
    $_.Name -like "*create*" -or
    $_.Name -like "*fix*" -or
    $_.Name -like "*clean*" -or
    $_.Name -like "*add_*" -or
    $_.Name -like "*generate*" -or
    $_.Name -like "*import*" -or
    $_.Name -like "*monitor*" -or
    $_.Name -like "*production*" -or
    $_.Name -like "*final*" -or
    $_.Name -like "*comprehensive*" -or
    $_.Name -like "*simple*" -or
    $_.Name -like "*contact_forms*" -or
    $_.Name -like "*commands*" -or
    $_.Name -like "*admin_video*"
} | ForEach-Object {
    Move-Item $_.FullName "$backupDir/"
    Write-Status "Moved utility file $($_.Name) to backup"
}

# Move documentation files to backup
Get-ChildItem -File -Filter "*.md" | ForEach-Object {
    Move-Item $_.FullName "$backupDir/"
    Write-Status "Moved documentation $($_.Name) to backup"
}

# Move environment template files to backup
Get-ChildItem -File -Filter "env_*.txt" | ForEach-Object {
    Move-Item $_.FullName "$backupDir/"
    Write-Status "Moved environment template $($_.Name) to backup"
}

# Move backup scripts to backup
Get-ChildItem -File -Filter "*backup*.sh" | ForEach-Object {
    Move-Item $_.FullName "$backupDir/"
    Write-Status "Moved backup script $($_.Name) to backup"
}

# Move auto backup script to backup
Get-ChildItem -File -Filter "auto_backup.sh" | ForEach-Object {
    Move-Item $_.FullName "$backupDir/"
    Write-Status "Moved auto backup script $($_.Name) to backup"
}

# Move test HTML file to backup
Get-ChildItem -File -Filter "test_*.html" | ForEach-Object {
    Move-Item $_.FullName "$backupDir/"
    Write-Status "Moved test HTML $($_.Name) to backup"
}

# Remove old database file
if (Test-Path "fitsmart.db") {
    Remove-Item "fitsmart.db" -Force
    Write-Status "Removed old fitsmart.db"
}

# Remove __pycache__ directory
if (Test-Path "__pycache__") {
    Remove-Item "__pycache__" -Recurse -Force
    Write-Status "Removed __pycache__ directory"
}

# Remove flask_session directory
if (Test-Path "flask_session") {
    Remove-Item "flask_session" -Recurse -Force
    Write-Status "Removed flask_session directory"
}

# Remove backups directory (since we're creating a clean backup)
if (Test-Path "backups") {
    Remove-Item "backups" -Recurse -Force
    Write-Status "Removed old backups directory"
}

Write-Status "Project cleanup completed successfully!"
Write-Host ""
Write-Status "Files kept:"
$filesToKeep | ForEach-Object { Write-Host "  - $_" -ForegroundColor Cyan }
Write-Host ""
Write-Status "Directories kept:"
$dirsToKeep | ForEach-Object { Write-Host "  - $_" -ForegroundColor Cyan }
Write-Host ""
Write-Status "Backup created at: $backupDir"
Write-Host ""
Write-Status "Next steps:"
Write-Status "1. Review the remaining files"
Write-Status "2. Test the application to ensure it still works"
Write-Status "3. Create new deployment scripts as needed"
Write-Status "4. Update requirements.txt if needed" 