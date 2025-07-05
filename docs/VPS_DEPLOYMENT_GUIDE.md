# HealthyRizz VPS Deployment Guide

This guide will help you deploy and troubleshoot HealthyRizz on your VPS.

## Quick Setup

1. Upload all files to your VPS
2. Make the deployment script executable:
   ```
   chmod +x deploy_vps.sh
   ```
3. Run the deployment script:
   ```
   ./deploy_vps.sh
   ```

## Troubleshooting Common Issues

### Application Won't Start

1. Check for error messages in your logs:
   ```
   sudo journalctl -u healthyrizz -n 100
   ```
   or
   ```
   sudo tail -n 100 /var/log/supervisor/healthyrizz.log
   ```

2. Verify Python version compatibility:
   ```
   python3 --version
   ```
   HealthyRizz works best with Python 3.9-3.11

3. Check your virtual environment:
   ```
   source venv/bin/activate
   pip list
   ```

### Dependency Conflicts

If you encounter dependency conflicts, you can:

1. Use the VPS-specific requirements file (`vps_requirements.txt`) which contains versions known to work on VPS environments.

2. Create a clean virtual environment:
   ```
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r vps_requirements.txt
   ```

### Database Connection Issues

1. Verify your database connection string in environment variables.
2. Ensure PostgreSQL is running:
   ```
   sudo systemctl status postgresql
   ```
3. Check database permissions:
   ```
   sudo -u postgres psql -c "SELECT usename, usesuper, usecreatedb FROM pg_user;"
   ```

## Customizing Your Deployment

### Using Systemd

Create a systemd service file at `/etc/systemd/system/healthyrizz.service`:

```
[Unit]
Description=HealthyRizz Meal Delivery Service
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/healthyrizz
ExecStart=/path/to/healthyrizz/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then activate it:
```
sudo systemctl enable healthyrizz
sudo systemctl start healthyrizz
```

### Using Supervisor

Create a supervisor config file at `/etc/supervisor/conf.d/healthyrizz.conf`:

```
[program:healthyrizz]
command=/path/to/healthyrizz/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 main:app
directory=/path/to/healthyrizz
user=your_username
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/healthyrizz.log
```

Then activate it:
```
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start healthyrizz
```

## Rollback to Previous Version

If you need to rollback to a previous working version:

1. Restore your codebase from backup or previous git commit
2. Use the `vps_requirements.txt` file to install dependencies
3. Restart your service
