#!/bin/bash

# Install Redis if not already installed
if ! command -v redis-server &> /dev/null; then
    echo "Installing Redis..."
    sudo apt-get update
    sudo apt-get install -y redis-server
fi

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Create Redis configuration for Flask-Limiter
sudo mkdir -p /etc/redis/redis.conf.d
sudo tee /etc/redis/redis.conf.d/flask-limiter.conf << EOF
maxmemory 256mb
maxmemory-policy allkeys-lru
appendonly yes
appendfilename "flask-limiter.aof"
EOF

# Restart Redis to apply changes
sudo systemctl restart redis-server

# Update Flask-Limiter configuration in main.py
sed -i 's/storage_uri = "memory:\/\/"/storage_uri = "redis:\/\/localhost:6379\/1"/' main.py

# Restart the HealthyRizz service
sudo systemctl restart healthyrizz

echo "Redis has been installed and configured for Flask-Limiter"
echo "The HealthyRizz service has been restarted" 
