"""
Authentication utility functions
"""
import secrets
import logging
from flask import current_app, url_for
from flask_mail import Message
from extensions import mail

logger = logging.getLogger(__name__)

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def send_verification_email(user_email, verification_token=None):
    """
    Send verification email to user
    """
    try:
        if not verification_token:
            verification_token = generate_verification_token()
        
        # For now, just log the email (since email might not be configured)
        logger.info(f"Verification email would be sent to {user_email} with token {verification_token}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user_email}: {str(e)}")
        return False

def send_password_reset_email(user_email, reset_token):
    """
    Send password reset email to user
    """
    try:
        # For now, just log the email (since email might not be configured)
        logger.info(f"Password reset email would be sent to {user_email} with token {reset_token}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user_email}: {str(e)}")
        return False 