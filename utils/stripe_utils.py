"""
Stripe payment integration utility functions for FitSmart meal delivery application.
"""
import os
import logging
import stripe
from datetime import datetime, timedelta
from flask import current_app

# Constants
CURRENCY = 'cad'  # Canadian Dollar

def get_stripe_api_key():
    """
    Get Stripe API key from config or environment variable.
    """
    api_key = None
    
    # Try to get from Flask app config first
    try:
        if current_app:
            api_key = current_app.config.get('STRIPE_SECRET_KEY')
            if api_key:
                return api_key
    except RuntimeError:
        # Outside of application context
        pass
    
    # Fall back to environment variable
    api_key = os.environ.get('STRIPE_SECRET_KEY')
    
    # Log warning if key is not found (but don't spam logs)
    if not api_key:
        logging.warning("STRIPE_SECRET_KEY not found in config or environment variables. Please add it to your .env file.")
    
    return api_key

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
        api_key = get_stripe_api_key()
        if not api_key:
            logging.error("Stripe API key not configured - check STRIPE_SECRET_KEY in environment variables")
            return None
        
        stripe.api_key = api_key
        
        # Prepare customer data - make phone and address optional
        customer_data = {
            'name': name,
            'email': email,
            'metadata': {
                'source': 'website'
            }
        }
        
        # Add phone if provided
        if phone:
            customer_data['phone'] = phone
        
        # Add address if provided and properly formatted
        if address:
            # Ensure address is a dict and has required fields
            if isinstance(address, dict):
                # Stripe requires at least line1 for address
                if address.get('line1') or address.get('line_1'):
                    customer_data['address'] = {
                        'line1': address.get('line1') or address.get('line_1', ''),
                        'city': address.get('city', ''),
                        'state': address.get('state', ''),
                        'postal_code': address.get('postal_code', ''),
                        'country': address.get('country', 'CA')
                    }
        
        customer = stripe.Customer.create(**customer_data)
        
        logging.info(f"Successfully created Stripe customer: {customer.id}")
        return customer.id
    except stripe.error.StripeError as e:
        # Stripe-specific errors
        error_msg = f"Stripe API error creating customer: {e.user_message or str(e)} (Code: {e.code})"
        logging.error(error_msg)
        return None
    except Exception as e:
        # Other errors
        error_msg = f"Error creating Stripe customer: {str(e)} (Type: {type(e).__name__})"
        logging.error(error_msg)
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
        api_key = get_stripe_api_key()
        if not api_key:
            logging.error("Stripe API key not configured")
            return None
        
        stripe.api_key = api_key
        
        # Create a price object for the subscription
        # Note: product_data only accepts 'name', not 'description'
        price = stripe.Price.create(
            unit_amount=int(price_amount * 100),  # Convert to cents
            currency='cad',
            recurring={
                'interval': 'week' if frequency == 'weekly' else 'month'
            },
            product_data={
                'name': f"{meal_plan_name} - {frequency.title()} Plan"
            }
        )
        
        # Create the checkout session
        # Note: Stripe will replace {CHECKOUT_SESSION_ID} with the actual session ID
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price.id,
                'quantity': 1
            }],
            mode='subscription',
            success_url=success_url,  # Should include ?session_id={CHECKOUT_SESSION_ID}
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
    except stripe.error.StripeError as e:
        # Stripe-specific errors
        error_msg = f"Stripe API error creating checkout session: {e.user_message or str(e)} (Code: {e.code}, Type: {type(e).__name__})"
        logging.error(error_msg)
        logging.error(f"Stripe error details: {e}")
        return None
    except Exception as e:
        # Other errors
        error_msg = f"Error creating Stripe checkout session: {str(e)} (Type: {type(e).__name__})"
        logging.error(error_msg)
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
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
        api_key = get_stripe_api_key()
        if not api_key:
            logging.error("Stripe API key not configured")
            return None
        
        stripe.api_key = api_key
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
        api_key = get_stripe_api_key()
        if not api_key:
            logging.error("Stripe API key not configured")
            return False
        
        stripe.api_key = api_key
        
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
        api_key = get_stripe_api_key()
        if not api_key:
            logging.error("Stripe API key not configured")
            return False
        
        stripe.api_key = api_key
        
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
        api_key = get_stripe_api_key()
        if not api_key:
            logging.error("Stripe API key not configured")
            return False
        
        stripe.api_key = api_key
        
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
        api_key = get_stripe_api_key()
        if not api_key:
            logging.error("Stripe API key not configured")
            return None
        
        stripe.api_key = api_key
        
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
        # Note: Webhook signature verification doesn't require API key
        # but we'll set it if available for consistency
        api_key = get_stripe_api_key()
        if api_key:
            stripe.api_key = api_key
        
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
