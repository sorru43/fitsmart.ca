#!/usr/bin/env python3
"""
Automated Email Marketing System for HealthyRizz.in
"""

from flask import current_app
from extensions import db, mail
from database.models import User, Order, Subscription, MealPlan, Holiday
from flask_mail import Message
from datetime import datetime, timedelta
import json
import logging
from threading import Thread
from sqlalchemy import and_, or_

logger = logging.getLogger(__name__)

class EmailMarketingSystem:
    """Automated email marketing system"""
    
    def __init__(self):
        self.campaign_types = {
            'welcome': self.send_welcome_series,
            'abandoned_cart': self.send_abandoned_cart_emails,
            'order_confirmation': self.send_order_confirmation,
            'delivery_reminder': self.send_delivery_reminder,
            'subscription_renewal': self.send_subscription_renewal,
            'holiday_notification': self.send_holiday_notification,
            'meal_plan_promotion': self.send_meal_plan_promotion,
            'loyalty_rewards': self.send_loyalty_rewards,
            'feedback_request': self.send_feedback_request,
            'win_back': self.send_win_back_campaign,
            'referral_program': self.send_referral_invitation
        }
    
    def send_email_async(self, msg):
        """Send email asynchronously"""
        try:
            with current_app.app_context():
                mail.send(msg)
                logger.info(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
    
    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send email with both HTML and text content"""
        try:
            msg = Message(
                subject=subject,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@healthyrizz.in'),
                recipients=[to_email]
            )
            msg.html = html_content
            if text_content:
                msg.body = text_content
            
            # Send asynchronously
            Thread(target=self.send_email_async, args=(msg,)).start()
            return True
        except Exception as e:
            logger.error(f"Error creating email: {str(e)}")
            return False
    
    def send_welcome_series(self, user):
        """Send welcome email series to new users"""
        try:
            # Welcome Email 1: Immediate welcome
            subject = "Welcome to HealthyRizz! 🎉 Your Healthy Meal Journey Starts Here"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #379777, #2c5f4a); color: white; padding: 30px; text-align: center;">
                    <h1>Welcome to HealthyRizz! 🎉</h1>
                    <p>Hi {user.name or user.username},</p>
                    <p>We're excited to have you join our healthy meal community!</p>
                </div>
                
                <div style="padding: 30px; background: #f9f9f9;">
                    <h2>What's Next?</h2>
                    <ul>
                        <li>🍽️ Explore our delicious meal plans</li>
                        <li>🎯 Set your dietary preferences</li>
                        <li>📅 Schedule your first delivery</li>
                        <li>🎁 Get 10% off your first order with code: WELCOME10</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/meal-plans" 
                           style="background: #379777; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                            Explore Meal Plans
                        </a>
                    </div>
                </div>
                
                <div style="padding: 20px; background: #e8f5e8; text-align: center;">
                    <p>Questions? Contact us at healthyrizz.in@gmail.com</p>
                </div>
            </div>
            """
            
            self.send_email(user.email, subject, html_content)
            
            # Schedule follow-up emails
            self.schedule_follow_up_email(user, 'welcome_day3', 3)
            self.schedule_follow_up_email(user, 'welcome_day7', 7)
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
    
    def send_abandoned_cart_emails(self, user, cart_items):
        """Send abandoned cart recovery emails"""
        try:
            subject = "Your cart is waiting! 🛒 Complete your healthy meal order"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #fff3cd; padding: 20px; border-left: 4px solid #ffc107;">
                    <h2>Don't forget your cart! 🛒</h2>
                    <p>Hi {user.name or user.username},</p>
                    <p>We noticed you left some delicious meals in your cart. Don't let them go to waste!</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>Your Cart Items:</h3>
                    <ul>
                        {''.join([f'<li>{item}</li>' for item in cart_items])}
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/cart" 
                           style="background: #379777; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                            Complete Your Order
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        Limited time offer: Use code CART10 for 10% off your order!
                    </p>
                </div>
            </div>
            """
            
            self.send_email(user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending abandoned cart email: {str(e)}")
    
    def send_order_confirmation(self, order):
        """Send order confirmation email"""
        try:
            subject = f"Order Confirmed! 🎉 Your order #{order.id} is being prepared"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #d4edda; padding: 20px; border-left: 4px solid #28a745;">
                    <h2>Order Confirmed! 🎉</h2>
                    <p>Hi {order.user.name or order.user.username},</p>
                    <p>Your order has been confirmed and is being prepared with love!</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>Order Details:</h3>
                    <p><strong>Order ID:</strong> #{order.id}</p>
                    <p><strong>Amount:</strong> ₹{order.amount}</p>
                    <p><strong>Meal Plan:</strong> {order.meal_plan.name if order.meal_plan else 'Custom'}</p>
                    <p><strong>Delivery Date:</strong> {order.delivery_date.strftime('%B %d, %Y') if order.delivery_date else 'TBD'}</p>
                    
                    <div style="background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4>What's Next?</h4>
                        <ol>
                            <li>Our chefs are preparing your meals</li>
                            <li>You'll receive delivery updates</li>
                            <li>Track your delivery in real-time</li>
                        </ol>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/orders/{order.id}" 
                           style="background: #379777; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                            Track Your Order
                        </a>
                    </div>
                </div>
            </div>
            """
            
            self.send_email(order.user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending order confirmation: {str(e)}")
    
    def send_delivery_reminder(self, order):
        """Send delivery reminder email"""
        try:
            subject = "Your healthy meals are on the way! 🚚"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #cce5ff; padding: 20px; border-left: 4px solid #007bff;">
                    <h2>Your meals are on the way! 🚚</h2>
                    <p>Hi {order.user.name or order.user.username},</p>
                    <p>Your healthy meals are being delivered today. Please ensure someone is available to receive them.</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>Delivery Details:</h3>
                    <p><strong>Order ID:</strong> #{order.id}</p>
                    <p><strong>Delivery Address:</strong> {order.user.address or 'Address not specified'}</p>
                    <p><strong>Estimated Time:</strong> 12:00 PM - 2:00 PM</p>
                    
                    <div style="background: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4>💡 Pro Tips:</h4>
                        <ul>
                            <li>Keep your phone handy for delivery updates</li>
                            <li>Store meals in refrigerator immediately</li>
                            <li>Reheat meals before consumption</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/orders/{order.id}" 
                           style="background: #379777; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                            Track Delivery
                        </a>
                    </div>
                </div>
            </div>
            """
            
            self.send_email(order.user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending delivery reminder: {str(e)}")
    
    def send_subscription_renewal(self, subscription):
        """Send subscription renewal reminder"""
        try:
            subject = "Your subscription is expiring soon! 🔄"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #fff3cd; padding: 20px; border-left: 4px solid #ffc107;">
                    <h2>Renew Your Healthy Journey! 🔄</h2>
                    <p>Hi {subscription.user.name or subscription.user.username},</p>
                    <p>Your subscription is expiring soon. Don't miss out on your healthy meals!</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>Subscription Details:</h3>
                    <p><strong>Current Plan:</strong> {subscription.meal_plan.name if subscription.meal_plan else 'Custom'}</p>
                    <p><strong>Expiry Date:</strong> {subscription.end_date.strftime('%B %d, %Y') if subscription.end_date else 'TBD'}</p>
                    
                    <div style="background: #d4edda; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4>🎁 Renewal Benefits:</h4>
                        <ul>
                            <li>10% discount on renewal</li>
                            <li>Priority delivery slots</li>
                            <li>Exclusive meal options</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/subscriptions/renew" 
                           style="background: #379777; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                            Renew Now
                        </a>
                    </div>
                </div>
            </div>
            """
            
            self.send_email(subscription.user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending subscription renewal: {str(e)}")
    
    def send_holiday_notification(self, holiday):
        """Send holiday notification to all users"""
        try:
            users = User.query.filter_by(is_active=True).all()
            
            subject = f"Holiday Notice: {holiday.name} 🎉"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #e2e3e5; padding: 20px; border-left: 4px solid #6c757d;">
                    <h2>Holiday Notice: {holiday.name} 🎉</h2>
                    <p>Dear HealthyRizz Customer,</p>
                    <p>We wanted to inform you about our upcoming holiday schedule.</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>Holiday Details:</h3>
                    <p><strong>Holiday:</strong> {holiday.name}</p>
                    <p><strong>Duration:</strong> {holiday.start_date.strftime('%B %d')} - {holiday.end_date.strftime('%B %d, %Y')}</p>
                    <p><strong>Description:</strong> {holiday.description}</p>
                    
                    <div style="background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4>📅 What This Means:</h4>
                        <ul>
                            <li>No deliveries during this period</li>
                            <li>Your meals are protected (no deductions)</li>
                            <li>We'll resume normal operations after the holiday</li>
                        </ul>
                    </div>
                    
                    <p>Thank you for your understanding!</p>
                </div>
            </div>
            """
            
            for user in users:
                self.send_email(user.email, subject, html_content)
                
        except Exception as e:
            logger.error(f"Error sending holiday notification: {str(e)}")
    
    def send_meal_plan_promotion(self, meal_plan, discount_percent=15):
        """Send meal plan promotion email"""
        try:
            users = User.query.filter_by(is_active=True).all()
            
            subject = f"Special Offer: {discount_percent}% off {meal_plan.name}! 🎉"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; padding: 30px; text-align: center;">
                    <h1>Special Offer! 🎉</h1>
                    <h2>{discount_percent}% OFF</h2>
                    <p>{meal_plan.name}</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>Meal Plan Details:</h3>
                    <p><strong>Plan:</strong> {meal_plan.name}</p>
                    <p><strong>Original Price:</strong> ₹{meal_plan.price}</p>
                    <p><strong>Discounted Price:</strong> ₹{meal_plan.price * (1 - discount_percent/100):.2f}</p>
                    <p><strong>Description:</strong> {meal_plan.description}</p>
                    
                    <div style="background: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4>⏰ Limited Time Offer:</h4>
                        <p>This offer expires in 48 hours!</p>
                        <p>Use code: <strong>SAVE{discount_percent}</strong></p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/meal-plans/{meal_plan.id}" 
                           style="background: #ff6b6b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                            Order Now
                        </a>
                    </div>
                </div>
            </div>
            """
            
            for user in users:
                self.send_email(user.email, subject, html_content)
                
        except Exception as e:
            logger.error(f"Error sending meal plan promotion: {str(e)}")
    
    def send_loyalty_rewards(self, user, points_earned, total_points):
        """Send loyalty rewards notification"""
        try:
            subject = f"You earned {points_earned} loyalty points! ⭐"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #ffd700, #ffed4e); color: #333; padding: 30px; text-align: center;">
                    <h1>🎉 Loyalty Points Earned!</h1>
                    <h2>+{points_earned} Points</h2>
                    <p>Total Points: {total_points}</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>Rewards Available:</h3>
                    <ul>
                        <li>100 points = ₹50 discount</li>
                        <li>200 points = Free delivery</li>
                        <li>500 points = 1 free meal</li>
                        <li>1000 points = 1 week free subscription</li>
                    </ul>
                    
                    <div style="background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4>💡 How to earn more points:</h4>
                        <ul>
                            <li>Place orders (+10 points per order)</li>
                            <li>Refer friends (+50 points per referral)</li>
                            <li>Leave reviews (+5 points per review)</li>
                            <li>Share on social media (+2 points per share)</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/loyalty" 
                           style="background: #ffd700; color: #333; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                            View Rewards
                        </a>
                    </div>
                </div>
            </div>
            """
            
            self.send_email(user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending loyalty rewards: {str(e)}")
    
    def send_feedback_request(self, order):
        """Send feedback request after delivery"""
        try:
            subject = "How was your meal? We'd love to hear from you! ⭐"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #e3f2fd; padding: 20px; border-left: 4px solid #2196f3;">
                    <h2>How was your meal? ⭐</h2>
                    <p>Hi {order.user.name or order.user.username},</p>
                    <p>We hope you enjoyed your healthy meal! Your feedback helps us improve.</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>Order Details:</h3>
                    <p><strong>Order ID:</strong> #{order.id}</p>
                    <p><strong>Meal Plan:</strong> {order.meal_plan.name if order.meal_plan else 'Custom'}</p>
                    <p><strong>Delivery Date:</strong> {order.delivery_date.strftime('%B %d, %Y') if order.delivery_date else 'TBD'}</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <h4>Rate your experience:</h4>
                        <div style="margin: 20px 0;">
                            <span style="font-size: 24px; cursor: pointer;">⭐</span>
                            <span style="font-size: 24px; cursor: pointer;">⭐</span>
                            <span style="font-size: 24px; cursor: pointer;">⭐</span>
                            <span style="font-size: 24px; cursor: pointer;">⭐</span>
                            <span style="font-size: 24px; cursor: pointer;">⭐</span>
                        </div>
                        
                        <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/feedback/{order.id}" 
                           style="background: #2196f3; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                            Leave Feedback
                        </a>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4>🎁 Bonus:</h4>
                        <p>Leave a review and earn 5 loyalty points!</p>
                    </div>
                </div>
            </div>
            """
            
            self.send_email(order.user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending feedback request: {str(e)}")
    
    def send_win_back_campaign(self, user):
        """Send win-back campaign to inactive users"""
        try:
            subject = "We miss you! Come back to HealthyRizz 🥗"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; padding: 30px; text-align: center;">
                    <h1>We miss you! 🥗</h1>
                    <p>Hi {user.name or user.username},</p>
                    <p>It's been a while since your last order. We'd love to have you back!</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>What's New:</h3>
                    <ul>
                        <li>🍽️ New seasonal meal plans</li>
                        <li>🎯 Personalized recommendations</li>
                        <li>🚚 Faster delivery options</li>
                        <li>⭐ Enhanced loyalty program</li>
                    </ul>
                    
                    <div style="background: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4>🎁 Special Comeback Offer:</h4>
                        <p><strong>25% OFF</strong> your next order!</p>
                        <p>Use code: <strong>COMEBACK25</strong></p>
                        <p>Valid for 7 days only!</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/meal-plans" 
                           style="background: #ff6b6b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                            Order Now
                        </a>
                    </div>
                </div>
            </div>
            """
            
            self.send_email(user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending win-back campaign: {str(e)}")
    
    def send_referral_invitation(self, user):
        """Send referral program invitation"""
        try:
            subject = "Invite friends & earn rewards! 🎁"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #4caf50, #45a049); color: white; padding: 30px; text-align: center;">
                    <h1>Refer & Earn! 🎁</h1>
                    <p>Hi {user.name or user.username},</p>
                    <p>Share the joy of healthy eating with your friends and family!</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>How it works:</h3>
                    <ol>
                        <li>Share your unique referral link</li>
                        <li>Friend signs up and places first order</li>
                        <li>Both of you get ₹100 credit!</li>
                    </ol>
                    
                    <div style="background: #e8f5e8; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4>Your Referral Link:</h4>
                        <p style="background: #f8f9fa; padding: 10px; border-radius: 3px; word-break: break-all;">
                            {current_app.config.get('BASE_URL', 'http://localhost:5000')}/ref/{user.id}
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/referrals" 
                           style="background: #4caf50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
                            View Referrals
                        </a>
                    </div>
                </div>
            </div>
            """
            
            self.send_email(user.email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Error sending referral invitation: {str(e)}")
    
    def schedule_follow_up_email(self, user, email_type, days_delay):
        """Schedule follow-up email"""
        # This would integrate with a task queue like Celery
        # For now, we'll just log it
        logger.info(f"Scheduled {email_type} email for user {user.id} in {days_delay} days")
    
    def run_campaign(self, campaign_type, **kwargs):
        """Run a specific email campaign"""
        if campaign_type in self.campaign_types:
            try:
                self.campaign_types[campaign_type](**kwargs)
                logger.info(f"Campaign {campaign_type} executed successfully")
                return True
            except Exception as e:
                logger.error(f"Error running campaign {campaign_type}: {str(e)}")
                return False
        else:
            logger.error(f"Unknown campaign type: {campaign_type}")
            return False
    
    def get_campaign_stats(self):
        """Get email campaign statistics"""
        # This would query the database for email campaign statistics
        return {
            'total_campaigns': len(self.campaign_types),
            'campaigns_sent': 0,  # Would be calculated from database
            'open_rate': 0.0,     # Would be calculated from database
            'click_rate': 0.0,    # Would be calculated from database
            'conversion_rate': 0.0 # Would be calculated from database
        }

# Create global instance
email_system = EmailMarketingSystem()

def send_welcome_email(user):
    """Send welcome email to new user"""
    return email_system.send_welcome_series(user)

def send_order_confirmation_email(order):
    """Send order confirmation email"""
    return email_system.send_order_confirmation(order)

def send_delivery_reminder_email(order):
    """Send delivery reminder email"""
    return email_system.send_delivery_reminder(order)

def send_holiday_notification_email(holiday):
    """Send holiday notification email"""
    return email_system.send_holiday_notification(holiday)

def send_meal_plan_promotion_email(meal_plan, discount_percent=15):
    """Send meal plan promotion email"""
    return email_system.send_meal_plan_promotion(meal_plan, discount_percent)

def send_loyalty_rewards_email(user, points_earned, total_points):
    """Send loyalty rewards email"""
    return email_system.send_loyalty_rewards(user, points_earned, total_points)

def send_feedback_request_email(order):
    """Send feedback request email"""
    return email_system.send_feedback_request(order)

def send_win_back_email(user):
    """Send win-back campaign email"""
    return email_system.send_win_back_campaign(user)

def send_referral_invitation_email(user):
    """Send referral invitation email"""
    return email_system.send_referral_invitation(user)
