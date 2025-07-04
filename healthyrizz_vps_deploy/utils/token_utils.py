"""
Token generation and verification utilities
"""
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_password_reset_token(user):
    """Generate a password reset token for the given user"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user.email, salt='password-reset-salt') 