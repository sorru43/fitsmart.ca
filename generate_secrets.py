#!/usr/bin/env python3
"""
Secure Secret Generator for HealthyRizz
Generates cryptographically secure secrets for production use
"""

import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure secret key"""
    return secrets.token_hex(length)

def generate_password(length=16):
    """Generate a secure password with mixed characters"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_all_secrets():
    """Generate all required secrets for the application"""
    secrets_config = {
        'SECRET_KEY': generate_secret_key(32),
        'WTF_CSRF_SECRET_KEY': generate_secret_key(32),
        'RAZORPAY_WEBHOOK_SECRET': generate_secret_key(24),
        'DATABASE_ENCRYPTION_KEY': generate_secret_key(32),
        'SESSION_ENCRYPTION_KEY': generate_secret_key(32),
    }
    
    return secrets_config

def main():
    """Main function to generate and display secrets"""
    print("🔐 HealthyRizz Security Secret Generator")
    print("=" * 50)
    print("⚠️  IMPORTANT: Save these secrets securely and never commit them to version control!")
    print("=" * 50)
    
    secrets_config = generate_all_secrets()
    
    print("\n📋 Copy these to your .env file:")
    print("-" * 30)
    
    for key, value in secrets_config.items():
        print(f"{key}={value}")
    
    print("\n🔒 Additional Security Recommendations:")
    print("- Store these secrets in environment variables on your server")
    print("- Use a password manager to store these values")
    print("- Rotate secrets regularly")
    print("- Never share these values via email or messaging")
    print("- In production, use a secrets management service (AWS Secrets Manager, etc.)")
    
    print("\n✨ Generate new passwords for:")
    print(f"- Email app password: {generate_password(16)}")
    print(f"- Database admin password: {generate_password(20)}")
    print(f"- Redis password: {generate_password(16)}")

if __name__ == "__main__":
    main() 