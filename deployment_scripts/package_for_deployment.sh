#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Creating deployment package for HealthyRizz...${NC}"

# Create a temporary directory
TEMP_DIR="healthyrizz_deployment_$(date +%Y%m%d_%H%M%S)"
mkdir -p $TEMP_DIR

# Copy necessary files
echo "Copying project files..."
cp -r app.py blueprints.py config.py deploy_healthyrizz.sh extensions.py forms.py \
    main.py models.py requirements.txt reset_db.py routes.py routes_api.py \
    routes_notifications.py routes_stripe.py static templates utils \
    $TEMP_DIR/

# Create necessary directories
mkdir -p $TEMP_DIR/logs
mkdir -p $TEMP_DIR/backups

# Set permissions
chmod +x $TEMP_DIR/deploy_healthyrizz.sh

# Create deployment package
echo "Creating deployment package..."
tar -czf healthyrizz_deployment.tar.gz $TEMP_DIR

# Clean up
echo "Cleaning up..."
rm -rf $TEMP_DIR

echo -e "${GREEN}Deployment package created: healthyrizz_deployment.tar.gz${NC}"
echo -e "${YELLOW}To deploy:${NC}"
echo "1. Upload healthyrizz_deployment.tar.gz to your server"
echo "2. Extract: tar -xzf healthyrizz_deployment.tar.gz"
echo "3. Navigate to the extracted directory"
echo "4. Run: ./deploy_healthyrizz.sh" 
