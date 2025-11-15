#!/usr/bin/env python3
"""
WhatsApp Webhook Routes for HealthyRizz.in
"""

from flask import Blueprint, request, jsonify, current_app
from whatsapp_marketing_system import whatsapp_system
import logging

logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp', __name__)

@whatsapp_bp.route('/webhook/whatsapp', methods=['GET'])
def verify_webhook():
    """Verify WhatsApp webhook"""
    try:
        # Get query parameters
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # Get verify token from database settings
        try:
            from database.models import SiteSetting
            verify_token = SiteSetting.get_setting('whatsapp_webhook_verify_token') or current_app.config.get('WHATSAPP_VERIFY_TOKEN')
        except Exception as e:
            verify_token = current_app.config.get('WHATSAPP_VERIFY_TOKEN')
        
        if mode == 'subscribe' and token == verify_token:
            logger.info("WhatsApp webhook verified successfully")
            return challenge, 200
        else:
            logger.error("WhatsApp webhook verification failed")
            return 'Forbidden', 403
            
    except Exception as e:
        logger.error(f"Error verifying WhatsApp webhook: {str(e)}")
        return 'Internal Server Error', 500

@whatsapp_bp.route('/webhook/whatsapp', methods=['POST'])
def handle_webhook():
    """Handle incoming WhatsApp webhook"""
    try:
        # Get webhook data
        data = request.get_json()
        
        if not data:
            logger.warning("Empty webhook data received")
            return 'OK', 200
        
        # Log webhook data for debugging
        logger.info(f"WhatsApp webhook received: {data}")
        
        # Handle the webhook
        success = whatsapp_system.handle_webhook(data)
        
        if success:
            return 'OK', 200
        else:
            logger.error("Error handling WhatsApp webhook")
            return 'Internal Server Error', 500
            
    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {str(e)}")
        return 'Internal Server Error', 500

@whatsapp_bp.route('/api/whatsapp/send-message', methods=['POST'])
def send_custom_message():
    """Send custom WhatsApp message"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        phone_number = data.get('phone_number')
        message_text = data.get('message')
        
        if not phone_number or not message_text:
            return jsonify({'error': 'Phone number and message are required'}), 400
        
        # Send message
        success = whatsapp_system.send_custom_message(phone_number, message_text)
        
        if success:
            return jsonify({'success': True, 'message': 'Message sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send message'}), 500
            
    except Exception as e:
        logger.error(f"Error sending custom WhatsApp message: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@whatsapp_bp.route('/api/whatsapp/send-template', methods=['POST'])
def send_template_message():
    """Send WhatsApp template message"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        phone_number = data.get('phone_number')
        template_name = data.get('template_name')
        parameters = data.get('parameters', [])
        language = data.get('language', 'en_US')
        
        if not phone_number or not template_name:
            return jsonify({'error': 'Phone number and template name are required'}), 400
        
        # Send template message
        success = whatsapp_system.send_message_async(phone_number, template_name, parameters, language)
        
        if success:
            return jsonify({'success': True, 'message': 'Template message sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send template message'}), 500
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp template message: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@whatsapp_bp.route('/api/whatsapp/bulk-campaign', methods=['POST'])
def send_bulk_campaign():
    """Send bulk WhatsApp campaign"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_ids = data.get('user_ids', [])
        template_name = data.get('template_name')
        parameters_list = data.get('parameters_list', [])
        
        if not user_ids or not template_name:
            return jsonify({'error': 'User IDs and template name are required'}), 400
        
        # Get users from database
        from database.models import User
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        if not users:
            return jsonify({'error': 'No valid users found'}), 400
        
        # Send bulk campaign
        sent_count = whatsapp_system.send_bulk_campaign(users, template_name, parameters_list)
        
        return jsonify({
            'success': True,
            'message': f'Bulk campaign sent to {sent_count} users',
            'sent_count': sent_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending bulk WhatsApp campaign: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@whatsapp_bp.route('/api/whatsapp/message-status/<message_id>', methods=['GET'])
def get_message_status(message_id):
    """Get WhatsApp message status"""
    try:
        if not message_id:
            return jsonify({'error': 'Message ID is required'}), 400
        
        # Get message status
        status = whatsapp_system.get_message_status(message_id)
        
        if status:
            return jsonify({'success': True, 'status': status}), 200
        else:
            return jsonify({'error': 'Failed to get message status'}), 500
            
    except Exception as e:
        logger.error(f"Error getting WhatsApp message status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@whatsapp_bp.route('/api/whatsapp/templates', methods=['GET'])
def get_available_templates():
    """Get available WhatsApp templates"""
    try:
        templates = whatsapp_system.templates
        
        return jsonify({
            'success': True,
            'templates': templates
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting WhatsApp templates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@whatsapp_bp.route('/api/whatsapp/test', methods=['POST'])
def test_whatsapp_connection():
    """Test WhatsApp API connection"""
    try:
        data = request.get_json()
        test_phone = data.get('test_phone')
        
        if not test_phone:
            return jsonify({'error': 'Test phone number is required'}), 400
        
        # Send test message
        test_message = "🧪 This is a test message from HealthyRizz WhatsApp API. If you receive this, the integration is working correctly!"
        
        success = whatsapp_system.send_custom_message(test_phone, test_message)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Test message sent successfully. Check your WhatsApp!'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send test message. Check your API configuration.'
            }), 500
            
    except Exception as e:
        logger.error(f"Error testing WhatsApp connection: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@whatsapp_bp.route('/api/whatsapp/analytics', methods=['GET'])
def get_whatsapp_analytics():
    """Get WhatsApp analytics"""
    try:
        # This would typically query your database for message statistics
        # For now, we'll return placeholder data
        
        analytics = {
            'total_messages_sent': 0,
            'messages_delivered': 0,
            'messages_read': 0,
            'failed_messages': 0,
            'delivery_rate': 0.0,
            'read_rate': 0.0,
            'templates_used': list(whatsapp_system.templates.keys()),
            'active_users': 0
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting WhatsApp analytics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@whatsapp_bp.route('/api/whatsapp/webhook-logs', methods=['GET'])
def get_webhook_logs():
    """Get recent webhook logs"""
    try:
        # This would typically query your database for webhook logs
        # For now, we'll return placeholder data
        
        logs = [
            {
                'timestamp': '2024-01-15T10:30:00Z',
                'type': 'message_received',
                'phone_number': '+91XXXXXXXXXX',
                'message': 'help',
                'response': 'Help message sent'
            },
            {
                'timestamp': '2024-01-15T10:25:00Z',
                'type': 'status_update',
                'message_id': 'wamid.123456789',
                'status': 'delivered'
            }
        ]
        
        return jsonify({
            'success': True,
            'logs': logs
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting webhook logs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
