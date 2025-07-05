#!/bin/bash

# Configuration
APP_DIR="/var/www/healthyrizz"
LOG_DIR="/var/log/healthyrizz"
ALERT_EMAIL="admin@healthyrizz.com"
DISK_THRESHOLD=80
MEMORY_THRESHOLD=80
CPU_THRESHOLD=80

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to send email alert
send_alert() {
    echo "$1" | mail -s "HealthyRizz Alert: $2" $ALERT_EMAIL
}

# Function to check disk usage
check_disk() {
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $usage -gt $DISK_THRESHOLD ]; then
        echo -e "${RED}[!] High disk usage: $usage%${NC}"
        send_alert "Disk usage is at $usage%" "High Disk Usage"
    else
        echo -e "${GREEN}[*] Disk usage: $usage%${NC}"
    fi
}

# Function to check memory usage
check_memory() {
    local usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}' | cut -d. -f1)
    if [ $usage -gt $MEMORY_THRESHOLD ]; then
        echo -e "${RED}[!] High memory usage: $usage%${NC}"
        send_alert "Memory usage is at $usage%" "High Memory Usage"
    else
        echo -e "${GREEN}[*] Memory usage: $usage%${NC}"
    fi
}

# Function to check CPU usage
check_cpu() {
    local usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)
    if [ $usage -gt $CPU_THRESHOLD ]; then
        echo -e "${RED}[!] High CPU usage: $usage%${NC}"
        send_alert "CPU usage is at $usage%" "High CPU Usage"
    else
        echo -e "${GREEN}[*] CPU usage: $usage%${NC}"
    fi
}

# Function to check service status
check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo -e "${GREEN}[*] $service is running${NC}"
    else
        echo -e "${RED}[!] $service is not running${NC}"
        send_alert "$service is not running" "Service Down"
        systemctl restart $service
    fi
}

# Function to check application logs
check_logs() {
    local error_count=$(journalctl -u healthyrizz --since "1 hour ago" | grep -i "error" | wc -l)
    if [ $error_count -gt 0 ]; then
        echo -e "${RED}[!] Found $error_count errors in the last hour${NC}"
        send_alert "Found $error_count errors in the last hour" "Application Errors"
    else
        echo -e "${GREEN}[*] No errors found in the last hour${NC}"
    fi
}

# Main monitoring loop
while true; do
    echo "=== HealthyRizz Monitoring Report ==="
    echo "Time: $(date)"
    echo "--------------------------------"
    
    check_disk
    check_memory
    check_cpu
    check_service healthyrizz
    check_service nginx
    check_service postgresql
    check_logs
    
    echo "--------------------------------"
    echo "Report completed at $(date)"
    echo ""
    
    # Wait for 5 minutes before next check
    sleep 300
done 
