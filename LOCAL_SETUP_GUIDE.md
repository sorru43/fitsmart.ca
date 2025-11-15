# 🏥 FitSmart Local Development Setup

This guide will help you run the FitSmart Flask application locally on your machine.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (to clone the repository)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
python run_local.py
```

This script will:
- ✅ Check Python version
- ✅ Install dependencies
- ✅ Create .env file
- ✅ Initialize database
- ✅ Start the Flask server

### Option 2: Manual Setup

If you prefer to set up manually, follow these steps:

#### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Create Environment File

Create a `.env` file in the project root:

```env
# Local Development Environment Variables
DATABASE_URL=sqlite:///healthyrizz.db
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
SERVER_NAME=localhost:5000

# Mail Configuration (optional for local development)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Admin Configuration
ADMIN_EMAIL=admin@healthyrizz.in

# Razorpay Configuration (test keys)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# AI Configuration (optional)
PERPLEXITY_API_KEY=your-perplexity-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
```

#### 4. Initialize Database

```bash
python -c "
from app import app
from database.models import db
from database.models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    # Create admin user
    admin = User.query.filter_by(email='admin@healthyrizz.in').first()
    if not admin:
        admin = User(
            email='admin@healthyrizz.in',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created: admin@healthyrizz.in / admin123')
    else:
        print('Admin user already exists')
"
```

#### 5. Run the Application

```bash
# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export DEBUG=True

# Run Flask development server
python -m flask run --host=0.0.0.0 --port=5000 --debug
```

## 🌐 Access the Application

Once the server is running:

- **Main Application**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin
- **Admin Login**: admin@healthyrizz.in / admin123

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill process on port 5000
# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

#### 2. Database Issues
```bash
# Remove existing database and recreate
rm healthyrizz.db
python -c "from app import app; from database.models import db; app.app_context().push(); db.create_all()"
```

#### 3. CSRF Issues
The application has CSRF protection enabled. For local development, you can disable it by modifying `config.py`:

```python
WTF_CSRF_ENABLED = False
```

#### 4. Missing Dependencies
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Development Tips

1. **Auto-reload**: The Flask development server will automatically reload when you make changes to the code.

2. **Debug Mode**: Debug mode is enabled by default, showing detailed error messages.

3. **Database**: The application uses SQLite for local development, which is perfect for testing.

4. **Static Files**: Static files are served from the `static/` directory.

5. **Templates**: Templates are in the `templates/` directory.

## 📁 Project Structure

```
healthyrizz.in/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt        # Python dependencies
├── run_local.py           # Automated setup script
├── database/              # Database models and migrations
├── routes/                # Flask routes and views
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── forms/                 # Flask-WTF forms
├── utils/                 # Utility functions
└── .env                   # Environment variables (create this)
```

## 🛠️ Development Commands

```bash
# Run the application
python run_local.py

# Or manually:
export FLASK_APP=app.py
export FLASK_ENV=development
python -m flask run --debug

# Create database migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Run tests (if available)
python -m pytest

# Install new dependency
pip install package_name
pip freeze > requirements.txt
```

## 🔐 Security Notes

- The default admin password is `admin123` - change this in production
- The secret key in `.env` should be changed for production
- Never commit `.env` files to version control
- Use strong passwords for all accounts

## 📞 Support

If you encounter any issues:

1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure the database is properly initialized
4. Check that the `.env` file exists and has correct values

Happy coding! 🚀 