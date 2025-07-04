#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="healthyrizz"
VERSION=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="${APP_NAME}_${VERSION}.zip"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Creating temporary directory: $TEMP_DIR"

# Copy application files
echo "Copying application files..."
cp -r \
    main.py \
    models.py \
    forms.py \
    utils/ \
    static/ \
    templates/ \
    requirements.txt \
    deploy.sh \
    README.md \
    .env.example \
    $TEMP_DIR/

# Create zip file
echo "Creating zip package..."
cd $TEMP_DIR
zip -r $PACKAGE_NAME .
cd -

# Move zip file to current directory
mv $TEMP_DIR/$PACKAGE_NAME .

# Clean up
echo "Cleaning up..."
rm -rf $TEMP_DIR

echo "Package created successfully: $PACKAGE_NAME" 
