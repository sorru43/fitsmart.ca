#!/bin/bash

# Script to restart Gunicorn server on port 9000

echo "🔄 Restarting Gunicorn server..."

# Find and kill existing Gunicorn processes on port 9000
echo "📋 Checking for existing processes on port 9000..."

# Method 1: Using lsof
if command -v lsof &> /dev/null; then
    PID=$(lsof -ti:9000)
    if [ -n "$PID" ]; then
        echo "⚠️  Found process $PID using port 9000"
        kill -9 $PID
        echo "✅ Killed process $PID"
        sleep 2
    else
        echo "✅ No process found on port 9000"
    fi
fi

# Method 2: Using fuser (alternative)
if command -v fuser &> /dev/null && [ -z "$PID" ]; then
    fuser -k 9000/tcp 2>/dev/null
    sleep 2
fi

# Method 3: Find Gunicorn processes by name
echo "📋 Checking for Gunicorn processes..."
GUNICORN_PIDS=$(pgrep -f "gunicorn.*9000")
if [ -n "$GUNICORN_PIDS" ]; then
    echo "⚠️  Found Gunicorn processes: $GUNICORN_PIDS"
    pkill -f "gunicorn.*9000"
    echo "✅ Killed Gunicorn processes"
    sleep 2
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Start Gunicorn
echo "🚀 Starting Gunicorn on port 9000..."
venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app

