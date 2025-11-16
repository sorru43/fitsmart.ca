#!/bin/bash

# Fix Virtual Environment Setup for CloudPanel
# This script properly creates and configures the virtual environment

set -e

PROJECT_DIR="/home/fitsmart/htdocs/www.fitsmart.ca"

echo "=========================================="
echo "Fixing Virtual Environment Setup"
echo "=========================================="
echo ""

cd "$PROJECT_DIR"

# Remove old venv if it exists
if [ -d "venv" ]; then
    echo "⚠️  Removing old virtual environment..."
    rm -rf venv
fi

# Check if python3-full is installed
if ! dpkg -l | grep -q python3-full; then
    echo "📦 Installing python3-full..."
    apt-get update
    apt-get install -y python3-full python3-venv
fi

# Create new virtual environment
echo "🔧 Creating new virtual environment..."
python3 -m venv venv --system-site-packages

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip using the venv's pip
echo "📦 Upgrading pip..."
venv/bin/pip install --upgrade pip

# Verify we're using the right pip
echo ""
echo "📍 Python location: $(which python)"
echo "📍 Pip location: $(which pip)"
echo ""

# Install requirements using venv's pip
echo "📦 Installing requirements..."
venv/bin/pip install -r requirements.txt

echo ""
echo "✅ Virtual environment setup complete!"
echo ""
echo "To activate in the future, run:"
echo "  source venv/bin/activate"
echo ""

