"""
Stripe payment integration utility functions for HealthyRizz meal delivery application.
"""
import os
import logging
import stripe
from datetime import datetime, timedelta
from flask import current_app

# Initialize Stripe with API key from environment variable
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Constants
CURRENCY = 'usd'

def create_stripe_customer(name, email, phone, address):
    """
    Create a Stripe customer with the given information.
    
    Args:
        name (str): Customer's full name
        email (str): Customer's email address
        phone (str): Customer's phone number
        address (dict): Customer's address information
        
    Returns:
        str: Stripe customer ID if successful, None otherwise
    """
    try:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        customer = stripe.Customer.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            metadata={
                'source': 'website'
            }
        )
        
        return customer.id
    except Exception as e:
        logging.error(f"Error creating Stripe customer: {str(e)}")
        return None

def create_stripe_checkout_session(customer_id, meal_plan_name, price_amount, frequency, success_url, cancel_url):
    """
    Create a Stripe checkout session for subscription payment.
    
    Args:
        customer_id (str): Stripe customer ID
        meal_plan_name (str): Name of the meal plan
        price_amount (float): Price amount in dollars
        frequency (str): Subscription frequency ('weekly' or 'monthly')
        success_url (str): URL to redirect to on successful payment
        cancel_url (str): URL to redirect to on cancelled payment
        
    Returns:
        dict: Stripe checkout session data if successful, None otherwise
    """
    try:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        # Create a price object for the subscription
        price = stripe.Price.create(
            unit_amount=int(price_amount * 100),  # Convert to cents
            currency='cad',
            recurring={
                'interval': 'week' if frequency == 'weekly' else 'month'
            },
            product_data={
                'name': f"{meal_plan_name} - {frequency.title()} Plan",
                'description': f"Subscription to {meal_plan_name} ({frequency} delivery)"
            }
        )
        
        # Create the checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price.id,
                'quantity': 1
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'meal_plan_name': meal_plan_name,
                'frequency': frequency
            }
        )
        
        return {
            'id': session.id,
            'url': session.url
        }
    except Exception as e:
        logging.error(f"Error creating Stripe checkout session: {str(e)}")
        return None

def retrieve_subscription(subscription_id):
    """
    Retrieve subscription details from Stripe.
    
    Args:
        subscription_id (str): Stripe subscription ID
        
    Returns:
        dict: Subscription details if successful, None otherwise
    """
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription
    except Exception as e:
        logging.error(f"Error retrieving Stripe subscription: {str(e)}")
        return None

def cancel_subscription(subscription_id, cancel_at_period_end=True):
    """
    Cancel a Stripe subscription.
    
    Args:
        subscription_id (str): Stripe subscription ID
        cancel_at_period_end (bool): Whether to cancel at the end of the billing period
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if cancel_at_period_end:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        else:
            stripe.Subscription.delete(subscription_id)
        return True
    except Exception as e:
        logging.error(f"Error cancelling Stripe subscription: {str(e)}")
        return False

def pause_subscription(subscription_id):
    """
    Pause a Stripe subscription by setting billing_cycle_anchor to far future.
    
    Args:
        subscription_id (str): Stripe subscription ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the subscription
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Pause collection by setting pause_collection
        stripe.Subscription.modify(
            subscription_id,
            pause_collection={
                'behavior': 'void'
            }
        )
        
        return True
    except Exception as e:
        logging.error(f"Error pausing Stripe subscription: {str(e)}")
        return False

def resume_subscription(subscription_id):
    """
    Resume a paused Stripe subscription.
    
    Args:
        subscription_id (str): Stripe subscription ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Remove the pause_collection to resume the subscription
        stripe.Subscription.modify(
            subscription_id,
            pause_collection=''
        )
        
        return True
    except Exception as e:
        logging.error(f"Error resuming Stripe subscription: {str(e)}")
        return False

def create_portal_session(customer_id, return_url):
    """
    Create a Stripe customer portal session for subscription management.
    
    Args:
        customer_id (str): Stripe customer ID
        return_url (str): URL to redirect after the portal session
        
    Returns:
        str: URL to the customer portal if successful, None otherwise
    """
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url
        )
        return session.url
    except Exception as e:
        logging.error(f"Error creating Stripe portal session: {str(e)}")
        return None

def handle_webhook_event(payload, signature, webhook_secret):
    """
    Handle Stripe webhook events for subscription lifecycle management.
    
    Args:
        payload (str): The raw payload of the webhook event
        signature (str): The signature header from Stripe
        webhook_secret (str): The webhook secret for validation
        
    Returns:
        dict: The event data if signature is valid, None otherwise
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        return event
    except ValueError as e:
        # Invalid payload
        logging.error(f"Invalid payload in Stripe webhook: {str(e)}")
        return None
    except stripe.SignatureVerificationError as e:
        # Invalid signature
        logging.error(f"Invalid signature in Stripe webhook: {str(e)}")
        return None
    except Exception as e:
        # Other errors
        logging.error(f"Error processing Stripe webhook: {str(e)}")
        return None
