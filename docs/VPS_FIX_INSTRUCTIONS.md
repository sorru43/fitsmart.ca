# HealthyRizz VPS Fix Instructions

Follow these steps to fix the database schema issue on your VPS:

## 1. Transfer the Required Files

Upload these files to your VPS:
- `fix_vps_database.py` - Script to add missing columns to database schema
- `find_postgres_credentials.sh` - Helper script to locate database credentials
- `fix_postgres_direct.sh` - Alternative fix using postgres superuser
- `vps_requirements.txt` - Required Python packages
- `deploy_vps.sh` - Main deployment script
- `healthyrizz.service` - Systemd service file (if using systemd)

## 2. Find Your Database Credentials

If you don't know your database credentials, use the finder script:

```bash
# Make the script executable
chmod +x find_postgres_credentials.sh

# Run the script to search for database credentials
./find_postgres_credentials.sh
```

This script will search common locations for database credentials and provide information about your PostgreSQL setup.

## 3. Fix the Database Schema

You have two options:

### Option A: Using Database Credentials

If you know your database credentials, you can:

1. Set environment variables for database connection:
```bash
export PGDATABASE=your_database_name
export PGUSER=your_database_user
export PGPASSWORD=your_database_password
export PGHOST=your_database_host  # Usually localhost
export PGPORT=5432  # Default PostgreSQL port
```

OR

2. Provide them directly as arguments to the fix_vps_database.py script:
```bash
python fix_vps_database.py --dbname=your_database_name --user=your_database_user --password=your_database_password
```

### Option B: Using PostgreSQL Superuser (if you have sudo access)

If you have sudo access but don't know the database password:

```bash
# Make the script executable
chmod +x fix_postgres_direct.sh

# Run the direct fix script
./fix_postgres_direct.sh
```

This script will use the postgres superuser to add the missing columns.

## 4. Execute the Full Deployment

```bash
# Make the script executable
chmod +x deploy_vps.sh

# Run the deployment script
./deploy_vps.sh
```

The script will:
1. Set up a virtual environment (if needed)
2. Install the correct dependencies
3. Fix the database schema by adding missing columns
4. Run database migrations
5. Notify you when the process is complete

## 3. Set Up as a Service (if needed)

If you want to set up HealthyRizz as a systemd service:

```bash
# Copy the service file
sudo cp healthyrizz.service /etc/systemd/system/

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start at boot
sudo systemctl enable healthyrizz

# Start the service
sudo systemctl start healthyrizz

# Check the service status
sudo systemctl status healthyrizz
```

## 4. Verify the Application

After running the fix, verify that your application is working:

```bash
# Check the application logs
sudo journalctl -u healthyrizz -n 50

# Manually start the application (if not using systemd)
gunicorn main:app -b 127.0.0.1:8090
```

## 5. Verify Nginx Configuration (if using Nginx)

Make sure your Nginx configuration is pointing to the correct port:

```bash
sudo nano /etc/nginx/sites-available/healthyrizz.conf
```

Ensure it contains a proxy_pass to your gunicorn server:

```
location / {
    proxy_pass http://127.0.0.1:8090;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

Then restart Nginx:

```bash
sudo systemctl restart nginx
```

## Troubleshooting

If you encounter any issues:

1. Check the database connection details in your environment variables
2. Verify that the database user has permission to alter tables
3. Check application logs for specific errors:
   ```
   sudo journalctl -u healthyrizz -n 100
   ```

For immediate troubleshooting, you can directly fix the database:

```bash
# Connect to PostgreSQL
sudo -u postgres psql your_database_name

# Add missing columns
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS username VARCHAR(64);
UPDATE "user" SET username = email WHERE username IS NULL;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;

# Exit PostgreSQL
\q
```
