#!/usr/bin/env python3
"""
WhatsApp Business API Integration for HealthyRizz.in
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from app import app, db
from database.models import User, Order, Subscription, MealPlan, Holiday
from threading import Thread

logger = logging.getLogger(__name__)

class WhatsAppMarketingSystem:
    """WhatsApp Business API integration for notifications and marketing"""
    
    def __init__(self):
        self.base_url = app.config.get('WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0')
        
        # Try to get settings from database first, then fallback to config
        try:
            from database.models import SiteSetting
            self.phone_number_id = SiteSetting.get_setting('whatsapp_phone_number_id') or app.config.get('WHATSAPP_PHONE_NUMBER_ID')
            self.access_token = SiteSetting.get_setting('whatsapp_access_token') or app.config.get('WHATSAPP_ACCESS_TOKEN')
            self.verify_token = SiteSetting.get_setting('whatsapp_webhook_verify_token') or app.config.get('WHATSAPP_VERIFY_TOKEN')
            self.business_account_id = SiteSetting.get_setting('whatsapp_business_account_id') or app.config.get('WHATSAPP_BUSINESS_ACCOUNT_ID')
        except Exception as e:
            # Fallback to config if database is not available
            self.phone_number_id = app.config.get('WHATSAPP_PHONE_NUMBER_ID')
            self.access_token = app.config.get('WHATSAPP_ACCESS_TOKEN')
            self.verify_token = app.config.get('WHATSAPP_VERIFY_TOKEN')
            self.business_account_id = app.config.get('WHATSAPP_BUSINESS_ACCOUNT_ID')
        
        # Template messages for different scenarios
        self.templates = {
            'welcome': {
                'name': 'welcome_message',
                'language': 'en_US',
                'components': [
                    {
                        'type': 'header',
                        'text': 'Welcome to HealthyRizz! 🎉'
                    },
                    {
                        'type': 'body',
                        'text': 'Hi {{1}}, welcome to HealthyRizz! We\'re excited to have you join our healthy meal community. Get 10% off your first order with code: WELCOME10'
                    },
                    {
                        'type': 'button',
                        'sub_type': 'url',
                        'index': 0,
                        'parameters': [
                            {
                                'type': 'text',
                                'text': 'Explore Meal Plans'
                            }
                        ]
                    }
                ]
            },
            'order_confirmation': {
                'name': 'order_confirmation',
                'language': 'en_US',
                'components': [
                    {
                        'type': 'header',
                        'text': 'Order Confirmed! 🎉'
                    },
                    {
                        'type': 'body',
                        'text': 'Hi {{1}}, your order #{{2}} has been confirmed and is being prepared with love! Amount: ₹{{3}}'
                    },
                    {
                        'type': 'button',
                        'sub_type': 'url',
                        'index': 0,
                        'parameters': [
                            {
                                'type': 'text',
                                'text': 'Track Order'
                            }
                        ]
                    }
                ]
            },
            'delivery_reminder': {
                'name': 'delivery_reminder',
                'language': 'en_US',
                'components': [
                    {
                        'type': 'header',
                        'text': 'Your meals are on the way! 🚚'
                    },
                    {
                        'type': 'body',
                        'text': 'Hi {{1}}, your healthy meals are being delivered today. Please ensure someone is available to receive them. Order #{{2}}'
                    }
                ]
            },
            'holiday_notification': {
                'name': 'holiday_notification',
                'language': 'en_US',
                'components': [
                    {
                        'type': 'header',
                        'text': 'Holiday Notice 🎊'
                    },
                    {
                        'type': 'body',
                        'text': 'Dear {{1}}, we wanted to inform you about our upcoming holiday: {{2}}. Duration: {{3}} to {{4}}. Your meals are protected during this period.'
                    }
                ]
            },
            'promotion_offer': {
                'name': 'promotion_offer',
                'language': 'en_US',
                'components': [
                    {
                        'type': 'header',
                        'text': 'Special Offer! 🏷️'
                    },
                    {
                        'type': 'body',
                        'text': 'Hi {{1}}, {{2}}% OFF on {{3}}! Limited time offer. Use code: {{4}}'
                    },
                    {
                        'type': 'button',
                        'sub_type': 'url',
                        'index': 0,
                        'parameters': [
                            {
                                'type': 'text',
                                'text': 'Order Now'
                            }
                        ]
                    }
                ]
            },
            'loyalty_rewards': {
                'name': 'loyalty_rewards',
                'language': 'en_US',
                'components': [
                    {
                        'type': 'header',
                        'text': 'Loyalty Points Earned! ⭐'
                    },
                    {
                        'type': 'body',
                        'text': 'Hi {{1}}, you earned {{2}} loyalty points! Total points: {{3}}. Redeem your rewards now!'
                    },
                    {
                        'type': 'button',
                        'sub_type': 'url',
                        'index': 0,
                        'parameters': [
                            {
                                'type': 'text',
                                'text': 'View Rewards'
                            }
                        ]
                    }
                ]
            },
            'feedback_request': {
                'name': 'feedback_request',
                'language': 'en_US',
                'components': [
                    {
                        'type': 'header',
                        'text': 'How was your meal? ⭐'
                    },
                    {
                        'type': 'body',
                        'text': 'Hi {{1}}, we hope you enjoyed your meal! Please rate your experience for order #{{2}}. Earn 5 loyalty points for your review!'
                    },
                    {
                        'type': 'button',
                        'sub_type': 'url',
                        'index': 0,
                        'parameters': [
                            {
                                'type': 'text',
                                'text': 'Leave Feedback'
                            }
                        ]
                    }
                ]
            },
            'win_back': {
                'name': 'win_back_campaign',
                'language': 'en_US',
                'components': [
                    {
                        'type': 'header',
                        'text': 'We miss you! 🥗'
                    },
                    {
                        'type': 'body',
                        'text': 'Hi {{1}}, it\'s been a while! We\'d love to have you back. Get 25% OFF with code: COMEBACK25'
                    },
                    {
                        'type': 'button',
                        'sub_type': 'url',
                        'index': 0,
                        'parameters': [
                            {
                                'type': 'text',
                                'text': 'Order Now'
                            }
                        ]
                    }
                ]
            },
            'referral_program': {
                'name': 'referral_program',
                'language': 'en_US',
                'components': [
                    {
                        'type': 'header',
                        'text': 'Refer & Earn! 🎁'
                    },
                    {
                        'type': 'body',
                        'text': 'Hi {{1}}, share the joy of healthy eating! Refer friends and both of you get ₹100 credit. Your referral link: {{2}}'
                    },
                    {
                        'type': 'button',
                        'sub_type': 'url',
                        'index': 0,
                        'parameters': [
                            {
                                'type': 'text',
                                'text': 'Share Now'
                            }
                        ]
                    }
                ]
            }
        }
    
    def send_message_async(self, phone_number, template_name, parameters, language='en_US'):
        """Send WhatsApp message asynchronously"""
        try:
            Thread(target=self._send_message, args=(phone_number, template_name, parameters, language)).start()
            return True
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False
    
    def _send_message(self, phone_number, template_name, parameters, language='en_US'):
        """Send WhatsApp message using Business API"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Format phone number (remove + and add country code if needed)
            formatted_phone = self._format_phone_number(phone_number)
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': formatted_phone,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {
                        'code': language
                    },
                    'components': []
                }
            }
            
            # Add parameters if provided
            if parameters:
                payload['template']['components'].append({
                    'type': 'body',
                    'parameters': [
                        {'type': 'text', 'text': str(param)} for param in parameters
                    ]
                })
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False
    
    def _format_phone_number(self, phone_number):
        """Format phone number for WhatsApp API"""
        # Remove any non-digit characters except +
        cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # If no country code, assume India (+91)
        if not cleaned.startswith('+'):
            cleaned = '+91' + cleaned
        
        # Remove + and return
        return cleaned.replace('+', '')
    
    def send_welcome_message(self, user):
        """Send welcome message to new user"""
        try:
            if not user.phone:
                logger.warning(f"No phone number for user {user.id}")
                return False
            
            parameters = [
                user.name or user.username,
                f"{app.config.get('BASE_URL', 'http://localhost:5000')}/meal-plans"
            ]
            
            return self.send_message_async(
                user.phone,
                'welcome_message',
                parameters
            )
        except Exception as e:
            logger.error(f"Error sending welcome WhatsApp message: {str(e)}")
            return False
    
    def send_order_confirmation(self, order):
        """Send order confirmation message"""
        try:
            if not order.user.phone:
                logger.warning(f"No phone number for user {order.user.id}")
                return False
            
            parameters = [
                order.user.name or order.user.username,
                str(order.id),
                str(order.amount),
                f"{app.config.get('BASE_URL', 'http://localhost:5000')}/orders/{order.id}"
            ]
            
            return self.send_message_async(
                order.user.phone,
                'order_confirmation',
                parameters
            )
        except Exception as e:
            logger.error(f"Error sending order confirmation WhatsApp message: {str(e)}")
            return False
    
    def send_delivery_reminder(self, order):
        """Send delivery reminder message"""
        try:
            if not order.user.phone:
                logger.warning(f"No phone number for user {order.user.id}")
                return False
            
            parameters = [
                order.user.name or order.user.username,
                str(order.id)
            ]
            
            return self.send_message_async(
                order.user.phone,
                'delivery_reminder',
                parameters
            )
        except Exception as e:
            logger.error(f"Error sending delivery reminder WhatsApp message: {str(e)}")
            return False
    
    def send_holiday_notification(self, holiday):
        """Send holiday notification to all users"""
        try:
            users = User.query.filter_by(is_active=True).all()
            sent_count = 0
            
            for user in users:
                if user.phone:
                    parameters = [
                        user.name or user.username,
                        holiday.name,
                        holiday.start_date.strftime('%B %d'),
                        holiday.end_date.strftime('%B %d, %Y')
                    ]
                    
                    if self.send_message_async(user.phone, 'holiday_notification', parameters):
                        sent_count += 1
            
            logger.info(f"Holiday notification sent to {sent_count} users via WhatsApp")
            return sent_count
        except Exception as e:
            logger.error(f"Error sending holiday notification WhatsApp message: {str(e)}")
            return 0
    
    def send_promotion_offer(self, meal_plan, discount_percent=15):
        """Send promotion offer to all users"""
        try:
            users = User.query.filter_by(is_active=True).all()
            sent_count = 0
            
            for user in users:
                if user.phone:
                    parameters = [
                        user.name or user.username,
                        str(discount_percent),
                        meal_plan.name,
                        f"SAVE{discount_percent}",
                        f"{app.config.get('BASE_URL', 'http://localhost:5000')}/meal-plans/{meal_plan.id}"
                    ]
                    
                    if self.send_message_async(user.phone, 'promotion_offer', parameters):
                        sent_count += 1
            
            logger.info(f"Promotion offer sent to {sent_count} users via WhatsApp")
            return sent_count
        except Exception as e:
            logger.error(f"Error sending promotion offer WhatsApp message: {str(e)}")
            return 0
    
    def send_loyalty_rewards(self, user, points_earned, total_points):
        """Send loyalty rewards notification"""
        try:
            if not user.phone:
                logger.warning(f"No phone number for user {user.id}")
                return False
            
            parameters = [
                user.name or user.username,
                str(points_earned),
                str(total_points),
                f"{app.config.get('BASE_URL', 'http://localhost:5000')}/loyalty"
            ]
            
            return self.send_message_async(
                user.phone,
                'loyalty_rewards',
                parameters
            )
        except Exception as e:
            logger.error(f"Error sending loyalty rewards WhatsApp message: {str(e)}")
            return False
    
    def send_feedback_request(self, order):
        """Send feedback request message"""
        try:
            if not order.user.phone:
                logger.warning(f"No phone number for user {order.user.id}")
                return False
            
            parameters = [
                order.user.name or order.user.username,
                str(order.id),
                f"{app.config.get('BASE_URL', 'http://localhost:5000')}/feedback/{order.id}"
            ]
            
            return self.send_message_async(
                order.user.phone,
                'feedback_request',
                parameters
            )
        except Exception as e:
            logger.error(f"Error sending feedback request WhatsApp message: {str(e)}")
            return False
    
    def send_win_back_campaign(self, user):
        """Send win-back campaign message"""
        try:
            if not user.phone:
                logger.warning(f"No phone number for user {user.id}")
                return False
            
            parameters = [
                user.name or user.username,
                f"{app.config.get('BASE_URL', 'http://localhost:5000')}/meal-plans"
            ]
            
            return self.send_message_async(
                user.phone,
                'win_back_campaign',
                parameters
            )
        except Exception as e:
            logger.error(f"Error sending win-back campaign WhatsApp message: {str(e)}")
            return False
    
    def send_referral_program(self, user):
        """Send referral program invitation"""
        try:
            if not user.phone:
                logger.warning(f"No phone number for user {user.id}")
                return False
            
            parameters = [
                user.name or user.username,
                f"{app.config.get('BASE_URL', 'http://localhost:5000')}/ref/{user.id}",
                f"{app.config.get('BASE_URL', 'http://localhost:5000')}/referrals"
            ]
            
            return self.send_message_async(
                user.phone,
                'referral_program',
                parameters
            )
        except Exception as e:
            logger.error(f"Error sending referral program WhatsApp message: {str(e)}")
            return False
    
    def send_custom_message(self, phone_number, message_text):
        """Send custom text message"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            formatted_phone = self._format_phone_number(phone_number)
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': formatted_phone,
                'type': 'text',
                'text': {
                    'body': message_text
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Custom WhatsApp message sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending custom WhatsApp message: {str(e)}")
            return False
    
    def send_bulk_campaign(self, users, template_name, parameters_list):
        """Send bulk campaign to multiple users"""
        try:
            sent_count = 0
            
            for user, parameters in zip(users, parameters_list):
                if user.phone:
                    if self.send_message_async(user.phone, template_name, parameters):
                        sent_count += 1
            
            logger.info(f"Bulk campaign sent to {sent_count} users via WhatsApp")
            return sent_count
        except Exception as e:
            logger.error(f"Error sending bulk WhatsApp campaign: {str(e)}")
            return 0
    
    def get_message_status(self, message_id):
        """Get message delivery status"""
        try:
            url = f"{self.base_url}/{message_id}"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting message status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting message status: {str(e)}")
            return None
    
    def handle_webhook(self, data):
        """Handle incoming webhook from WhatsApp"""
        try:
            # Handle message status updates
            if 'entry' in data:
                for entry in data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if change['value'].get('statuses'):
                                for status in change['value']['statuses']:
                                    self._process_status_update(status)
            
            # Handle incoming messages
            if 'entry' in data:
                for entry in data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if change['value'].get('messages'):
                                for message in change['value']['messages']:
                                    self._process_incoming_message(message)
            
            return True
        except Exception as e:
            logger.error(f"Error handling WhatsApp webhook: {str(e)}")
            return False
    
    def _process_status_update(self, status):
        """Process message status update"""
        try:
            message_id = status.get('id')
            status_type = status.get('status')
            timestamp = status.get('timestamp')
            
            logger.info(f"Message {message_id} status: {status_type} at {timestamp}")
            
            # Here you can update your database with message status
            # For example, mark messages as delivered, read, etc.
            
        except Exception as e:
            logger.error(f"Error processing status update: {str(e)}")
    
    def _process_incoming_message(self, message):
        """Process incoming message from user"""
        try:
            from_number = message.get('from')
            message_type = message.get('type')
            timestamp = message.get('timestamp')
            
            if message_type == 'text':
                text = message['text']['body']
                logger.info(f"Incoming message from {from_number}: {text}")
                
                # Handle different types of incoming messages
                self._handle_text_message(from_number, text)
            
        except Exception as e:
            logger.error(f"Error processing incoming message: {str(e)}")
    
    def _handle_text_message(self, from_number, text):
        """Handle incoming text message"""
        try:
            text_lower = text.lower()
            
            # Handle common keywords
            if 'help' in text_lower or 'support' in text_lower:
                self._send_help_message(from_number)
            elif 'menu' in text_lower or 'plans' in text_lower:
                self._send_menu_message(from_number)
            elif 'order' in text_lower or 'track' in text_lower:
                self._send_order_info_message(from_number)
            elif 'contact' in text_lower:
                self._send_contact_message(from_number)
            else:
                self._send_default_response(from_number)
                
        except Exception as e:
            logger.error(f"Error handling text message: {str(e)}")
    
    def _send_help_message(self, phone_number):
        """Send help message"""
        help_text = """🤖 HealthyRizz WhatsApp Support

Available commands:
• help - Show this message
• menu - View meal plans
• order - Track your order
• contact - Get contact info

For immediate support, call: +91-XXXXXXXXXX"""
        
        self.send_custom_message(phone_number, help_text)
    
    def _send_menu_message(self, phone_number):
        """Send menu/meal plans message"""
        menu_text = """🍽️ HealthyRizz Meal Plans

1. Balanced Lunch Plan - ₹299/week
2. High-Protein Weight Loss - ₹399/week
3. Vegetarian Delight - ₹249/week

Visit: https://healthyrizz.in/meal-plans
Or call: +91-XXXXXXXXXX"""
        
        self.send_custom_message(phone_number, menu_text)
    
    def _send_order_info_message(self, phone_number):
        """Send order tracking info"""
        order_text = """📦 Order Tracking

To track your order:
1. Visit: https://healthyrizz.in/orders
2. Enter your order number
3. Or call: +91-XXXXXXXXXX

Need help? Reply with your order number."""
        
        self.send_custom_message(phone_number, order_text)
    
    def _send_contact_message(self, phone_number):
        """Send contact information"""
        contact_text = """📞 Contact HealthyRizz

Phone: +91-XXXXXXXXXX
Email: healthyrizz.in@gmail.com
Website: https://healthyrizz.in

Business Hours: 8 AM - 8 PM (IST)
Emergency: +91-XXXXXXXXXX"""
        
        self.send_custom_message(phone_number, contact_text)
    
    def _send_default_response(self, phone_number):
        """Send default response for unrecognized messages"""
        default_text = """👋 Thanks for messaging HealthyRizz!

I'm here to help. Type:
• help - for support
• menu - for meal plans
• order - to track orders
• contact - for contact info

For immediate assistance, call: +91-XXXXXXXXXX"""
        
        self.send_custom_message(phone_number, default_text)
    
    def get_message_status(self, message_id):
        """Get message delivery status"""
        # This would typically query the WhatsApp API for message status
        # For now, return placeholder data
        return {
            'message_id': message_id,
            'status': 'delivered',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_analytics(self):
        """Get WhatsApp analytics"""
        # This would typically query your database for message statistics
        # For now, return placeholder data
        return {
            'total_messages_sent': 0,
            'messages_delivered': 0,
            'messages_read': 0,
            'failed_messages': 0,
            'delivery_rate': 0.0,
            'read_rate': 0.0,
            'templates_used': list(self.templates.keys()),
            'active_users': 0
        }
    
    def get_webhook_logs(self):
        """Get recent webhook logs"""
        # This would typically query your database for webhook logs
        # For now, return placeholder data
        return [
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

# Create global instance
whatsapp_system = WhatsAppMarketingSystem()

# Convenience functions
def send_whatsapp_welcome(user):
    """Send welcome WhatsApp message"""
    return whatsapp_system.send_welcome_message(user)

def send_whatsapp_order_confirmation(order):
    """Send order confirmation WhatsApp message"""
    return whatsapp_system.send_order_confirmation(order)

def send_whatsapp_delivery_reminder(order):
    """Send delivery reminder WhatsApp message"""
    return whatsapp_system.send_delivery_reminder(order)

def send_whatsapp_holiday_notification(holiday):
    """Send holiday notification WhatsApp message"""
    return whatsapp_system.send_holiday_notification(holiday)

def send_whatsapp_promotion(meal_plan, discount_percent=15):
    """Send promotion WhatsApp message"""
    return whatsapp_system.send_promotion_offer(meal_plan, discount_percent)

def send_whatsapp_loyalty_rewards(user, points_earned, total_points):
    """Send loyalty rewards WhatsApp message"""
    return whatsapp_system.send_loyalty_rewards(user, points_earned, total_points)

def send_whatsapp_feedback_request(order):
    """Send feedback request WhatsApp message"""
    return whatsapp_system.send_feedback_request(order)

def send_whatsapp_win_back(user):
    """Send win-back campaign WhatsApp message"""
    return whatsapp_system.send_win_back_campaign(user)

def send_whatsapp_referral_invitation(user):
    """Send referral program WhatsApp message"""
    return whatsapp_system.send_referral_program(user)
