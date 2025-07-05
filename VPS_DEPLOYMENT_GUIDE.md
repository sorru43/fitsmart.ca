# HealthyRizz VPS Linux Deployment Guide

This guide provides step-by-step instructions for deploying HealthyRizz on a VPS running Linux (Ubuntu/Debian).

## 📋 Prerequisites

- VPS with Ubuntu 20.04+ or Debian 11+
- Root access or sudo privileges
- Domain name pointing to your VPS IP
- At least 2GB RAM and 20GB storage

## 🚀 Quick Deployment

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/healthyrizz.git
cd healthyrizz

# Make deployment script executable
chmod +x deploy_vps.sh

# Run the deployment script
sudo ./deploy_vps.sh
```

### 2. Manual Setup (Alternative)

If you prefer manual setup, follow these steps:

#### System Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban
```

#### Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/healthyrizz
sudo chown www-data:www-data /var/www/healthyrizz

# Copy application files
sudo cp -r * /var/www/healthyrizz/

# Create virtual environment
cd /var/www/healthyrizz
sudo -u www-data python3 -m venv venv
sudo -u www-data venv/bin/pip install --upgrade pip
sudo -u www-data venv/bin/pip install -r requirements-production.txt
```

#### Database Setup

```bash
# Create database and user
sudo -u postgres createuser --createdb --createrole --superuser healthyrizz
sudo -u postgres createdb healthyrizz

# Initialize database
cd /var/www/healthyrizz
sudo -u www-data venv/bin/flask db upgrade
```

## ⚙️ Configuration

### 1. Environment Variables

Create `.env` file in `/var/www/healthyrizz/`:

```bash
# Database Configuration
DATABASE_URL=postgresql://healthyrizz:healthyrizz@localhost/healthyrizz

# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production
DEBUG=False

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Razorpay Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=your-razorpay-webhook-secret

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security
WTF_CSRF_SECRET_KEY=your-csrf-secret-key
SESSION_COOKIE_SECURE=True

# Server Configuration
SERVER_NAME=yourdomain.com
```

### 2. SSL Certificate

```bash
# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is already configured in cron
```

## 🔧 Service Configuration

### 1. Gunicorn

The application runs with Gunicorn using the configuration in `gunicorn.conf.py`.

### 2. Supervisor

Supervisor manages the application processes. Configuration is in `supervisor.conf`.

### 3. Nginx

Nginx serves as a reverse proxy. Configuration is in `nginx.conf`.

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check application status
sudo supervisorctl status healthyrizz

# Check nginx status
sudo systemctl status nginx

# Check database status
sudo systemctl status postgresql

# Check redis status
sudo systemctl status redis-server
```

### Logs

```bash
# Application logs
sudo tail -f /var/log/healthyrizz/gunicorn_error.log
sudo tail -f /var/log/healthyrizz/gunicorn_access.log

# Nginx logs
sudo tail -f /var/log/nginx/healthyrizz_error.log
sudo tail -f /var/log/nginx/healthyrizz_access.log

# Supervisor logs
sudo tail -f /var/log/healthyrizz/supervisor.log
```

### Backups

```bash
# Manual backup
sudo /usr/local/bin/backup-healthyrizz

# Check backup schedule
sudo crontab -l
```

## 🔒 Security

### Firewall

UFW is configured with:
- SSH (port 22)
- HTTP (port 80)
- HTTPS (port 443)

### Fail2ban

Protects against brute force attacks on SSH and web services.

### SSL/TLS

Automatic SSL certificate renewal with Let's Encrypt.

## 🚨 Troubleshooting

### Common Issues

1. **Application won't start**
   ```bash
   sudo supervisorctl restart healthyrizz
   sudo tail -f /var/log/healthyrizz/supervisor_error.log
   ```

2. **Database connection issues**
   ```bash
   sudo systemctl restart postgresql
   sudo -u postgres psql -c "SELECT version();"
   ```

3. **Nginx errors**
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **Permission issues**
   ```bash
   sudo chown -R www-data:www-data /var/www/healthyrizz
   sudo chmod -R 755 /var/www/healthyrizz
   ```

### Performance Tuning

1. **Database optimization**
   ```bash
   # Edit PostgreSQL configuration
   sudo nano /etc/postgresql/*/main/postgresql.conf
   ```

2. **Nginx optimization**
   ```bash
   # Edit Nginx configuration
   sudo nano /etc/nginx/nginx.conf
   ```

3. **Gunicorn optimization**
   ```bash
   # Edit Gunicorn configuration
   sudo nano /var/www/healthyrizz/gunicorn.conf.py
   ```

## 📈 Scaling

### Horizontal Scaling

1. **Load Balancer**: Use HAProxy or Nginx as load balancer
2. **Multiple Instances**: Run multiple Gunicorn instances
3. **Database Replication**: Set up PostgreSQL read replicas

### Vertical Scaling

1. **Increase Resources**: Upgrade VPS plan
2. **Optimize Code**: Profile and optimize application code
3. **Caching**: Implement Redis caching strategies

## 🔄 Updates

### Application Updates

```bash
cd /var/www/healthyrizz
sudo git pull origin main
sudo -u www-data venv/bin/pip install -r requirements-production.txt
sudo supervisorctl restart healthyrizz
```

### System Updates

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo systemctl restart nginx postgresql redis-server
```

## 📞 Support

For issues and support:
- Check logs: `/var/log/healthyrizz/`
- Monitor system resources: `htop`, `df -h`, `free -h`
- Application health: `curl https://yourdomain.com/health`

## 📝 Notes

- All services are configured to start automatically on boot
- Logs are rotated daily and kept for 52 weeks
- Backups are created daily and kept for 30 days
- SSL certificates auto-renew every 60 days
- Health checks run every 5 minutes

---

**Last Updated**: June 2025
**Version**: 1.0.0 