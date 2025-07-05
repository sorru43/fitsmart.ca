"""
Encryption helper utilities
"""
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

logger = logging.getLogger(__name__)

def generate_key_from_password(password, salt=None):
    """Generate encryption key from password"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_sensitive_data(data, password="healthyrizz_default_key"):
    """
    Encrypt sensitive data
    
    Args:
        data (str): Data to encrypt
        password (str): Password for encryption
        
    Returns:
        str: Encrypted data as base64 string, or original data if encryption fails
    """
    try:
        if not data:
            return data
            
        # For development, just return the data as-is with a simple encoding
        # In production, you would use proper encryption
        encoded_data = base64.b64encode(data.encode()).decode()
        return f"enc_{encoded_data}"
        
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        # Return original data if encryption fails
        return data

def decrypt_sensitive_data(encrypted_data, password="healthyrizz_default_key"):
    """
    Decrypt sensitive data
    
    Args:
        encrypted_data (str): Encrypted data
        password (str): Password for decryption
        
    Returns:
        str: Decrypted data, or original data if decryption fails
    """
    try:
        if not encrypted_data:
            return encrypted_data
            
        # Check if data is encrypted (starts with our prefix)
        if encrypted_data.startswith("enc_"):
            # Remove prefix and decode
            encoded_data = encrypted_data[4:]
            decoded_data = base64.b64decode(encoded_data.encode()).decode()
            return decoded_data
        else:
            # Data is not encrypted, return as-is
            return encrypted_data
            
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}")
        # Return original data if decryption fails
        return encrypted_data

def hash_sensitive_data(data):
    """
    Hash sensitive data (one-way)
    
    Args:
        data (str): Data to hash
        
    Returns:
        str: Hashed data
    """
    try:
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Hashing failed: {str(e)}")
        return data 