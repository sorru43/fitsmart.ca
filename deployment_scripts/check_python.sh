#!/bin/bash

# Script to check available Python versions and modules on the system

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Python Environment Diagnostic Tool     ${NC}"
echo -e "${BLUE}  For HealthyRizz Deployment on Hostinger   ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check which Python versions are available
echo -e "${YELLOW}Checking available Python versions:${NC}"

check_version() {
    if command -v $1 >/dev/null 2>&1; then
        VERSION=$($1 --version 2>&1)
        echo -e "${GREEN}✓${NC} $1: $VERSION"
        return 0
    else
        echo -e "${RED}✗${NC} $1: Not found"
        return 1
    fi
}

check_version python
check_version python3
check_version python3.8
check_version python3.9
check_version python3.10
check_version python3.11

echo ""
echo -e "${YELLOW}Checking Python module 'venv' availability:${NC}"

check_module() {
    if $1 -c "import $2" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $1: $2 module is available"
        return 0
    else
        echo -e "${RED}✗${NC} $1: $2 module is not available"
        return 1
    fi
}

# Check if the primary python command has venv
if command -v python3 >/dev/null 2>&1; then
    check_module python3 venv
    
    # Check if pip is available
    echo ""
    echo -e "${YELLOW}Checking pip availability:${NC}"
    if command -v pip3 >/dev/null 2>&1; then
        PIP_VERSION=$(pip3 --version)
        echo -e "${GREEN}✓${NC} pip3: $PIP_VERSION"
        
        # Check if virtualenv is installed
        if pip3 list | grep -i virtualenv >/dev/null 2>&1; then
            VIRTUALENV_VERSION=$(pip3 list | grep -i virtualenv)
            echo -e "${GREEN}✓${NC} virtualenv: $VIRTUALENV_VERSION"
        else
            echo -e "${RED}✗${NC} virtualenv: Not installed"
            echo -e "   You can install it with: pip3 install virtualenv"
        fi
    else
        echo -e "${RED}✗${NC} pip3: Not found"
    fi
fi

echo ""
echo -e "${YELLOW}Checking PostgreSQL client:${NC}"
if command -v psql >/dev/null 2>&1; then
    PSQL_VERSION=$(psql --version)
    echo -e "${GREEN}✓${NC} PostgreSQL client: $PSQL_VERSION"
else
    echo -e "${RED}✗${NC} PostgreSQL client: Not found"
    echo -e "   You may need to install postgresql-client package"
fi

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  System information                    ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check OS
echo -e "${YELLOW}Operating System:${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo -e "${GREEN}✓${NC} OS: $PRETTY_NAME"
else
    echo -e "${RED}✗${NC} Unable to determine OS version"
fi

# Check memory
echo ""
echo -e "${YELLOW}Memory Information:${NC}"
if command -v free >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Memory:"
    free -h | grep -v +
else
    echo -e "${RED}✗${NC} Unable to determine memory information"
fi

# Check CPU
echo ""
echo -e "${YELLOW}CPU Information:${NC}"
if [ -f /proc/cpuinfo ]; then
    CPU_MODEL=$(grep "model name" /proc/cpuinfo | head -1 | cut -d ":" -f2 | sed 's/^[ \t]*//')
    CPU_CORES=$(grep -c "processor" /proc/cpuinfo)
    echo -e "${GREEN}✓${NC} CPU: $CPU_MODEL"
    echo -e "${GREEN}✓${NC} Cores: $CPU_CORES"
else
    echo -e "${RED}✗${NC} Unable to determine CPU information"
fi

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  HealthyRizz deployment recommendations   ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Recommend Python version
echo -e "${YELLOW}Recommended Python setup:${NC}"
if command -v python3.9 >/dev/null 2>&1 || command -v python3.10 >/dev/null 2>&1 || command -v python3.11 >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Your system has a suitable Python version for HealthyRizz"
    
    # Find the highest version
    if command -v python3.11 >/dev/null 2>&1; then
        RECOMMENDED="python3.11"
    elif command -v python3.10 >/dev/null 2>&1; then
        RECOMMENDED="python3.10"
    elif command -v python3.9 >/dev/null 2>&1; then
        RECOMMENDED="python3.9"
    else
        RECOMMENDED="python3.8"
    fi
    
    echo -e "   Recommended version: ${GREEN}$RECOMMENDED${NC}"
    
else
    echo -e "${RED}✗${NC} Your system doesn't have Python 3.9+ installed"
    echo -e "   Consider installing Python 3.9 or higher for best compatibility"
    echo -e "   For Ubuntu/Debian: ${GREEN}apt install python3.9 python3.9-venv python3.9-dev${NC}"
fi

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Update the deployment script if needed to use your available Python version"
echo -e "2. Run the deployment script: ${GREEN}./deploy_healthyrizz_cloudpanel.sh${NC}"
echo -e "3. Configure your database in CloudPanel"
echo -e "4. Update your .env file with the correct database URL"
echo -e "5. Run database migrations manually if needed"
echo -e ""
echo -e "For more detailed instructions, see ${GREEN}HOSTINGER_QUICKSTART.md${NC}"

echo ""
echo -e "${BLUE}=========================================${NC}"
