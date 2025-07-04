"""
crypto_utils.py - Encryption utilities for sensitive data
"""
import os
from cryptography.fernet import Fernet

# Get or generate an encryption key
def get_encryption_key():
    # Check if the key exists in environment variables
    key = os.environ.get('ENCRYPTION_KEY')
    
    if not key:
        # For development/testing only - in production, use a securely stored key
        key = Fernet.generate_key().decode()
        # In a real deployment, you would store this key securely
        # and not regenerate it each time
    
    return key.encode() if isinstance(key, str) else key

# Initialize the Fernet cipher
cipher_suite = Fernet(get_encryption_key())

def encrypt_data(data):
    """
    Encrypt sensitive data
    
    Args:
        data (str): The data to encrypt
        
    Returns:
        str: The encrypted data as a string
    """
    if not data:
        return None
        
    return cipher_suite.encrypt(data.encode()).decode()
    
def decrypt_data(encrypted_data):
    """
    Decrypt sensitive data
    
    Args:
        encrypted_data (str): The encrypted data to decrypt
        
    Returns:
        str: The decrypted data
    """
    if not encrypted_data:
        return None
        
    return cipher_suite.decrypt(encrypted_data.encode()).decode()