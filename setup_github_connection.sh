#!/bin/bash

# CloudPanel GitHub Connection Setup Script
# Run this script on your CloudPanel server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/fitsmart/htdocs/www.fitsmart.ca"
GITHUB_REPO="https://github.com/sorru43/fitsmart.ca.git"
GIT_USER_NAME="FitSmart"
GIT_USER_EMAIL="122971823+sorru43@users.noreply.github.com"
BRANCH="main"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CloudPanel GitHub Connection Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi

# Navigate to project directory
cd "$PROJECT_DIR"
echo -e "${YELLOW}Current directory: $(pwd)${NC}"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: Git is not installed. Please install git first.${NC}"
    echo "Run: apt-get update && apt-get install -y git"
    exit 1
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Initializing git repository...${NC}"
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${GREEN}✓ Git repository already exists${NC}"
fi

# Configure git user
echo -e "${YELLOW}Configuring git user...${NC}"
git config user.name "$GIT_USER_NAME"
git config user.email "$GIT_USER_EMAIL"
echo -e "${GREEN}✓ Git user configured${NC}"

# Check if remote exists
if git remote get-url origin &> /dev/null; then
    echo -e "${YELLOW}Remote 'origin' already exists${NC}"
    CURRENT_URL=$(git remote get-url origin)
    echo "Current URL: $CURRENT_URL"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin "$GITHUB_REPO"
        echo -e "${GREEN}✓ Remote URL updated${NC}"
    fi
else
    echo -e "${YELLOW}Adding GitHub remote...${NC}"
    git remote add origin "$GITHUB_REPO"
    echo -e "${GREEN}✓ Remote 'origin' added${NC}"
fi

# Show remote configuration
echo ""
echo -e "${YELLOW}Remote configuration:${NC}"
git remote -v
echo ""

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    git status --short
    echo ""
    read -p "Do you want to commit these changes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Initial commit from CloudPanel server"
        echo -e "${GREEN}✓ Changes committed${NC}"
    fi
fi

# Try to fetch from remote
echo ""
echo -e "${YELLOW}Fetching from GitHub...${NC}"
if git fetch origin 2>&1 | grep -q "Authentication failed\|Permission denied"; then
    echo -e "${RED}⚠ Authentication failed${NC}"
    echo ""
    echo -e "${YELLOW}You need to set up authentication:${NC}"
    echo ""
    echo -e "${GREEN}Option 1: HTTPS with Personal Access Token${NC}"
    echo "1. Create a token at: https://github.com/settings/tokens"
    echo "2. Run: git config --global credential.helper store"
    echo "3. When prompted, use token as password"
    echo ""
    echo -e "${GREEN}Option 2: SSH Keys${NC}"
    echo "1. Generate key: ssh-keygen -t ed25519 -C 'fitsmart-cloudpanel'"
    echo "2. Add to GitHub: https://github.com/settings/keys"
    echo "3. Update remote: git remote set-url origin git@github.com:sorru43/fitsmart.ca.git"
    echo ""
else
    echo -e "${GREEN}✓ Successfully fetched from GitHub${NC}"
    
    # Check available branches
    echo ""
    echo -e "${YELLOW}Available branches:${NC}"
    git branch -r
    
    # Try to checkout main branch
    if git show-ref --verify --quiet refs/remotes/origin/$BRANCH; then
        echo ""
        echo -e "${YELLOW}Checking out $BRANCH branch...${NC}"
        if git checkout -b $BRANCH origin/$BRANCH 2>/dev/null || git checkout $BRANCH 2>/dev/null; then
            echo -e "${GREEN}✓ Checked out $BRANCH branch${NC}"
        else
            echo -e "${YELLOW}Already on a branch, pulling latest changes...${NC}"
            git pull origin $BRANCH --allow-unrelated-histories || true
        fi
    else
        echo -e "${YELLOW}Branch $BRANCH not found on remote${NC}"
        echo "You may need to push your local branch first"
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Set up authentication (see above if needed)"
echo "2. Pull latest: git pull origin $BRANCH"
echo "3. Push changes: git push -u origin $BRANCH"
echo ""

