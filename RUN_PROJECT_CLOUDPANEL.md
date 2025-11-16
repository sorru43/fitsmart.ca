# Running FitSmart Project on CloudPanel

This guide will help you run your Flask application on CloudPanel server.

## Prerequisites Check

First, verify you have everything:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Check Python version
python3 --version

# Check if virtual environment exists
ls -la | grep venv
```

## Step 1: Set Up Python Virtual Environment

```bash
# Navigate to project
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Create virtual environment (if it doesn't exist)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

## Step 2: Install Dependencies

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install all requirements
pip install -r requirements.txt
```

## Step 3: Set Up Environment Variables

Create a `.env` file with your configuration:

```bash
# Create .env file
nano .env
```

Add these essential variables (adjust as needed):

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_APP=wsgi.py
FLASK_ENV=production

# Database (SQLite for now, or PostgreSQL for production)
DATABASE_URL=sqlite:///database/fitsmart.db

# Email Configuration (if using)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Payment Gateways (if using)
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
STRIPE_PUBLIC_KEY=your-stripe-key
STRIPE_SECRET_KEY=your-stripe-secret

# Other settings
DEBUG=False
```

Save and exit (Ctrl+X, then Y, then Enter).

## Step 4: Initialize Database

```bash
# Activate virtual environment
source venv/bin/activate

# Initialize database
python3 -c "
from app import create_app
from database.models import db, User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    db.create_all()
    
    # Create admin user if doesn't exist
    admin = User.query.filter_by(email='admin@fitsmart.ca').first()
    if not admin:
        admin = User(
            email='admin@fitsmart.ca',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created: admin@fitsmart.ca / admin123')
    else:
        print('ℹ️  Admin user already exists')
"
```

## Step 5: Run the Application

### Option A: Development Mode (Testing)

```bash
# Activate virtual environment
source venv/bin/activate

# Set Flask environment
export FLASK_APP=wsgi.py
export FLASK_ENV=development

# Run Flask development server
flask run --host=0.0.0.0 --port=5000
```

Or using Python directly:

```bash
source venv/bin/activate
python3 wsgi.py
```

### Option B: Production Mode with Gunicorn (Recommended)

```bash
# Activate virtual environment
source venv/bin/activate

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 wsgi:app
```

Or with more options:

```bash
gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  wsgi:app
```

## Step 6: Access Your Application

Once running, access your application at:
- **Local**: http://localhost:5000
- **External**: http://your-server-ip:5000
- **Domain**: http://www.fitsmart.ca (if DNS is configured)

## Step 7: Set Up as a Service (Optional - For Auto-Start)

Create a systemd service to run automatically:

```bash
# Create service file
sudo nano /etc/systemd/system/fitsmart.service
```

Add this content:

```ini
[Unit]
Description=FitSmart Flask Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/home/fitsmart/htdocs/www.fitsmart.ca
Environment="PATH=/home/fitsmart/htdocs/www.fitsmart.ca/venv/bin"
ExecStart=/home/fitsmart/htdocs/www.fitsmart.ca/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --timeout 120 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable fitsmart

# Start service
sudo systemctl start fitsmart

# Check status
sudo systemctl status fitsmart
```

## Step 8: Configure Nginx (If using CloudPanel)

CloudPanel usually handles Nginx configuration, but you can verify:

1. Go to CloudPanel web interface
2. Navigate to your site settings
3. Ensure it's pointing to your application
4. If needed, configure reverse proxy to `http://127.0.0.1:5000`

## Quick Start Script

Create a quick start script:

```bash
# Create start script
nano start.sh
```

Add:

```bash
#!/bin/bash
cd /home/fitsmart/htdocs/www.fitsmart.ca
source venv/bin/activate
export FLASK_APP=wsgi.py
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 wsgi:app
```

Make it executable:

```bash
chmod +x start.sh
```

Run it:

```bash
./start.sh
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -ti:5000

# Kill it
kill -9 $(lsof -ti:5000)
```

### Permission Issues
```bash
# Fix permissions
chmod -R 755 /home/fitsmart/htdocs/www.fitsmart.ca
chown -R fitsmart:fitsmart /home/fitsmart/htdocs/www.fitsmart.ca
```

### Database Issues
```bash
# Recreate database
source venv/bin/activate
python3 -c "from app import create_app; from database.models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### Module Not Found Errors
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Check installed packages
pip list

# Update requirements
pip freeze > requirements.txt

# Run database migrations (if using Flask-Migrate)
flask db upgrade
```

## Next Steps

1. ✅ Project is running
2. Configure domain in CloudPanel
3. Set up SSL certificate
4. Configure email settings
5. Set up payment gateways
6. Configure backups

Your application should now be running! 🚀

