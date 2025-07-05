#!/bin/bash
# Minimal deployment script for HealthyRizz (Ubuntu/Linux)
# Usage: bash deploy_healthyrizz.sh

set -e

APP_NAME="healthyrizz"
APP_DIR=$(pwd)
VENV_DIR="$APP_DIR/venv"
REQUIREMENTS_FILE="requirements.txt"
GUNICORN_PORT=8090

# 1. Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Activate virtual environment
source "$VENV_DIR/bin/activate"

# 3. Upgrade pip and install requirements
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

# 4. Run migrations (if using Flask-Migrate/Alembic)
if [ -d "migrations" ]; then
    echo "[+] Running database migrations..."
    flask db upgrade || echo "[!] Skipped migrations (no Flask-Migrate setup)"
fi

# 5. Start Gunicorn
if ! command -v gunicorn &> /dev/null; then
    pip install gunicorn
fi

echo "[+] Starting Gunicorn on port $GUNICORN_PORT..."
gunicorn -w 4 -b 0.0.0.0:$GUNICORN_PORT main:app 