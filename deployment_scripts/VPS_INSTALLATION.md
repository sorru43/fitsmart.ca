# HealthyRizz VPS Installation Guide

This guide provides step-by-step instructions for deploying HealthyRizz on a Linux VPS.

## Prerequisites

- Ubuntu 20.04 LTS or later
- Root or sudo access
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)

## System Requirements

- CPU: 2+ cores
- RAM: 4GB minimum
- Storage: 20GB minimum
- Network: 1Gbps

## Installation Steps

### 1. System Update and Basic Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
    nginx postgresql postgresql-contrib \
    build-essential libpq-dev \
    certbot python3-certbot-nginx \
    supervisor
```

### 2. PostgreSQL Setup

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE healthyrizz;"
sudo -u postgres psql -c "CREATE USER healthyrizz WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE healthyrizz TO healthyrizz;"
```

### 3. Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/healthyrizz
sudo chown -R $USER:$USER /var/www/healthyrizz

# Clone repository (replace with your repository URL)
git clone https://your-repository-url.git /var/www/healthyrizz

# Create and activate virtual environment
cd /var/www/healthyrizz
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the application directory:

```bash
# Create .env file
cat > .env << EOL
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your_secure_secret_key
DATABASE_URL=postgresql://healthyrizz:your_secure_password@localhost/healthyrizz
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_specific_password
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_phone
SENDGRID_API_KEY=your_sendgrid_api_key
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
EOL
```

### 5. Gunicorn Setup

Create a Gunicorn service file:

```bash
sudo nano /etc/systemd/system/healthyrizz.service
```

Add the following content:

```ini
[Unit]
Description=HealthyRizz Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/healthyrizz
Environment="PATH=/var/www/healthyrizz/venv/bin"
ExecStart=/var/www/healthyrizz/venv/bin/gunicorn --workers 3 --bind unix:healthyrizz.sock -m 007 run:app

[Install]
WantedBy=multi-user.target
```

### 6. Nginx Configuration

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/healthyrizz
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/healthyrizz/healthyrizz.sock;
    }

    location /static {
        alias /var/www/healthyrizz/static;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/healthyrizz /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL Setup (Let's Encrypt)

```bash
sudo certbot --nginx -d your_domain.com
```

### 8. Start Services

```bash
# Set proper permissions
sudo chown -R www-data:www-data /var/www/healthyrizz

# Start and enable services
sudo systemctl start healthyrizz
sudo systemctl enable healthyrizz
sudo systemctl restart nginx
```

### 9. Database Migration

```bash
cd /var/www/healthyrizz
source venv/bin/activate
flask db upgrade
```

### 10. Create Admin User

```bash
cd /var/www/healthyrizz
source venv/bin/activate
python utils/create_admin.py
```

## Maintenance

### Logs

- Application logs: `journalctl -u healthyrizz`
- Nginx logs: `/var/log/nginx/`
- Supervisor logs: `/var/log/supervisor/`

### Backup

Create a backup script:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/healthyrizz"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U healthyrizz healthyrizz > $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Backup application files
tar -czf $BACKUP_DIR/app_backup_$TIMESTAMP.tar.gz /var/www/healthyrizz

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete
```

## Security Considerations

1. Keep system and packages updated
2. Use strong passwords
3. Configure firewall (UFW)
4. Regular security audits
5. Monitor system logs
6. Regular backups
7. SSL/TLS encryption
8. Rate limiting
9. Secure headers
10. Regular security updates

## Troubleshooting

1. Check service status: `sudo systemctl status healthyrizz`
2. Check logs: `journalctl -u healthyrizz -f`
3. Check Nginx: `sudo nginx -t`
4. Check permissions: `ls -la /var/www/healthyrizz`
5. Check database: `sudo -u postgres psql -d healthyrizz`

## Support

For support, please contact:
- Email: support@healthyrizz.com
- Documentation: https://docs.healthyrizz.com
- GitHub Issues: https://github.com/healthyrizz/issues 
