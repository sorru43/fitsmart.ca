#!/bin/bash

echo "=== Redis Status Check ==="
echo ""

# Check if Redis service is running
echo "1. Checking Redis service status..."
if systemctl is-active --quiet redis-server; then
    echo "✅ Redis service is running"
else
    echo "❌ Redis service is not running"
    echo "Starting Redis service..."
    sudo systemctl start redis-server
fi

# Check Redis port
echo ""
echo "2. Checking Redis port..."
if netstat -tlnp | grep :6379; then
    echo "✅ Redis is listening on port 6379"
else
    echo "❌ Redis is not listening on port 6379"
fi

# Test Redis connection
echo ""
echo "3. Testing Redis connection..."
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis connection successful"
else
    echo "❌ Redis connection failed"
fi

# Check Redis configuration
echo ""
echo "4. Redis configuration:"
redis-cli config get bind
redis-cli config get port
redis-cli config get maxmemory

echo ""
echo "=== Redis Check Complete ===" 