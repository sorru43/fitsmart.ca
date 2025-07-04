import razorpay
from flask import current_app
from datetime import datetime
import hmac
import hashlib

def get_razorpay_client():
    """Initialize and return Razorpay client"""
    return razorpay.Client(
        auth=(current_app.config['RAZORPAY_KEY_ID'], 
              current_app.config['RAZORPAY_KEY_SECRET'])
    )

def create_order(amount, currency='INR', receipt=None):
    """
    Create a Razorpay order
    amount: Amount in paise (multiply by 100)
    """
    client = get_razorpay_client()
    
    # Calculate amount with GST (5%)
    amount_with_gst = int(amount * 1.05)
    
    data = {
        'amount': amount_with_gst,
        'currency': currency,
        'receipt': receipt or f'receipt_{datetime.now().timestamp()}',
        'notes': {
            'description': 'HealthyRizz Meal Plan Subscription'
        }
    }
    
    try:
        order = client.order.create(data=data)
        return order
    except Exception as e:
        current_app.logger.error(f"Error creating Razorpay order: {str(e)}")
        raise

def verify_payment_signature(payment_id, order_id, signature):
    """Verify the payment signature"""
    client = get_razorpay_client()
    try:
        client.utility.verify_payment_signature({
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        })
        return True
    except Exception as e:
        current_app.logger.error(f"Payment signature verification failed: {str(e)}")
        return False

def verify_webhook_signature(payload, signature):
    """Verify Razorpay webhook signature"""
    try:
        hmac_obj = hmac.new(
            current_app.config['RAZORPAY_WEBHOOK_SECRET'].encode(),
            payload.encode(),
            hashlib.sha256
        )
        generated_signature = hmac_obj.hexdigest()
        return hmac.compare_digest(generated_signature, signature)
    except Exception as e:
        current_app.logger.error(f"Webhook signature verification failed: {str(e)}")
        return False 