# CloudPanel-Specific Deployment Guide for HealthyRizz

This guide focuses specifically on CloudPanel commands and features for deploying the HealthyRizz application on your Hostinger VPS.

## CloudPanel CLI (`clpctl`)

CloudPanel comes with a powerful command-line tool `clpctl` that can be used to manage your applications directly from the terminal.

### Basic CloudPanel CLI Commands

```bash
# List all sites
clpctl site:list

# List all databases
clpctl database:list

# Restart Nginx
clpctl nginx:restart

# View application logs
clpctl log:site www.healthyrizz.ca

# Backup a database
clpctl database:backup healthyrizz_db

# Restore a database
clpctl database:restore healthyrizz_db /path/to/backup.sql
```

## Setting Up Your HealthyRizz Application

### 1. Create a Site in CloudPanel

If the site doesn't already exist:

```bash
# Create a new site (will prompt for domain name)
clpctl site:add
```

Or use the CloudPanel web interface:
1. Go to Sites → Add Site
2. Enter domain: www.healthyrizz.ca
3. Set document root to: /home/healthyrizz/htdocs/www.healthyrizz.ca

### 2. Create a Database

```bash
# Create a new database
clpctl database:add
```

This will prompt you for:
- Database name (e.g., healthyrizz_db)
- Database user (e.g., healthyrizz_user)
- Password

Or use the CloudPanel web interface:
1. Go to Databases → Add Database
2. Enter the database details

After creating the database, update your .env file with the correct database connection string:

```bash
# Edit the .env file
nano /home/healthyrizz/htdocs/www.healthyrizz.ca/.env

# Update the DATABASE_URL with the CloudPanel database credentials
# Format: postgresql://username:password@localhost/database_name
DATABASE_URL=postgresql://cp_healthyrizz_user:your_password@localhost/cp_healthyrizz_db
```

Then initialize the database:

```bash
# Run the migrations script to create tables and add necessary columns
cd /home/healthyrizz/htdocs/www.healthyrizz.ca
source venv/bin/activate
python migrations.py
```

> **Note**: The enhanced migrations script will automatically create all required tables if they don't exist and then add the Stripe-specific columns. Make sure the database user has sufficient privileges (CREATE TABLE).

### 3. Configure Process Manager

Create a CloudPanel Process Manager (clppm) configuration:

```bash
cat > /home/healthyrizz/htdocs/www.healthyrizz.ca/clppm.yml << EOF
# CloudPanel Process Manager Configuration
processes:
  - name: healthyrizz
    script: /home/healthyrizz/htdocs/www.healthyrizz.ca/venv/bin/gunicorn
    args: ["--workers", "3", "--bind", "0.0.0.0:8090", "--timeout", "120", "main:app"]
    cwd: /home/healthyrizz/htdocs/www.healthyrizz.ca
    env: {}
    merge_logs: true
    instances: 1
    exec_mode: fork
    watch: false
    restart_delay: 5000
EOF
```

Enable the Process Manager in CloudPanel:
1. Go to Sites → www.healthyrizz.ca → Settings → PHP-FPM → Process Manager
2. Enable Process Manager
3. Select the clppm.yml file

### 4. Custom Nginx Configuration

Add a custom Nginx configuration for your Flask application:

```bash
# Create a temporary file with the configuration
cat > /tmp/healthyrizz_nginx.conf << EOF
# Proxy requests to the Gunicorn server
location / {
    proxy_pass http://127.0.0.1:8090;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
}

# Serve static files directly
location /static {
    alias /home/healthyrizz/htdocs/www.healthyrizz.ca/static;
    expires 30d;
}

# Set maximum upload size
client_max_body_size 10M;
EOF
```

Then add this to your site using the CloudPanel web interface:
1. Go to Sites → www.healthyrizz.ca → Settings → Nginx
2. Add the contents of the temporary file to the Custom Nginx directives
3. Apply and restart Nginx

### 5. Setting Up SSL/TLS

```bash
# Request Let's Encrypt certificate
clpctl ssl:create:letsencrypt www.healthyrizz.ca
```

Or use the CloudPanel web interface:
1. Go to Sites → www.healthyrizz.ca → SSL
2. Select Let's Encrypt
3. Follow the prompts

### 6. Managing Application Processes

```bash
# Start the application process
clpctl clppm:start www.healthyrizz.ca

# Stop the application process
clpctl clppm:stop www.healthyrizz.ca

# Restart the application process
clpctl clppm:restart www.healthyrizz.ca

# View process status
clpctl clppm:status www.healthyrizz.ca
```

## CloudPanel-Specific Directories

CloudPanel organizes sites in a specific way:

- **Document Root**: `/home/healthyrizz/htdocs/www.healthyrizz.ca`
- **Log Directory**: `/home/healthyrizz/logs/www.healthyrizz.ca`
- **Configuration**: `/etc/nginx/sites-enabled/100-www.healthyrizz.ca.conf`

## Managing Environment Variables in CloudPanel

CloudPanel doesn't have a built-in environment variable manager, but you can use the .env file approach:

```bash
# Create or edit the .env file
nano /home/healthyrizz/htdocs/www.healthyrizz.ca/.env
```

Make sure to secure this file:

```bash
chmod 600 /home/healthyrizz/htdocs/www.healthyrizz.ca/.env
chown healthyrizz:healthyrizz /home/healthyrizz/htdocs/www.healthyrizz.ca/.env
```

## Automating Backups with CloudPanel

```bash
# Set up automated database backups
clpctl backup:add
```

In the CloudPanel web interface:
1. Go to Backups → Add Backup
2. Select type: Database
3. Select database: healthyrizz_db
4. Set schedule (daily, weekly, etc.)
5. Set retention period

## Debugging in CloudPanel

```bash
# View Nginx error logs
clpctl log:nginx:error

# View Nginx access logs for your site
clpctl log:nginx:access www.healthyrizz.ca

# View application logs
clpctl log:site www.healthyrizz.ca

# Check Nginx configuration
clpctl nginx:check
```

### Troubleshooting Database Issues

If you encounter database errors during deployment:

1. **Check database connection**:
   ```bash
   # Using psql to test connection
   psql -U cp_healthyrizz_user -h localhost -d cp_healthyrizz_db -W
   ```

2. **Verify database permissions**:
   ```bash
   # Connect to PostgreSQL
   sudo -u postgres psql
   
   # Check user privileges
   \du cp_healthyrizz_user
   
   # Grant necessary permissions if needed
   ALTER USER cp_healthyrizz_user WITH CREATEDB;
   ```

3. **Manual database initialization**:
   ```bash
   # Run migrations with verbose output
   cd /home/healthyrizz/htdocs/www.healthyrizz.ca
   source venv/bin/activate
   python -c "
   import logging
   logging.basicConfig(level=logging.DEBUG)
   from migrations import run_migrations
   run_migrations()
   "
   ```

### Troubleshooting Application Startup

If the application fails to start:

1. **Check process manager status**:
   ```bash
   clpctl clppm:status www.healthyrizz.ca
   ```

2. **View application logs**:
   ```bash
   # View the last 100 lines of the application log
   tail -n 100 /home/healthyrizz/logs/www.healthyrizz.ca/healthyrizz.log
   ```

3. **Test Gunicorn directly**:
   ```bash
   cd /home/healthyrizz/htdocs/www.healthyrizz.ca
   source venv/bin/activate
   gunicorn --workers 1 --bind 0.0.0.0:8090 --log-level debug main:app
   ```

### Troubleshooting Nginx Configuration

If Nginx is not properly routing to your application:

1. **Test Nginx configuration**:
   ```bash
   nginx -t
   ```

2. **Verify proxy settings**:
   ```bash
   # Check if the port is being listened to
   netstat -tuln | grep 8090
   
   # Test connection locally
   curl -v http://localhost:8090/
   ```

## CloudPanel Security Best Practices

1. **Update CloudPanel regularly**:
   ```bash
   clpctl update
   ```

2. **Enable CloudPanel Firewall**:
   - Go to Security → Firewall in the CloudPanel web interface
   - Enable and configure as needed

3. **Set up CloudPanel two-factor authentication**:
   - Go to Your Account → Two-Factor Authentication in the CloudPanel web interface
