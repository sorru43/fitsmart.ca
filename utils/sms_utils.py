"""
sms_utils.py - Utilities for sending SMS messages via Twilio
"""

import os
import logging
from datetime import datetime
from twilio.rest import Client
from flask import current_app
from dotenv import load_dotenv

load_dotenv()

# Try to import Twilio client
try:
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("Twilio package not installed. SMS functionality will be disabled.")

# Get Twilio credentials from environment
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

# Check if Twilio credentials are set
TWILIO_CONFIGURED = all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER])

def get_twilio_client():
    """Initialize and return Twilio client"""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    return Client(account_sid, auth_token)

def send_sms(to_number, message):
    """Send SMS using Twilio"""
    try:
        client = get_twilio_client()
        message = client.messages.create(
            body=message,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=to_number
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send SMS: {str(e)}")
        return False

def send_delivery_notification(phone_number, delivery_date, delivery_time):
    """Send delivery notification SMS"""
    message = f"Your HealthyRizz delivery is scheduled for {delivery_date} at {delivery_time}. Please ensure someone is available to receive it."
    return send_sms(phone_number, message)

def send_subscription_confirmation(phone_number, customer_name, meal_plan_name, first_delivery_date):
    """Send subscription confirmation SMS"""
    # For development environments (like Replit), just log the message
    if os.environ.get('REPLIT_DEV_DOMAIN') or os.environ.get('REPLIT_DEPLOYMENT'):
        current_app.logger.info(f"[DEV SMS] To: {phone_number}")
        current_app.logger.info(f"[DEV SMS] Subject: HealthyRizz Subscription Confirmation")
        current_app.logger.info(f"[DEV SMS] Body: Thank you {customer_name} for subscribing to HealthyRizz {meal_plan_name} plan! Your first delivery is scheduled for {first_delivery_date}.")
        return True
    
    # For production, send an actual SMS
    message = f"Thank you {customer_name} for subscribing to HealthyRizz {meal_plan_name} plan! Your first delivery is scheduled for {first_delivery_date}."
    return send_sms(phone_number, message)

def send_subscription_reminder(phone_number, subscription_type, renewal_date):
    """Send subscription renewal reminder SMS"""
    message = f"Your HealthyRizz {subscription_type} subscription will renew on {renewal_date}. Please ensure your payment method is up to date."
    return send_sms(phone_number, message)

def send_payment_success_sms(phone_number, customer_name, meal_plan_name, amount, period_end):
    """Send payment success SMS for recurring subscription payment"""
    message = f"Hi {customer_name}! Your {meal_plan_name} subscription payment of ${amount:.2f} CAD was successful. Next billing: {period_end.strftime('%B %d, %Y')}. Thank you! - FitSmart"
    return send_sms(phone_number, message)

def send_payment_failed_sms(phone_number, customer_name, meal_plan_name, amount, attempt_count):
    """Send payment failed SMS for recurring subscription payment"""
    message = f"Hi {customer_name}! Payment failed for your {meal_plan_name} subscription (${amount:.2f} CAD). Attempt #{attempt_count}. Please update your payment method at fitsmart.ca/profile to avoid cancellation. - FitSmart"
    return send_sms(phone_number, message)

def send_payment_reminder_sms(phone_number, customer_name, meal_plan_name, amount, due_date):
    """Send payment reminder SMS before recurring payment"""
    message = f"Hi {customer_name}! Your {meal_plan_name} subscription will renew automatically on {due_date.strftime('%B %d, %Y')} for ${amount:.2f} CAD. Ensure your payment method is up to date. - FitSmart"
    return send_sms(phone_number, message)

def send_bulk_sms(recipients, message_generator_func, batch_size=10, batch_delay=2):
    """
    Send bulk SMS messages to a list of recipients with rate limiting
    
    Args:
        recipients (list): List of recipient objects (e.g., User or Subscription objects)
        message_generator_func (callable): Function that takes a recipient and returns a message
        batch_size (int): Number of messages to send in each batch
        batch_delay (int): Delay in seconds between batches
        
    Returns:
        tuple: (success_count, error_count, errors) where errors is a list of (recipient, error) tuples
    """
    import time
    
    success_count = 0
    error_count = 0
    errors = []
    
    # Process recipients in batches
    for i in range(0, len(recipients), batch_size):
        batch = recipients[i:i+batch_size]
        
        # Send messages to this batch
        for recipient in batch:
            try:
                # Generate message for this recipient
                message = message_generator_func(recipient)
                
                # Get phone number (assuming recipient has a 'phone' attribute)
                phone_number = getattr(recipient, 'phone', None)
                
                if not phone_number:
                    error_count += 1
                    errors.append((recipient, "No phone number available"))
                    continue
                
                # Send the SMS
                send_sms(phone_number, message)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append((recipient, str(e)))
                logging.error(f"Failed to send SMS to recipient: {str(e)}")
        
        # Delay between batches to avoid rate limits (but not after the last batch)
        if i + batch_size < len(recipients):
            time.sleep(batch_delay)
    
    return success_count, error_count, errors