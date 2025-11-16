#!/bin/bash

# Quick script to kill existing Gunicorn and restart

echo "🛑 Stopping existing Gunicorn processes..."

# Kill all Gunicorn processes
pkill -f "gunicorn.*wsgi:app" || pkill -f gunicorn

# Wait a moment
sleep 2

# Kill any process on port 9000
if command -v lsof &> /dev/null; then
    lsof -ti:9000 | xargs kill -9 2>/dev/null
fi

if command -v fuser &> /dev/null; then
    fuser -k 9000/tcp 2>/dev/null
fi

echo "✅ Stopped existing processes"
echo ""
echo "🚀 Starting Gunicorn..."

# Activate venv and start
source venv/bin/activate
venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app

