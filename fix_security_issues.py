#!/usr/bin/env python3
"""
HealthyRizz Security Fix Script
Automatically fixes critical security vulnerabilities
"""

import os
import re
import sys
import subprocess
from pathlib import Path

class SecurityFixer:
    def __init__(self):
        self.project_root = Path(".")
        self.issues_fixed = []
        self.issues_failed = []
    
    def log_fix(self, issue, status="FIXED"):
        if status == "FIXED":
            self.issues_fixed.append(issue)
            print(f"✅ {issue}")
        else:
            self.issues_failed.append(issue)
            print(f"❌ {issue}")
    
    def create_gitignore(self):
        """Create or update .gitignore to protect sensitive files"""
        gitignore_content = """
# Environment variables
.env
.env.local
.env.production
.env.staging

# Secret files
secrets.txt
config_secrets.py

# Database files
*.db
*.sqlite
*.sqlite3

# Session files
flask_session/

# Log files
*.log
logs/

# Backup files
*.bak
*.backup

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# Testing
.coverage
.pytest_cache/

# Uploads
static/uploads/
uploads/
"""
        try:
            with open(".gitignore", "w") as f:
                f.write(gitignore_content)
            self.log_fix("Created secure .gitignore file")
        except Exception as e:
            self.log_fix(f"Failed to create .gitignore: {e}", "FAILED")
    
    def create_development_env(self):
        """Create a development .env file with secure defaults"""
        dev_env = f"""# HealthyRizz Development Environment
# DO NOT USE THESE VALUES IN PRODUCTION!

# Security Keys (CHANGE THESE!)
SECRET_KEY={os.urandom(32).hex()}
WTF_CSRF_SECRET_KEY={os.urandom(32).hex()}

# Environment
FLASK_ENV=development
DEBUG=True

# Database
DATABASE_URL=sqlite:///healthyrizz.db

# Email (Configure with your Gmail app password)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Payment (Test keys only)
RAZORPAY_KEY_ID=your-test-key
RAZORPAY_KEY_SECRET=your-test-secret
RAZORPAY_WEBHOOK_SECRET=your-test-webhook-secret

# Redis
REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/1

# Security Settings (Development)
SESSION_COOKIE_SECURE=False
WTF_CSRF_SSL_STRICT=False
PERMANENT_SESSION_LIFETIME=1800
"""
        
        try:
            if not os.path.exists(".env"):
                with open(".env", "w") as f:
                    f.write(dev_env)
                self.log_fix("Created development .env file")
            else:
                self.log_fix(".env file already exists")
                
        except Exception as e:
            self.log_fix(f"Failed to create .env file: {e}", "FAILED")
    
    def fix_all(self):
        """Run all security fixes"""
        print("🔒 HealthyRizz Security Fixer")
        print("=" * 50)
        
        self.create_gitignore()
        self.create_development_env()
        
        print("\\n" + "=" * 50)
        print(f"✅ Fixed {len(self.issues_fixed)} security issues")
        if self.issues_failed:
            print(f"❌ Failed to fix {len(self.issues_failed)} issues")
            for issue in self.issues_failed:
                print(f"   - {issue}")
        
        print("\\n🔒 IMPORTANT NEXT STEPS:")
        print("1. Run: python generate_secrets.py")
        print("2. Update your .env file with real secrets")
        print("3. Install missing dependencies: pip install -r requirements.txt")
        print("4. Test the application: python main.py")
        print("5. Never commit .env files to version control!")

if __name__ == "__main__":
    fixer = SecurityFixer()
    fixer.fix_all() 