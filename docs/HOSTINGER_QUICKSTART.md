# HealthyRizz Hostinger VPS Quickstart Guide

This guide provides quick steps to get HealthyRizz running on your Hostinger VPS with CloudPanel. It addresses common issues like Python version compatibility and database setup.

## Prerequisites

Before starting, ensure you have:

1. Access to your Hostinger VPS via SSH (as root or with sudo privileges)
2. CloudPanel installed (typically at https://YOUR_IP:8443)
3. A domain configured in CloudPanel (e.g., www.healthyrizz.ca)

## Step 1: Check Available Python Version

First, check which Python versions are available on your server:

```bash
# Check all available Python versions
python3 --version
python3.8 --version
python3.9 --version
python3.10 --version
python3.11 --version
```

If Python 3.8 or higher is not available, install it:

```bash
# For Ubuntu/Debian-based systems
apt update
apt install python3.9 python3.9-venv python3.9-dev
```

## Step 2: Install Required Packages

```bash
# Basic system packages
apt update
apt install git curl wget unzip zip python3-venv python3-dev

# PostgreSQL client is required for database operations
apt install postgresql-client

# For Python 3.12 you might need these additional packages
apt install python3-pip python3-wheel
```

## Step 3: Run the Deployment Script

The enhanced deployment script now automatically detects your Python version and accommodates various environments:

```bash
cd /home/healthyrizz/htdocs/www.healthyrizz.ca
chmod +x deploy_healthyrizz_cloudpanel.sh
./deploy_healthyrizz_cloudpanel.sh
```

## Step 4: Configure Database

If the script encounters database issues:

1. Check that PostgreSQL is running:
   ```bash
   systemctl status postgresql
   ```

2. Create the database in CloudPanel:
   - Go to CloudPanel -> Databases -> Add Database
   - Name: cp_healthyrizz_db
   - User: cp_healthyrizz_user

3. Update your .env file with the correct credentials:
   ```bash
   nano /home/healthyrizz/htdocs/www.healthyrizz.ca/.env
   ```
   
   Set DATABASE_URL to:
   ```
   DATABASE_URL=postgresql://cp_healthyrizz_user:your_password@localhost/cp_healthyrizz_db
   ```

4. Run migrations manually with debug enabled:
   ```bash
   cd /home/healthyrizz/htdocs/www.healthyrizz.ca
   source venv/bin/activate
   python -c "
   import logging
   logging.basicConfig(level=logging.DEBUG)
   from migrations import run_migrations
   run_migrations()
   "
   ```

## Step 5: Starting the Application

```bash
# Start using the Process Manager in CloudPanel:
1. Go to CloudPanel -> Sites -> www.healthyrizz.ca -> Settings -> PHP-FPM -> Process Manager
2. Enable the Process Manager and select clppm.yml

# Or start manually for testing:
cd /home/healthyrizz/htdocs/www.healthyrizz.ca
./start_healthyrizz.sh
```

## Troubleshooting

### Issue: Python version compatibility
- Solution: The script now detects available Python versions automatically. If you have Python 3.12 (which you do), make sure you have the necessary packages:
  ```bash
  apt install python3-venv python3-pip python3-dev python3-wheel
  ```
  
### Issue: Virtual environment creation fails with Python 3.12
- Solution: Python 3.12 might have some compatibility issues with venv. Try installing manually:
  ```bash
  # Install virtualenv
  pip3 install virtualenv
  
  # Create environment with virtualenv
  cd /home/healthyrizz/htdocs/www.healthyrizz.ca
  virtualenv -p python3 venv
  
  # Then activate and continue
  source venv/bin/activate
  ```

### Issue: Database tables don't exist
- Solution: The enhanced migrations.py now creates tables automatically before adding columns.

### Issue: Database connection failures
- Check your DATABASE_URL in .env
- Verify the database user has sufficient permissions
- Test the connection: `psql -U cp_healthyrizz_user -h localhost -d cp_healthyrizz_db -W`

### Issue: Application won't start
- Check process manager logs in CloudPanel
- View application logs: `tail -n 100 /home/healthyrizz/logs/www.healthyrizz.ca/healthyrizz.log`
- Test Gunicorn directly: 
  ```bash
  cd /home/healthyrizz/htdocs/www.healthyrizz.ca
  source venv/bin/activate
  gunicorn --workers 1 --bind 0.0.0.0:8090 --log-level debug main:app
  ```

## Next Steps

Once the application is running:

1. Set up SSL/TLS in CloudPanel (Sites -> www.healthyrizz.ca -> SSL)
2. Add your Stripe API keys (STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET)
3. Configure Twilio for SMS notifications
4. Set up email with proper SMTP credentials

For more detailed information, refer to DEPLOYMENT.md and CLOUDPANEL_GUIDE.md.
