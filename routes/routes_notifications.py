"""
Routes for push notification functionality
"""
import os
import json
import logging
from flask import request, jsonify, current_app
from main import app
from database.models import db, User, PushSubscription

# Configure logging
logger = logging.getLogger(__name__)

# Initialize push subscription storage
subscriptions = []

# Create push_subscriptions table if it doesn't exist
with app.app_context():
    db.create_all()

@app.route('/api/save-subscription', methods=['POST'])
def save_subscription():
    """Save a push notification subscription to the database"""
    try:
        # Get the subscription data from the request
        subscription = request.json
        
        if not subscription or not isinstance(subscription, dict):
            return jsonify({'success': False, 'error': 'Invalid subscription data'}), 400
        
        # Extract subscription details
        endpoint = subscription.get('endpoint')
        keys = subscription.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')
        
        if not endpoint or not p256dh or not auth:
            return jsonify({'success': False, 'error': 'Missing required subscription fields'}), 400
        
        # Check if this subscription already exists
        existing_sub = PushSubscription.query.filter_by(endpoint=endpoint).first()
        
        if existing_sub:
            # Update existing subscription
            existing_sub.p256dh = p256dh
            existing_sub.auth = auth
            db.session.commit()
            logger.info(f"Updated existing push subscription: {endpoint}")
        else:
            # Create new subscription
            # Get current user ID if authenticated
            user_id = None
            # You can add code here to get the current user ID if needed
            
            new_subscription = PushSubscription(
                user_id=user_id,
                endpoint=endpoint,
                p256dh=p256dh,
                auth=auth
            )
            db.session.add(new_subscription)
            db.session.commit()
            logger.info(f"Saved new push subscription: {endpoint}")
        
        return jsonify({'success': True}), 201
        
    except Exception as e:
        logger.error(f"Error saving push subscription: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-notification', methods=['POST'])
def send_notification():
    """Send a push notification to all subscribers or specific subscribers"""
    # This endpoint would typically be protected by authentication
    try:
        import pywebpush
        
        # Get notification data from request
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No notification data provided'}), 400
        
        title = data.get('title', 'HealthyRizz Notification')
        message = data.get('message', 'You have a new notification!')
        url = data.get('url', '/')
        user_id = data.get('user_id')  # Optional: target specific user
        
        notification_data = json.dumps({
            'title': title,
            'message': message,
            'url': url
        })
        
        # Get VAPID keys from environment variables
        vapid_private_key = os.environ.get('VAPID_PRIVATE_KEY')
        vapid_public_key = os.environ.get('VAPID_PUBLIC_KEY')
        vapid_claims = {
            'sub': f"mailto:{os.environ.get('VAPID_CONTACT_EMAIL', 'admin@healthyrizz.ca')}",
            'aud': request.host_url
        }
        
        if not vapid_private_key or not vapid_public_key:
            return jsonify({
                'success': False, 
                'error': 'VAPID keys not configured. Use generate_vapid_keys.py to create them.'
            }), 500
        
        # Query subscriptions based on filters
        query = PushSubscription.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        subscriptions_to_notify = query.all()
        
        if not subscriptions_to_notify:
            return jsonify({'success': False, 'error': 'No subscriptions found'}), 404
        
        # Send notifications to all subscriptions
        sent_count = 0
        failed_count = 0
        
        for subscription in subscriptions_to_notify:
            try:
                # Format subscription for pywebpush
                sub_info = {
                    'endpoint': subscription.endpoint,
                    'keys': {
                        'p256dh': subscription.p256dh,
                        'auth': subscription.auth
                    }
                }
                
                # Send the notification
                pywebpush.webpush(
                    subscription_info=sub_info,
                    data=notification_data,
                    vapid_private_key=vapid_private_key,
                    vapid_claims=vapid_claims
                )
                
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send notification to {subscription.endpoint}: {str(e)}")
                failed_count += 1
        
        return jsonify({
            'success': True,
            'sent': sent_count,
            'failed': failed_count
        }), 200
        
    except ImportError:
        return jsonify({
            'success': False, 
            'error': 'pywebpush not installed. Run: pip install pywebpush'
        }), 500
    except Exception as e:
        logger.error(f"Error sending notifications: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vapid-public-key')
def get_vapid_public_key():
    """Return the VAPID public key for push notifications"""
    vapid_public_key = os.environ.get('VAPID_PUBLIC_KEY')
    
    if not vapid_public_key:
        return jsonify({
            'success': False, 
            'error': 'VAPID keys not configured. Use generate_vapid_keys.py to create them.'
        }), 500
    
    return jsonify({'success': True, 'publicKey': vapid_public_key}), 200

@app.route('/api/remove-subscription', methods=['POST'])
def remove_subscription():
    """Remove a push notification subscription from the database"""
    try:
        data = request.json
        
        if not data or not data.get('endpoint'):
            return jsonify({'success': False, 'error': 'Missing endpoint'}), 400
        
        endpoint = data.get('endpoint')
        
        # Find and remove the subscription
        subscription = PushSubscription.query.filter_by(endpoint=endpoint).first()
        
        if subscription:
            db.session.delete(subscription)
            db.session.commit()
            logger.info(f"Removed push subscription: {endpoint}")
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'error': 'Subscription not found'}), 404
        
    except Exception as e:
        logger.error(f"Error removing push subscription: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
