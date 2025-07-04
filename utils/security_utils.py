"""
security_utils.py - Security utilities for the application
"""
import re
from functools import wraps
from flask import abort, request, current_app, session
import ipaddress

def is_ip_trusted(ip, trusted_ips=None, trusted_ranges=None):
    """
    Check if an IP address is in the trusted list or ranges
    
    Args:
        ip (str): The IP address to check
        trusted_ips (list): List of trusted IP addresses
        trusted_ranges (list): List of trusted IP CIDR ranges
        
    Returns:
        bool: True if the IP is trusted, False otherwise
    """
    trusted_ips = trusted_ips or []
    trusted_ranges = trusted_ranges or []
    
    # Convert string IP to an IP address object
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        return False  # Invalid IP
    
    # Check if the IP is in the trusted list
    if ip in trusted_ips:
        return True
    
    # Check if the IP is in any of the trusted ranges
    for cidr_range in trusted_ranges:
        try:
            if ip_obj in ipaddress.ip_network(cidr_range):
                return True
        except ValueError:
            continue  # Invalid CIDR range
    
    return False

def protect_admin_route(trusted_ips=None, trusted_ranges=None):
    """
    Decorator to restrict access to admin routes by IP
    
    Args:
        trusted_ips (list): List of trusted IP addresses
        trusted_ranges (list): List of trusted IP CIDR ranges
        
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            
            # First check if the user is logged in and is an admin
            if 'user_id' not in session:
                return abort(403)
            
            # Then check if the IP is trusted
            if not is_ip_trusted(client_ip, trusted_ips, trusted_ranges):
                # Log the attempt
                current_app.logger.warning(f"Admin access attempt from untrusted IP: {client_ip}")
                return abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_html(html):
    """
    Sanitize HTML content by removing potentially dangerous tags and attributes
    
    Args:
        html (str): The HTML content to sanitize
        
    Returns:
        str: The sanitized HTML
    """
    if not html:
        return ''
    
    # Remove script tags and their content
    html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
    
    # Remove onclick, onload, etc. attributes
    html = re.sub(r'on\w+=".*?"', '', html)
    html = re.sub(r"on\w+='.*?'", '', html)
    
    # Remove javascript: URLs
    html = re.sub(r'href="javascript:.*?"', 'href="#"', html)
    html = re.sub(r"href='javascript:.*?'", "href='#'", html)
    
    return html