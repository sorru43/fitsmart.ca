@echo off
echo 🏥 HealthyRizz - Starting Application...
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "main.py" (
    if not exist "app.py" (
        echo ❌ main.py or app.py not found
        echo Please run this script from the HealthyRizz directory
        pause
        exit /b 1
    )
)

REM Kill any existing Python processes (optional)
echo 🔧 Checking for existing processes...
taskkill /F /IM python.exe >nul 2>&1

REM Start the application
echo 🚀 Starting HealthyRizz...
python start_app_windows.py

pause 