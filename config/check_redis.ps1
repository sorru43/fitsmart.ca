# PowerShell script to check Redis status

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

# Check if Redis is installed
$redisInstalled = Get-Command redis-cli -ErrorAction SilentlyContinue
if (-not $redisInstalled) {
    Write-ColorOutput Red "Redis is not installed. Please install Redis first."
    Write-ColorOutput Yellow "You can download Redis for Windows from: https://github.com/microsoftarchive/redis/releases"
    exit 1
}

# Check if Redis server is running
$redisRunning = Get-Process redis-server -ErrorAction SilentlyContinue
if (-not $redisRunning) {
    Write-ColorOutput Red "Redis server is not running."
    Write-ColorOutput Yellow "Starting Redis server..."
    Start-Process redis-server
    Start-Sleep -Seconds 2
}

# Test Redis connection
try {
    $result = redis-cli ping
    if ($result -eq "PONG") {
        Write-ColorOutput Green "✓ Redis is running and responding"
        Write-ColorOutput Green "✓ Redis connection test successful"
    }
    else {
        Write-ColorOutput Red "✗ Redis is not responding correctly"
        exit 1
    }
}
catch {
    Write-ColorOutput Red "✗ Failed to connect to Redis: $_"
    exit 1
} 