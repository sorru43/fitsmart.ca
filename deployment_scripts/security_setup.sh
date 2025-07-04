#!/bin/bash

# Configuration
APP_DIR="/var/www/healthyrizz"
NGINX_CONF="/etc/nginx/sites-available/healthyrizz"
FIREWALL_RULES=(
    "22/tcp"    # SSH
    "80/tcp"    # HTTP
    "443/tcp"   # HTTPS
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print status
print_status() {
    echo -e "${GREEN}[*] $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}[!] $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# Update system
print_status "Updating system..."
apt update && apt upgrade -y

# Install security packages
print_status "Installing security packages..."
apt install -y fail2ban ufw

# Configure UFW
print_status "Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing

for rule in "${FIREWALL_RULES[@]}"; do
    ufw allow $rule
done

ufw --force enable

# Configure fail2ban
print_status "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << EOL
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600
findtime = 600
EOL

systemctl restart fail2ban

# Configure Nginx security headers
print_status "Configuring Nginx security headers..."
cat > $NGINX_CONF << EOL
server {
    listen 80;
    server_name your_domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your_domain.com;

    ssl_certificate /etc/letsencrypt/live/your_domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your_domain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS (uncomment if you're sure)
    # add_header Strict-Transport-Security "max-age=63072000" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/healthyrizz/healthyrizz.sock;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
    }

    location /static {
        alias /var/www/healthyrizz/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOL

# Configure system security
print_status "Configuring system security..."

# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Configure password policy
cat > /etc/security/pwquality.conf << EOL
minlen = 12
dcredit = -1
ucredit = -1
ocredit = -1
lcredit = -1
EOL

# Set up automatic security updates
apt install -y unattended-upgrades
cat > /etc/apt/apt.conf.d/20auto-upgrades << EOL
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOL

# Restart services
print_status "Restarting services..."
systemctl restart sshd
systemctl restart nginx
systemctl restart fail2ban

print_status "Security setup completed successfully!" 
