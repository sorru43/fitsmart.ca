# HealthyRizz Deployment Scripts

This directory contains scripts for deploying and maintaining the HealthyRizz application on a Linux VPS.

## Scripts Overview

1. `deploy.sh` - Main deployment script
   - Clones/updates repository
   - Sets up virtual environment
   - Installs dependencies
   - Configures permissions
   - Runs database migrations
   - Restarts services

2. `backup.sh` - Backup script
   - Backs up database
   - Backs up application files
   - Backs up environment file
   - Maintains backup retention

3. `monitor.sh` - Monitoring script
   - Monitors system resources
   - Checks service status
   - Monitors application logs
   - Sends email alerts

4. `security_setup.sh` - Security configuration script
   - Configures firewall (UFW)
   - Sets up fail2ban
   - Configures Nginx security headers
   - Sets up system security

## Usage

### Initial Deployment

1. Clone the repository:
   ```bash
   git clone https://your-repository-url.git
   cd healthyrizz
   ```

2. Make scripts executable:
   ```bash
   chmod +x deploy.sh backup.sh monitor.sh security_setup.sh
   ```

3. Run security setup:
   ```bash
   sudo ./security_setup.sh
   ```

4. Run deployment:
   ```bash
   sudo ./deploy.sh
   ```

### Regular Maintenance

1. Set up automated backups:
   ```bash
   # Add to crontab
   0 2 * * * /path/to/backup.sh
   ```

2. Set up monitoring:
   ```bash
   # Run in screen or tmux session
   ./monitor.sh
   ```

3. Update application:
   ```bash
   sudo ./deploy.sh
   ```

## Configuration

### Environment Variables

Create a `.env` file in the application directory with the following variables:

```env
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
```

### Nginx Configuration

The Nginx configuration is automatically set up by the security script. Make sure to:

1. Replace `your_domain.com` with your actual domain
2. Set up SSL certificates using Let's Encrypt
3. Adjust security headers as needed

### System Requirements

- Ubuntu 20.04 LTS or later
- Python 3.11
- PostgreSQL 12 or later
- Nginx
- 4GB RAM minimum
- 20GB storage minimum

## Troubleshooting

### Common Issues

1. Permission denied errors:
   ```bash
   sudo chown -R www-data:www-data /var/www/healthyrizz
   sudo chmod -R 755 /var/www/healthyrizz
   ```

2. Database connection errors:
   - Check PostgreSQL service status
   - Verify database credentials
   - Check database permissions

3. Nginx errors:
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

4. Application errors:
   ```bash
   sudo journalctl -u healthyrizz -f
   ```

### Logs

- Application logs: `journalctl -u healthyrizz`
- Nginx logs: `/var/log/nginx/`
- System logs: `/var/log/syslog`

## Security

1. Keep system updated:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

2. Monitor fail2ban:
   ```bash
   sudo fail2ban-client status
   ```

3. Check firewall:
   ```bash
   sudo ufw status
   ```

4. Regular security audits:
   ```bash
   sudo lynis audit system
   ```

## Support

For support, please contact:
- Email: support@healthyrizz.com
- Documentation: https://docs.healthyrizz.com
- GitHub Issues: https://github.com/healthyrizz/issues 
