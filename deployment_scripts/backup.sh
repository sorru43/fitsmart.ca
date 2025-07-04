#!/bin/bash

# Configuration
BACKUP_DIR="/var/backups/healthyrizz"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_USER="healthyrizz"
DB_NAME="healthyrizz"
APP_DIR="/var/www/healthyrizz"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Backup application files
echo "Backing up application files..."
tar -czf $BACKUP_DIR/app_backup_$TIMESTAMP.tar.gz $APP_DIR

# Backup environment file
echo "Backing up environment file..."
cp $APP_DIR/.env $BACKUP_DIR/env_backup_$TIMESTAMP

# Remove old backups
echo "Removing backups older than $RETENTION_DAYS days..."
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

# Set proper permissions
chmod 600 $BACKUP_DIR/*

echo "Backup completed successfully!" 
