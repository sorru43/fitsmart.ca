# HealthyRizz Deployment: Quick Start Guide

This is a condensed guide for deploying the HealthyRizz application on your Hostinger VPS with CloudPanel.

## Step 1: Initial Setup (SSH into your server)

```bash
# SSH into your server
ssh root@147.93.27.232

# Navigate to the web directory
cd /home/healthyrizz/htdocs/www.healthyrizz.ca

# Make sure the directory exists
mkdir -p /home/healthyrizz/htdocs/www.healthyrizz.ca
```

## Step 2: Upload Files

**Option 1: Using Git**
```bash
cd /home/healthyrizz/htdocs/www.healthyrizz.ca
git clone https://your-repo-url.git .
```

**Option 2: Upload deployment scripts first, then run them**
```bash
# Upload the deployment script
scp deploy_healthyrizz_cloudpanel.sh root@147.93.27.232:/home/healthyrizz/htdocs/www.healthyrizz.ca/

# Make it executable
chmod +x /home/healthyrizz/htdocs/www.healthyrizz.ca/deploy_healthyrizz_cloudpanel.sh

# Run the script
cd /home/healthyrizz/htdocs/www.healthyrizz.ca
./deploy_healthyrizz_cloudpanel.sh
```

## Step 3: Database Setup

**Use CloudPanel UI:**
1. Go to CloudPanel at https://147.93.27.232:8443
2. Navigate to Databases → Add Database
3. Create a database named `healthyrizz_db`
4. Note the username and password

**Update .env file:**
```bash
nano /home/healthyrizz/htdocs/www.healthyrizz.ca/.env
# Update DATABASE_URL with the correct credentials
```

## Step 4: Configure CloudPanel

1. Go to Sites → www.healthyrizz.ca → Settings
2. PHP-FPM → Process Manager:
   - Enable Process Manager
   - Select the clppm.yml file

3. Add custom Nginx configuration:
```nginx
location / {
    proxy_pass http://127.0.0.1:8090;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /static {
    alias /home/healthyrizz/htdocs/www.healthyrizz.ca/static;
    expires 30d;
}

client_max_body_size 10M;
```

4. Set up SSL at: Sites → www.healthyrizz.ca → SSL

## Step 5: Start the Application

Click "Start" in CloudPanel Process Manager.

## Step 6: Verify Deployment

Visit https://www.healthyrizz.ca to confirm everything is working.

## Common Issues

1. **Application won't start**: Check logs in CloudPanel → Sites → www.healthyrizz.ca → Logs
2. **Database connection issues**: Verify DATABASE_URL in .env file
3. **Missing dependencies**: Run `pip install -r requirements.txt` in the project directory
4. **Permission issues**: Run `chown -R healthyrizz:healthyrizz /home/healthyrizz/htdocs/www.healthyrizz.ca`

## Important Environment Variables

Make sure these are set in your .env file:

```
SECRET_KEY=...
DATABASE_URL=postgresql://user:password@localhost/healthyrizz_db
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
MAIL_PASSWORD=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...
```

## Deployment Script

For a fully automated deployment, use the included scripts:
- `deploy_healthyrizz.sh` - For standard VPS deployment
- `deploy_healthyrizz_cloudpanel.sh` - Specifically for CloudPanel environments
