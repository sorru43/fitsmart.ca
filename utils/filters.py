from datetime import datetime
from flask import current_app
from decimal import Decimal

def timeago(date):
    """Convert datetime to human readable time ago string"""
    if not date:
        return ''
    
    now = datetime.utcnow()
    diff = now - date
    
    if diff.days > 365:
        years = diff.days // 365
        return f'{years} year{"s" if years > 1 else ""} ago'
    elif diff.days > 30:
        months = diff.days // 30
        return f'{months} month{"s" if months > 1 else ""} ago'
    elif diff.days > 0:
        return f'{diff.days} day{"s" if diff.days > 1 else ""} ago'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    else:
        return 'just now'

def multiply_decimal(value, multiplier):
    """Multiply a Decimal value with a float multiplier"""
    if isinstance(value, Decimal):
        return float(value) * multiplier
    return value * multiplier 