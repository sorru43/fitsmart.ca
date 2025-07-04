# PowerShell Script to rename all healthyrizz references to healthyrizz
# This script will update file names, database names, service names, and content references

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

Write-Status "Starting rename process from healthyrizz to healthyrizz..."

# 1. Rename files and directories
Write-Status "Renaming files and directories..."

# Rename main files
if (Test-Path "healthyrizz.db") {
    Rename-Item "healthyrizz.db" "healthyrizz.db"
    Write-Status "Renamed healthyrizz.db to healthyrizz.db"
}

if (Test-Path "healthyrizz.service") {
    Rename-Item "healthyrizz.service" "healthyrizz.service"
    Write-Status "Renamed healthyrizz.service to healthyrizz.service"
}

# Rename deployment scripts
Get-ChildItem -Name "deploy_healthyrizz*.sh" | ForEach-Object {
    $newName = $_ -replace "healthyrizz", "healthyrizz"
    Rename-Item $_ $newName
    Write-Status "Renamed $_ to $newName"
}

Get-ChildItem -Name "deploy_healthyrizz*.ps1" | ForEach-Object {
    $newName = $_ -replace "healthyrizz", "healthyrizz"
    Rename-Item $_ $newName
    Write-Status "Renamed $_ to $newName"
}

# Rename test files
Get-ChildItem -Name "test_*healthyrizz*.py" | ForEach-Object {
    $newName = $_ -replace "healthyrizz", "healthyrizz"
    Rename-Item $_ $newName
    Write-Status "Renamed $_ to $newName"
}

# Rename config files
Get-ChildItem -Name "*healthyrizz*.conf" | ForEach-Object {
    $newName = $_ -replace "healthyrizz", "healthyrizz"
    Rename-Item $_ $newName
    Write-Status "Renamed $_ to $newName"
}

Get-ChildItem -Name "*healthyrizz*.txt" | ForEach-Object {
    $newName = $_ -replace "healthyrizz", "healthyrizz"
    Rename-Item $_ $newName
    Write-Status "Renamed $_ to $newName"
}

# 2. Update content in Python files
Write-Status "Updating content in Python files..."

Get-ChildItem -Recurse -Filter "*.py" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    $content = $content -replace "healthyrizz", "HEALTHYRIZZ"
    Set-Content $_.FullName $content -NoNewline
}

# 3. Update content in configuration files
Write-Status "Updating content in configuration files..."

# Update .env files
Get-ChildItem -Recurse -Filter ".env*" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content $_.FullName $content -NoNewline
}

# Update requirements files
Get-ChildItem -Recurse -Filter "requirements*.txt" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    Set-Content $_.FullName $content -NoNewline
}

# Update config files
Get-ChildItem -Recurse -Filter "*.conf" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    Set-Content $_.FullName $content -NoNewline
}

Get-ChildItem -Recurse -Filter "*.cfg" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    Set-Content $_.FullName $content -NoNewline
}

# 4. Update HTML templates
Write-Status "Updating content in HTML templates..."

Get-ChildItem -Recurse -Filter "*.html" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content $_.FullName $content -NoNewline
}

# 5. Update JavaScript files
Write-Status "Updating content in JavaScript files..."

Get-ChildItem -Recurse -Filter "*.js" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content $_.FullName $content -NoNewline
}

# 6. Update CSS files
Write-Status "Updating content in CSS files..."

Get-ChildItem -Recurse -Filter "*.css" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content $_.FullName $content -NoNewline
}

# 7. Update documentation files
Write-Status "Updating content in documentation files..."

Get-ChildItem -Recurse -Filter "*.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content $_.FullName $content -NoNewline
}

Get-ChildItem -Recurse -Filter "*.txt" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content $_.FullName $content -NoNewline
}

# 8. Update JSON files
Write-Status "Updating content in JSON files..."

Get-ChildItem -Recurse -Filter "*.json" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content $_.FullName $content -NoNewline
}

# 9. Update shell scripts
Write-Status "Updating content in shell scripts..."

Get-ChildItem -Recurse -Filter "*.sh" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content $_.FullName $content -NoNewline
}

# 10. Update PowerShell scripts
Write-Status "Updating content in PowerShell scripts..."

Get-ChildItem -Recurse -Filter "*.ps1" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content $_.FullName $content -NoNewline
}

# 11. Update specific database references
Write-Status "Updating database references..."

# Update config.py specifically
if (Test-Path "config.py") {
    $content = Get-Content "config.py" -Raw
    $content = $content -replace "healthyrizz\.db", "healthyrizz.db"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content "config.py" $content -NoNewline
    Write-Status "Updated config.py"
}

# Update main.py specifically
if (Test-Path "main.py") {
    $content = Get-Content "main.py" -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content "main.py" $content -NoNewline
    Write-Status "Updated main.py"
}

# Update app.py specifically
if (Test-Path "app.py") {
    $content = Get-Content "app.py" -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content "app.py" $content -NoNewline
    Write-Status "Updated app.py"
}

# 12. Update service files
Write-Status "Updating service files..."

if (Test-Path "healthyrizz.service") {
    $content = Get-Content "healthyrizz.service" -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content "healthyrizz.service" $content -NoNewline
    Write-Status "Updated healthyrizz.service"
}

# 13. Update nginx configurations
Write-Status "Updating nginx configurations..."

Get-ChildItem -Recurse -Filter "*nginx*" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content $_.FullName $content -NoNewline
}

# 14. Update manifest.json for PWA
Write-Status "Updating PWA manifest..."

if (Test-Path "static/manifest.json") {
    $content = Get-Content "static/manifest.json" -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content "static/manifest.json" $content -NoNewline
    Write-Status "Updated PWA manifest"
}

# 15. Update robots.txt
Write-Status "Updating robots.txt..."

if (Test-Path "robots.txt") {
    $content = Get-Content "robots.txt" -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content "robots.txt" $content -NoNewline
    Write-Status "Updated robots.txt"
}

# 16. Update sitemap.xml
Write-Status "Updating sitemap.xml..."

if (Test-Path "sitemap.xml") {
    $content = Get-Content "sitemap.xml" -Raw
    $content = $content -replace "healthyrizz", "healthyrizz"
    $content = $content -replace "healthyrizz", "HealthyRizz"
    Set-Content "sitemap.xml" $content -NoNewline
    Write-Status "Updated sitemap.xml"
}

Write-Status "Rename process completed successfully!"
Write-Host ""
Write-Status "Summary of changes:"
Write-Status "- All file names containing 'healthyrizz' have been renamed to 'healthyrizz'"
Write-Status "- All content references have been updated"
Write-Status "- Database names updated to use 'healthyrizz'"
Write-Status "- Service names updated to use 'healthyrizz'"
Write-Status "- Configuration files updated"
Write-Host ""
Write-Status "Next steps:"
Write-Status "1. Review the changes to ensure everything is correct"
Write-Status "2. Test the application to make sure it still works"
Write-Status "3. Update any external references or documentation"
Write-Status "4. Commit the changes to your version control system" 