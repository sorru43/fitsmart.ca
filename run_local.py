#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run FitSmart Locally
=======================
This script will help you run the FitSmart Flask application locally.
"""

import os
import sys
import subprocess
import platform
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_virtual_environment():
    """Check if virtual environment is activated"""
    print("\n🔧 Checking virtual environment...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is activated")
        return True
    else:
        print("⚠️ Virtual environment not detected")
        print("💡 Consider creating a virtual environment:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create a .env file for local development"""
    print("\n📝 Creating .env file for local development...")
    
    env_content = """# Local Development Environment Variables
# Database Configuration
DATABASE_URL=sqlite:///fitsmart.db

# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
SERVER_NAME=localhost:5000

# Mail Configuration (optional for local development)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=info@fitsmart.ca

# Admin Configuration
ADMIN_EMAIL=admin@fitsmart.ca

# Stripe Configuration (test keys for local development)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Razorpay Configuration (Deprecated - kept for backward compatibility)
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=

# Google OAuth Configuration (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# AI Configuration (optional)
PERPLEXITY_API_KEY=your-perplexity-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("📝 Please edit .env file with your actual credentials")
    else:
        print("✅ .env file already exists")

def initialize_database():
    """Initialize the database"""
    print("\n🗄️ Initializing database...")
    try:
        from app import app
        from database.models import db
        
        with app.app_context():
            db.create_all()
            print("✅ Database initialized successfully")
            
            # Create admin user if it doesn't exist
            from database.models import User
            admin = User.query.filter_by(email='admin@fitsmart.ca').first()
            if not admin:
                from werkzeug.security import generate_password_hash
                admin = User(
                    email='admin@fitsmart.ca',
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True,
                    is_active=True,
                    name='Admin User'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created (email: admin@fitsmart.ca, password: admin123)")
            else:
                print("✅ Admin user already exists")
                
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    return True

def run_flask_app():
    """Run the Flask application"""
    print("\n🚀 Starting Flask application...")
    print("🌐 The application will be available at: http://localhost:5000")
    print("👤 Admin login: admin@fitsmart.ca / admin123")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Set environment variables for local development
        os.environ['FLASK_APP'] = 'app.py'
        os.environ['FLASK_ENV'] = 'development'
        os.environ['DEBUG'] = 'True'
        
        # Run Flask development server
        subprocess.run([sys.executable, "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")

def main():
    """Main function to set up and run the application"""
    print("🏥 FitSmart Local Development Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check virtual environment
    check_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create .env file
    create_env_file()
    
    # Initialize database
    if not initialize_database():
        return
    
    # Run the application
    run_flask_app()

if __name__ == "__main__":
    main() 