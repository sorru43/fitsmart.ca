# HealthyRizz Application

## Deployment Instructions

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- Redis server
- Systemd (for service management)

### Environment Setup
1. Create a `.env` file in the root directory with the following variables:
```env
FLASK_APP=main.py
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/healthyrizz
REDIS_URL=redis://localhost:6379/0
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
```

### Deployment Steps
1. Clone the repository:
```bash
git clone <repository-url>
cd healthyrizz
```

2. Make the deployment script executable:
```bash
chmod +x deploy.sh
```

3. Run the deployment script:
```bash
./deploy.sh
```

4. Configure your web server (Nginx/Apache) to proxy requests to `http://127.0.0.1:8000`

### Service Management
- Start the service: `sudo systemctl start healthyrizz`
- Stop the service: `sudo systemctl stop healthyrizz`
- Restart the service: `sudo systemctl restart healthyrizz`
- Check service status: `sudo systemctl status healthyrizz`
- View logs: `sudo journalctl -u healthyrizz`

### Database Setup
1. Create the database:
```sql
CREATE DATABASE healthyrizz;
```

2. Initialize the database:
```bash
flask db upgrade
```

### Redis Setup
1. Install Redis:
```bash
sudo apt-get install redis-server
```

2. Start Redis:
```bash
sudo systemctl start redis-server
```

### Troubleshooting
- Check application logs: `sudo journalctl -u healthyrizz -f`
- Check Redis status: `sudo systemctl status redis-server`
- Verify database connection: `psql -U postgres -d healthyrizz`

### Backup
Regular backups are recommended:
1. Database backup:
```bash
pg_dump -U postgres healthyrizz > backup.sql
```

2. Application files backup:
```bash
tar -czf healthyrizz_backup.tar.gz /var/www/healthyrizz
``` 
