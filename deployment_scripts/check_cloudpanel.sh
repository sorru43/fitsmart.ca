#!/bin/bash

# CloudPanel Environment Check Script
# This script validates the CloudPanel environment for HealthyRizz deployment
# Run this before deploying to ensure your environment is properly set up

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print header
echo "====================================================================="
echo "HealthyRizz CloudPanel Environment Check"
echo "====================================================================="
echo ""

# Check if clpctl is installed
echo -n "Checking CloudPanel installation: "
if command -v clpctl &> /dev/null; then
    echo -e "${GREEN}FOUND${NC}"
    CLPCTL_VERSION=$(clpctl --version 2>&1 | grep -oP 'CloudPanel CLI \K[0-9\.]+' || echo "Unknown")
    echo "CloudPanel CLI version: $CLPCTL_VERSION"
else
    echo -e "${RED}NOT FOUND${NC}"
    echo -e "${YELLOW}CloudPanel CLI (clpctl) is not installed or not in PATH.${NC}"
    echo "Please ensure CloudPanel is properly installed on this system."
    exit 1
fi

# Check web directory
echo -n "Checking web directory: "
if [ -d "/home/healthyrizz/htdocs" ]; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}NOT FOUND${NC}"
    echo -e "${YELLOW}Web directory /home/healthyrizz/htdocs does not exist.${NC}"
    echo "Please ensure the healthyrizz site is created in CloudPanel."
fi

# Check Python version
echo -n "Checking Python 3.11: "
if command -v python3.11 &> /dev/null; then
    echo -e "${GREEN}FOUND${NC}"
    PYTHON_VERSION=$(python3.11 --version)
    echo "Python version: $PYTHON_VERSION"
else
    echo -e "${RED}NOT FOUND${NC}"
    echo -e "${YELLOW}Python 3.11 is required but not installed.${NC}"
    echo "Please install Python 3.11:"
    echo "apt update && apt install python3.11 python3.11-venv python3.11-dev"
fi

# Check PostgreSQL
echo -n "Checking PostgreSQL: "
if command -v psql &> /dev/null; then
    echo -e "${GREEN}FOUND${NC}"
    PG_VERSION=$(psql --version | grep -oP 'psql \(PostgreSQL\) \K[0-9\.]+')
    echo "PostgreSQL version: $PG_VERSION"
else
    echo -e "${RED}NOT FOUND${NC}"
    echo -e "${YELLOW}PostgreSQL is required but not installed.${NC}"
    echo "Please install PostgreSQL:"
    echo "apt update && apt install postgresql postgresql-contrib"
fi

# Check if site exists in CloudPanel
echo -n "Checking if site exists in CloudPanel: "
if command -v clpctl &> /dev/null; then
    if clpctl site:list | grep -q "www.healthyrizz.ca"; then
        echo -e "${GREEN}FOUND${NC}"
    else
        echo -e "${YELLOW}NOT FOUND${NC}"
        echo "Site www.healthyrizz.ca is not configured in CloudPanel."
        echo "Please create the site in CloudPanel before deployment."
    fi
else
    echo -e "${YELLOW}SKIPPED${NC} (CloudPanel CLI not available)"
fi

# Check port 8090
echo -n "Checking port 8090 availability: "
if ! command -v nc &> /dev/null; then
    echo -e "${YELLOW}SKIPPED${NC} (netcat not installed)"
else
    if nc -z 127.0.0.1 8090 >/dev/null 2>&1; then
        echo -e "${YELLOW}IN USE${NC}"
        echo "Port 8090 is already in use. You may need to configure a different port."
    else
        echo -e "${GREEN}AVAILABLE${NC}"
    fi
fi

# Check system resources
echo -n "Checking system resources: "
MEM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
DISK_FREE=$(df -h / | awk 'NR==2 {print $4}')
CPU_CORES=$(grep -c ^processor /proc/cpuinfo)

if [ "$MEM_TOTAL" -lt 2000 ]; then
    echo -e "${YELLOW}WARNING${NC}"
    echo "Memory: ${MEM_TOTAL}MB (recommended: at least 2GB)"
else
    echo -e "${GREEN}OK${NC}"
    echo "Memory: ${MEM_TOTAL}MB"
fi
echo "Disk space available: ${DISK_FREE}"
echo "CPU cores: ${CPU_CORES}"

echo ""
echo "====================================================================="
echo "Environment check complete."
echo "Fix any highlighted issues before proceeding with deployment."
echo "====================================================================="
