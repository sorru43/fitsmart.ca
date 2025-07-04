"""
validation_utils.py - Input validation utilities
"""
import re
from email_validator import validate_email, EmailNotValidError
from werkzeug.utils import escape

def is_valid_email(email):
    """
    Validate an email address
    
    Args:
        email (str): The email address to validate
        
    Returns:
        bool: True if the email is valid, False otherwise
    """
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def is_valid_phone(phone):
    """
    Validate a phone number (North American format)
    
    Args:
        phone (str): The phone number to validate
        
    Returns:
        bool: True if the phone number is valid, False otherwise
    """
    # Remove all non-numeric characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid format (10 digits, or 11 digits starting with 1)
    if len(digits_only) == 10:
        return True
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return True
    
    return False

def is_valid_postal_code(postal_code):
    """
    Validate a Canadian postal code
    
    Args:
        postal_code (str): The postal code to validate
        
    Returns:
        bool: True if the postal code is valid, False otherwise
    """
    # Canadian postal codes are in the format A1A 1A1
    pattern = r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$'
    return bool(re.match(pattern, postal_code))

def format_postal_code(postal_code):
    """
    Format a postal code to the standard format (A1A 1A1)
    
    Args:
        postal_code (str): The postal code to format
        
    Returns:
        str: The formatted postal code
    """
    # Remove all non-alphanumeric characters
    postal_code = re.sub(r'[^a-zA-Z0-9]', '', postal_code).upper()
    
    # Format as A1A 1A1
    if len(postal_code) == 6:
        return f"{postal_code[:3]} {postal_code[3:]}"
    
    return postal_code

def validate_and_sanitize_input(input_data, required_fields=None, max_lengths=None, field_validators=None):
    """
    Validate and sanitize form input data
    
    Args:
        input_data (dict): The input data to validate
        required_fields (list): List of fields that must be present and non-empty
        max_lengths (dict): Dictionary mapping field names to their maximum allowed lengths
        field_validators (dict): Dictionary mapping field names to validation functions
        
    Returns:
        tuple: (validated_data, errors) where validated_data is a dictionary of 
               sanitized data and errors is a dictionary of error messages
    """
    validated_data = {}
    errors = {}
    
    # Initialize with default values if None
    required_fields = required_fields or []
    max_lengths = max_lengths or {}
    field_validators = field_validators or {}
    
    # Check all input data
    for field, value in input_data.items():
        # Sanitize the input (removes potentially dangerous HTML)
        if isinstance(value, str):
            value = escape(value.strip())
        
        # Check required fields
        if field in required_fields and (value is None or value == ''):
            errors[field] = f"{field.replace('_', ' ').title()} is required"
            continue
            
        # Check maximum lengths
        if field in max_lengths and isinstance(value, str) and len(value) > max_lengths[field]:
            errors[field] = f"{field.replace('_', ' ').title()} exceeds maximum length of {max_lengths[field]}"
            continue
            
        # Apply custom validators
        if field in field_validators and value:
            validator = field_validators[field]
            if not validator(value):
                errors[field] = f"{field.replace('_', ' ').title()} is invalid"
                continue
                
        # If all checks pass, add to validated data
        validated_data[field] = value
    
    # Check that all required fields are present
    for field in required_fields:
        if field not in input_data:
            errors[field] = f"{field.replace('_', ' ').title()} is required"
    
    return validated_data, errors