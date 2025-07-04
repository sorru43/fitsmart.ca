#!/bin/bash

# Script to manually set up a Python 3.12 environment for HealthyRizz
# This script handles the special requirements for Python 3.12 on Ubuntu 24.04

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Python 3.12 environment for HealthyRizz...${NC}"

# Install prerequisites
echo -e "${YELLOW}Installing required packages...${NC}"
apt update
apt install -y python3-pip python3-dev python3-wheel python3-venv virtualenv postgresql-client

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "app.py" ]; then
    echo -e "${RED}Error: This doesn't appear to be the HealthyRizz directory.${NC}"
    echo "Please run this script from the HealthyRizz project directory."
    exit 1
fi

# Set up virtual environment
echo -e "${YELLOW}Setting up virtual environment...${NC}"

if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Remove it? (y/n)${NC}"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment."
    fi
fi

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Trying to create virtual environment with Python 3.12...${NC}"
    
    # Try different methods to create a venv
    if python3 -m venv venv; then
        echo -e "${GREEN}Virtual environment created successfully with python3 -m venv${NC}"
    elif virtualenv -p python3 venv; then
        echo -e "${GREEN}Virtual environment created successfully with virtualenv${NC}"
    else
        echo -e "${RED}Failed to create virtual environment with standard methods.${NC}"
        echo "Trying with pip..."
        
        pip3 install virtualenv
        virtualenv -p python3 venv || {
            echo -e "${RED}All methods to create virtual environment failed.${NC}"
            echo "Please check your Python installation and try again."
            exit 1
        }
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate || {
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
}

# Verify Python version in the virtual environment
PYTHON_VERSION=$(python --version)
echo -e "${GREEN}Using: $PYTHON_VERSION${NC}"

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install wheel

# Install required packages
echo -e "${YELLOW}Installing required packages...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install flask flask-sqlalchemy flask-wtf cryptography email-validator \
        flask-limiter flask-mail fpdf gunicorn pandas psycopg2-binary python-dotenv \
        sendgrid stripe twilio
fi

echo -e "${GREEN}Setup complete!${NC}"
echo "You can now:"
echo "1. Edit the .env file with your database credentials"
echo "2. Run database migrations:"
echo "   python -c \"import logging; logging.basicConfig(level=logging.DEBUG); from migrations import run_migrations; run_migrations()\""
echo "3. Start the application:"
echo "   gunicorn --workers 3 --bind 0.0.0.0:8090 --timeout 120 main:app"
echo
echo "For more help, see HOSTINGER_QUICKSTART.md"
