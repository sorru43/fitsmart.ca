"""
Stripe payment integration routes for HealthyRizz meal delivery application.
"""
import os
import json
import logging
from flask import request, jsonify, redirect, url_for, flash, render_template, session, current_app
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Import app instance from main.py
from main import app, db
from database.models import User, Subscription, MealPlan, SubscriptionFrequency, SubscriptionStatus
from utils.stripe_utils import (
    create_stripe_customer,
    create_stripe_checkout_session,
    retrieve_subscription,
    cancel_subscription,
    pause_subscription,
    resume_subscription,
    create_portal_session,
    handle_webhook_event
)

@app.route('/stripe-create-checkout-session/<int:plan_id>', methods=['POST'])
def stripe_create_checkout_session(plan_id):
    """
    Create a Stripe checkout session for subscription payment.
    """
    try:
        # Get the meal plan
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
        # Get form data
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        customer_address = request.form.get('customer_address')
        customer_city = request.form.get('customer_city')
        customer_postal_code = request.form.get('customer_postal_code')
        delivery_instructions = request.form.get('delivery_instructions', '')
        frequency = request.form.get('frequency', 'weekly')
        vegetarian_days = request.form.get('vegetarian_days', '')
        total_price = request.form.get('total_price')
        
        # Validate required fields
        if not all([customer_name, customer_email, customer_phone, 
                  customer_address, customer_city, customer_postal_code]):
            flash('Please fill out all required fields', 'danger')
            return redirect(url_for('main.meal_plan_checkout', plan_id=plan_id))
        
        # Store checkout data in session for later use
        session['checkout_data'] = {
            'plan_id': plan_id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'customer_address': customer_address,
            'customer_city': customer_city,
            'customer_postal_code': customer_postal_code,
            'delivery_instructions': delivery_instructions,
            'frequency': frequency,
            'vegetarian_days': vegetarian_days,
            'price': float(total_price) if total_price else (
                float(meal_plan.price_weekly) if frequency == 'weekly' else float(meal_plan.price_monthly)
            )
        }
        
        # Check if user is logged in or create guest checkout
        user_id = None
        user = None
        
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
        else:
            # Check if user exists with this email
            user = User.query.filter_by(email=customer_email).first()
            
            if not user:
                # Create a new user for guest checkout
                user = User(
                    name=customer_name,
                    email=customer_email,
                    phone=customer_phone,
                    address=customer_address,
                    city=customer_city,
                    postal_code=customer_postal_code
                )
                db.session.add(user)
                db.session.flush()  # Get user ID without committing
                session['user_id'] = user.id
        
        # Create Stripe customer if it doesn't exist for the user
        if not user or not user.stripe_customer_id:
            stripe_customer_id = create_stripe_customer(
                name=customer_name,
                email=customer_email,
                phone=customer_phone,
                address={
                    'line1': customer_address,
                    'city': customer_city,
                    'postal_code': customer_postal_code,
                    'country': 'CA',  # Assuming Canada
                }
            )
            
            if not stripe_customer_id:
                flash('Error creating payment profile. Please try again.', 'danger')
                return redirect(url_for('main.meal_plan_checkout', plan_id=plan_id))
            
            # Save Stripe customer ID to user
            if user:
                user.stripe_customer_id = stripe_customer_id
                db.session.commit()
        else:
            stripe_customer_id = user.stripe_customer_id
        
        # Build success and cancel URLs
        success_url = url_for('stripe_checkout_success', _external=True)
        cancel_url = url_for('stripe_checkout_cancel', _external=True)
        
        # Create Stripe checkout session
        checkout_session = create_stripe_checkout_session(
            customer_id=stripe_customer_id,
            meal_plan_name=meal_plan.name,
            price_amount=session['checkout_data']['price'],
            frequency=frequency,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        if not checkout_session:
            flash('Error setting up checkout session. Please try again.', 'danger')
            return redirect(url_for('main.meal_plan_checkout', plan_id=plan_id))
        
        # Store checkout session ID in session
        session['checkout_session_id'] = checkout_session['id']
        
        # Redirect to Stripe checkout
        return redirect(checkout_session['url'])
        
    except Exception as e:
        logging.error(f"Error creating checkout session: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'danger')
        return redirect(url_for('main.meal_plan_checkout', plan_id=plan_id))

@app.route('/stripe-checkout-success')
def stripe_checkout_success():
    """
    Handle successful checkout.
    """
    try:
        # Get checkout data from session
        checkout_data = session.get('checkout_data')
        checkout_session_id = session.get('checkout_session_id')
        
        if not checkout_data or not checkout_session_id:
            flash('Invalid checkout session. Please try again.', 'warning')
            return redirect(url_for('main.meals'))
        
        # Get meal plan
        plan_id = checkout_data.get('plan_id')
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
        # Get user ID from session
        user_id = session.get('user_id')
        
        if not user_id:
            flash('User session expired. Please try again.', 'warning')
            return redirect(url_for('main.login'))
        
        # Create subscription record
        frequency = SubscriptionFrequency.WEEKLY if checkout_data.get('frequency') == 'weekly' else SubscriptionFrequency.MONTHLY
        
        # Get user
        user = User.query.get(user_id)
        
        # Create subscription
        subscription = Subscription(
            user_id=user_id,
            meal_plan_id=plan_id,
            frequency=frequency,
            status=SubscriptionStatus.ACTIVE,
            price=checkout_data.get('price'),
            stripe_customer_id=user.stripe_customer_id if user else None,
            # stripe_subscription_id will be updated via webhook
            vegetarian_days=checkout_data.get('vegetarian_days', ''),
            start_date=datetime.now(),
            # Set current period based on frequency
            current_period_start=datetime.now(),
            current_period_end=(
                datetime.now() + timedelta(days=7) if frequency == SubscriptionFrequency.WEEKLY 
                else datetime.now() + timedelta(days=30)
            )
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        # Clear session data
        session.pop('checkout_data', None)
        session.pop('checkout_session_id', None)
        
        flash('Your subscription has been created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        logging.error(f"Error processing successful checkout: {str(e)}")
        flash('An error occurred while processing your subscription. Please contact support.', 'error')
        return redirect(url_for('main.meal_plans'))

@app.route('/stripe-checkout-cancel')
def stripe_checkout_cancel():
    """
    Handle cancelled checkout.
    """
    # Clear session data
    session.pop('checkout_data', None)
    session.pop('checkout_session_id', None)
    
    flash('Checkout was cancelled. Please try again when you are ready.', 'info')
    return redirect(url_for('main.meal_plans'))

# Route removed to prevent duplicate endpoint with main.py
# The validate_coupon functionality is already implemented in main.py

@app.route('/customer-portal')
def customer_portal():
    """
    Redirect to Stripe customer portal for subscription management.
    """
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Please log in to manage your subscription.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if not user or not user.stripe_customer_id:
        flash('No active subscription found.', 'warning')
        return redirect(url_for('profile'))
    
    # Create portal session
    return_url = url_for('profile', _external=True)
    portal_url = create_portal_session(user.stripe_customer_id, return_url)
    
    if not portal_url:
        flash('Error accessing subscription management. Please try again.', 'danger')
        return redirect(url_for('profile'))
    
    return redirect(portal_url)

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events.
    """
    # Get webhook secret from environment
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if not webhook_secret:
        logging.error("Missing Stripe webhook secret")
        return jsonify({'status': 'error', 'message': 'Webhook configuration error'}), 500
    
    # Get request data
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    if not sig_header:
        return jsonify({'status': 'error', 'message': 'Missing signature header'}), 400
    
    # Verify webhook signature
    event = handle_webhook_event(payload, sig_header, webhook_secret)
    
    if not event:
        return jsonify({'status': 'error', 'message': 'Invalid webhook payload'}), 400
    
    # Handle the event
    try:
        event_type = event['type']
        event_data = event['data']['object']
        
        # Handle different event types
        if event_type == 'checkout.session.completed':
            # Payment was successful, update subscription with Stripe subscription ID
            customer_id = event_data.get('customer')
            subscription_id = event_data.get('subscription')
            
            if customer_id and subscription_id:
                # Find user with this Stripe customer ID
                user = User.query.filter_by(stripe_customer_id=customer_id).first()
                
                if user:
                    # Find the most recent subscription without a Stripe subscription ID
                    subscription = Subscription.query.filter_by(
                        user_id=user.id, 
                        stripe_subscription_id=None
                    ).order_by(Subscription.created_at.desc()).first()
                    
                    if subscription:
                        subscription.stripe_subscription_id = subscription_id
                        db.session.commit()
                        logging.info(f"Updated subscription {subscription.id} with Stripe subscription ID {subscription_id}")
        
        elif event_type == 'customer.subscription.updated':
            # Subscription was updated (renewal, plan change, etc.)
            subscription_id = event_data.get('id')
            status = event_data.get('status')
            current_period_start = datetime.fromtimestamp(event_data.get('current_period_start', 0))
            current_period_end = datetime.fromtimestamp(event_data.get('current_period_end', 0))
            cancel_at_period_end = event_data.get('cancel_at_period_end', False)
            
            if subscription_id:
                # Find subscription with this Stripe subscription ID
                subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
                
                if subscription:
                    # Update subscription status based on Stripe status
                    if status == 'active':
                        subscription.status = SubscriptionStatus.ACTIVE
                    elif status == 'past_due':
                        # Keep as active but could add a past_due flag
                        subscription.status = SubscriptionStatus.ACTIVE
                    elif status == 'canceled':
                        subscription.status = SubscriptionStatus.CANCELED
                    elif status == 'unpaid':
                        subscription.status = SubscriptionStatus.CANCELED
                    
                    # Update subscription period dates
                    subscription.current_period_start = current_period_start
                    subscription.current_period_end = current_period_end
                    subscription.cancel_at_period_end = cancel_at_period_end
                    
                    db.session.commit()
                    logging.info(f"Updated subscription {subscription.id} status to {status}")
        
        elif event_type == 'customer.subscription.deleted':
            # Subscription was cancelled or expired
            subscription_id = event_data.get('id')
            
            if subscription_id:
                subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
                
                if subscription:
                    subscription.status = SubscriptionStatus.CANCELED
                    subscription.end_date = datetime.now()
                    db.session.commit()
                    logging.info(f"Marked subscription {subscription.id} as cancelled")
        
        # Add more event handling as needed
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logging.error(f"Error handling webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Error processing webhook'}), 500

# Import this file in main.py or app.py to register the routes
