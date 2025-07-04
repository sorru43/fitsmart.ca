# HealthyRizz Server Requirements

## Server Requirements

1. **Operating System**
   - Ubuntu 20.04 LTS, 22.04 LTS, or 24.04 LTS
   - Compatible with Hostinger VPS running CloudPanel

2. **Web Server**
   - Nginx (for reverse proxy and static file serving)
   - Configured with proper worker connections and buffer sizes

3. **Application Server**
   - Gunicorn (4+ workers recommended)
   - Configured with timeout settings appropriate for your workload

4. **Database**
   - PostgreSQL 12+ (recommended: PostgreSQL 14 or newer)
   - Properly configured for production use with appropriate connection pooling

5. **Python Environment**
   - Python 3.8+ (recommended: Python 3.10 or 3.12)
   - Virtual environment for dependency isolation
   - Required system packages for building Python extensions

6. **SSL/TLS**
   - Let's Encrypt certificates for HTTPS
   - Auto-renewal configured properly

7. **System Resources**
   - Minimum 1 CPU core (2+ recommended)
   - Minimum 2GB RAM (4GB+ recommended)
   - At least 10GB of available disk space

8. **Networking**
   - Firewall configured (allow ports 80, 443, and SSH)
   - Rate limiting for API endpoints
   - DDoS protection if possible

## Python Package Requirements

```
Flask==2.3.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
Flask-Limiter==3.5.0
Flask-Mail==0.9.1
WTForms==3.1.1
email-validator==2.1.0.post1
python-dotenv==1.0.0
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23
gunicorn==21.2.0
pandas==2.1.3
fpdf==1.7.2
cryptography==41.0.5
stripe==7.6.0
twilio==8.9.1
sendgrid==6.10.0
Werkzeug==2.3.7
Jinja2==3.1.2
```

## External Service Requirements

1. **Stripe Integration**
   - Stripe account with API keys
   - Webhook endpoint configured
   - Required environment variables:
     - `STRIPE_SECRET_KEY`
     - `STRIPE_WEBHOOK_SECRET`

2. **Twilio Integration (for SMS notifications)**
   - Twilio account with API credentials
   - Phone number for sending SMS
   - Required environment variables:
     - `TWILIO_ACCOUNT_SID`
     - `TWILIO_AUTH_TOKEN`
     - `TWILIO_PHONE_NUMBER`

3. **SendGrid Integration (for email notifications)**
   - SendGrid account with API key
   - Verified sender identity
   - Required environment variables:
     - `SENDGRID_API_KEY`

## CloudPanel Specific Requirements

1. **Database Configuration**
   - CloudPanel PostgreSQL database (recommended naming: `cp_healthyrizz_db`)
   - Database user with appropriate permissions (recommended: `cp_healthyrizz_user`)

2. **Directory Structure**
   - Application files in `/var/www/healthyrizz/` or CloudPanel web directory path
   - Static files in subdirectory `static/`
   - Template files in subdirectory `templates/`

3. **Domain Configuration**
   - Properly configured DNS records pointing to your server
   - Domain added to CloudPanel
   - PHP version set to "no PHP" for the domain

4. **SSL/TLS**
   - SSL certificate issued through CloudPanel interface or Let's Encrypt

## System Configuration

1. **Service Configuration**
   - Systemd service for automatic application startup
   - Proper user permissions (typically www-data or cloudpanel user)
   - Log rotation configured
   - Monitoring setup (optional but recommended)

2. **Environment Variables**
   - Properly configured in `.env` file or system environment
   - Include all necessary database credentials, API keys, and application settings
   - `SESSION_SECRET` for Flask secret key
