"""
Timezone utilities for Indian Standard Time (IST)
"""
import pytz
from datetime import datetime, timezone
from flask import current_app

def get_ist_timezone():
    """Get Indian Standard Time timezone"""
    return pytz.timezone('Asia/Kolkata')

def get_current_ist_time():
    """Get current time in Indian Standard Time"""
    ist_tz = get_ist_timezone()
    return datetime.now(ist_tz)

def convert_to_ist(dt):
    """Convert a datetime object to Indian Standard Time"""
    if dt is None:
        return None
    
    # If datetime is naive (no timezone), assume it's UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    ist_tz = get_ist_timezone()
    return dt.astimezone(ist_tz)

def convert_from_ist(dt):
    """Convert a datetime object from Indian Standard Time to UTC"""
    if dt is None:
        return None
    
    # If datetime is naive (no timezone), assume it's IST
    if dt.tzinfo is None:
        ist_tz = get_ist_timezone()
        dt = ist_tz.localize(dt)
    
    return dt.astimezone(timezone.utc)

def format_ist_time(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object in IST with the specified format"""
    if dt is None:
        return None
    
    ist_dt = convert_to_ist(dt)
    return ist_dt.strftime(format_str)

def format_ist_date(dt, format_str='%d/%m/%Y'):
    """Format a date in IST with the specified format"""
    if dt is None:
        return None
    
    ist_dt = convert_to_ist(dt)
    return ist_dt.strftime(format_str)

def format_ist_time_only(dt, format_str='%I:%M %p'):
    """Format time only in IST with 12-hour format"""
    if dt is None:
        return None
    
    ist_dt = convert_to_ist(dt)
    return ist_dt.strftime(format_str)

def get_ist_now():
    """Get current IST datetime with timezone info"""
    return get_current_ist_time()

def get_ist_today():
    """Get today's date in IST"""
    return get_current_ist_time().date()

def is_delivery_time():
    """Check if current time is within delivery hours (6 AM to 10 PM IST)"""
    ist_now = get_current_ist_time()
    delivery_start = ist_now.replace(hour=6, minute=0, second=0, microsecond=0)
    delivery_end = ist_now.replace(hour=22, minute=0, second=0, microsecond=0)
    
    return delivery_start <= ist_now <= delivery_end

def get_delivery_time_range():
    """Get delivery time range in IST"""
    ist_now = get_current_ist_time()
    start_time = ist_now.replace(hour=6, minute=0, second=0, microsecond=0)
    end_time = ist_now.replace(hour=22, minute=0, second=0, microsecond=0)
    
    return start_time, end_time

def format_delivery_time_range():
    """Format delivery time range for display"""
    start_time, end_time = get_delivery_time_range()
    return f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')} IST"

def get_ist_weekday():
    """Get current weekday in IST (0=Monday, 6=Sunday)"""
    return get_current_ist_time().weekday()

def is_weekend():
    """Check if current day is weekend in IST"""
    weekday = get_ist_weekday()
    return weekday >= 5  # Saturday (5) or Sunday (6)

def get_next_delivery_date():
    """Get next delivery date (skip weekends)"""
    ist_now = get_current_ist_time()
    current_date = ist_now.date()
    
    # If today is weekend, find next Monday
    if is_weekend():
        days_until_monday = (7 - get_ist_weekday()) % 7
        if days_until_monday == 0:  # Already Monday
            days_until_monday = 7
        from datetime import timedelta
        return current_date + timedelta(days=days_until_monday)
    
    # If it's past delivery hours, deliver tomorrow
    if not is_delivery_time():
        from datetime import timedelta
        tomorrow = current_date + timedelta(days=1)
        # If tomorrow is weekend, deliver next Monday
        tomorrow_weekday = (get_ist_weekday() + 1) % 7
        if tomorrow_weekday >= 5:  # Weekend
            days_until_monday = (7 - tomorrow_weekday) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            return current_date + timedelta(days=days_until_monday)
        return tomorrow
    
    return current_date

def format_relative_time(dt):
    """Format relative time (e.g., '2 hours ago', 'yesterday')"""
    if dt is None:
        return "Unknown"
    
    ist_dt = convert_to_ist(dt)
    ist_now = get_current_ist_time()
    
    diff = ist_now - ist_dt
    
    if diff.days > 0:
        if diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            return format_ist_date(ist_dt)
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now" 