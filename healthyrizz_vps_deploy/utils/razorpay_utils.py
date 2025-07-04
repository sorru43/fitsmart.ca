"""
Razorpay payment integration utility functions for HealthyRizz meal delivery application.
"""
import os
import logging
import razorpay
from datetime import datetime, timedelta
from flask import current_app

# Initialize Razorpay client
client = razorpay.Client(
    auth=(os.environ.get('RAZORPAY_KEY_ID'), os.environ.get('RAZORPAY_KEY_SECRET'))
)

def create_razorpay_order(amount, currency="INR", receipt=None, notes=None):
    """
    Create a Razorpay order.
    
    Args:
        amount (int): Amount in paise (multiply by 100)
        currency (str): Currency code (default: INR)
        receipt (str): Receipt ID for the order
        notes (dict): Additional notes for the order
        
    Returns:
        dict: Razorpay order data if successful, None otherwise
    """
    try:
        data = {
            'amount': amount,
            'currency': currency,
            'receipt': receipt,
            'notes': notes or {}
        }
        
        order = client.order.create(data=data)
        return order
    except Exception as e:
        logging.error(f"Error creating Razorpay order: {str(e)}")
        return None

def verify_payment_signature(order_id, payment_id, signature):
    """
    Verify the payment signature from Razorpay.
    
    Args:
        order_id (str): Razorpay order ID
        payment_id (str): Razorpay payment ID
        signature (str): Payment signature from Razorpay
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        client.utility.verify_payment_signature(params_dict)
        return True
    except Exception as e:
        logging.error(f"Error verifying Razorpay payment signature: {str(e)}")
        return False

def create_razorpay_customer(name, email, contact):
    """
    Create a Razorpay customer.
    
    Args:
        name (str): Customer's full name
        email (str): Customer's email address
        contact (str): Customer's phone number
        
    Returns:
        dict: Razorpay customer data if successful, None otherwise
    """
    try:
        data = {
            'name': name,
            'email': email,
            'contact': contact
        }
        
        customer = client.customer.create(data=data)
        return customer
    except Exception as e:
        logging.error(f"Error creating Razorpay customer: {str(e)}")
        return None

def get_razorpay_key():
    """
    Get the Razorpay key ID for client-side integration.
    
    Returns:
        str: Razorpay key ID
    """
    return os.environ.get('RAZORPAY_KEY_ID') 
