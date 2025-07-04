# HealthyRizz Deployment Guide

This guide will help you deploy the HealthyRizz application on a Hostinger VPS with CloudPanel.

## Prerequisites

- Hostinger VPS with Ubuntu 24.04 or later
- CloudPanel installed
- Domain name (www.healthyrizz.ca) pointing to your server
- SSH access to your server

## Deployment Steps

1. **Upload Files**
   - Upload the project files to `/home/healthyrizz/htdocs/www.healthyrizz.ca/`
   - Make sure all files are uploaded with correct permissions

2. **Run Deployment Script**
   ```bash
   cd /home/healthyrizz/htdocs/www.healthyrizz.ca/
   chmod +x deploy_healthyrizz.sh
   ./deploy_healthyrizz.sh
   ```

3. **Follow the Interactive Menu**
   The script will guide you through the following steps:
   1. Install System Dependencies
   2. Setup Python Environment
   3. Install Project Dependencies
   4. Configure Environment Variables
   5. Setup Database
   6. Configure Gunicorn
   7. Setup Systemd Service
   8. Configure Nginx
   9. Setup SSL Certificate
   10. Start Services

## Post-Deployment

### Common Commands

1. **Check Service Status**
   ```bash
   sudo systemctl status healthyrizz
   sudo systemctl status nginx
   ```

2. **View Logs**
   ```bash
   # Gunicorn logs
   tail -f logs/gunicorn-access.log
   tail -f logs/gunicorn-error.log
   
   # Nginx logs
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Restart Services**
   ```bash
   sudo systemctl restart healthyrizz
   sudo systemctl restart nginx
   ```

4. **Backup Database**
   ```bash
   ./deploy_healthyrizz.sh
   # Select option 14
   ```

### Troubleshooting

1. **Service Won't Start**
   - Check logs: `sudo journalctl -u healthyrizz -f`
   - Verify permissions: `ls -la /home/healthyrizz/htdocs/www.healthyrizz.ca/`
   - Check environment variables: `cat .env`

2. **Nginx Issues**
   - Test configuration: `sudo nginx -t`
   - Check error logs: `sudo tail -f /var/log/nginx/error.log`

3. **Database Connection Issues**
   - Verify database URL in .env
   - Check PostgreSQL status: `sudo systemctl status postgresql`
   - Test connection: `psql -U healthyrizz -d healthyrizz_db`

### Maintenance

1. **Regular Backups**
   - Database backups are stored in the `backups` directory
   - Backup naming format: `backup_YYYYMMDD_HHMMSS.sql`

2. **Updating the Application**
   ```bash
   git pull  # If using git
   source venv/bin/activate
   pip install -r requirements.txt
   python reset_db.py  # If database schema changed
   sudo systemctl restart healthyrizz
   ```

3. **Monitoring**
   - Check application status: `sudo systemctl status healthyrizz`
   - Monitor logs: `tail -f logs/gunicorn-access.log`
   - Check resource usage: `htop`

## Security Notes

1. Keep your `.env` file secure and never commit it to version control
2. Regularly update system packages: `sudo apt update && sudo apt upgrade`
3. Monitor logs for suspicious activity
4. Keep SSL certificates up to date
5. Use strong passwords for all services

## Support

If you encounter any issues:
1. Check the logs for error messages
2. Verify all configuration files
3. Ensure all services are running
4. Check file permissions
5. Verify database connectivity

For additional help, contact the development team.
