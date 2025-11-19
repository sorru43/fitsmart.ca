#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Email Functions for FitSmart
This file contains all email functions needed for the application
"""

import os
import logging
from datetime import datetime, timedelta
from flask import current_app, render_template, url_for
from flask_mail import Message
from extensions import mail
from utils.email_utils import send_email

logger = logging.getLogger(__name__)

# ============================================================================
# USER REGISTRATION & ACCOUNT EMAILS
# ============================================================================

def send_welcome_email(user):
    """
    Send welcome email to new user
    
    Args:
        user: User object
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = "Welcome to FitSmart! 🎉"
        
        html_content = render_template('email/welcome.html', 
                                     user=user, 
                                     now=datetime.now())
        
        text_content = f"""
Welcome to FitSmart!

Hello {user.name},

Welcome to FitSmart! We're thrilled to have you join our community of health-conscious individuals.

At FitSmart, we believe that healthy eating should be delicious, convenient, and personalized to your needs. Our team of nutrition experts and chefs work together to create meals that are not only nutritious but also incredibly tasty.

What you can expect from FitSmart:
- Fresh, Chef-Prepared Meals
- Personalized Nutrition Plans  
- Convenient Delivery
- Easy Management

Ready to start your healthy journey? Visit our website to explore meal plans.

If you have any questions or need assistance, our customer support team is here to help:
- Email: support@fitsmart.ca
- Phone: +91-98765-43210
- Live Chat: Available on our website

Thank you for choosing FitSmart for your nutritional needs!

Best regards,
The FitSmart Team
        """
        
        return send_email(
            to_email=user.email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False

def send_verification_email(user, verification_token):
    """
    Send email verification email
    
    Args:
        user: User object
        verification_token: Verification token
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = "Verify Your Email - FitSmart"
        verification_url = url_for('auth.verify_email', token=verification_token, _external=True)
        
        html_content = render_template('email/email_verification.html',
                                     user=user,
                                     verification_url=verification_url,
                                     now=datetime.now())
        
        text_content = f"""
Verify Your Email Address

Hello {user.name},

Thank you for registering with FitSmart! To complete your registration and start enjoying our healthy meal services, please verify your email address.

Click the link below to verify your email address:
{verification_url}

If the link doesn't work, copy and paste it into your browser.

Important Security Notice:
- This verification link will expire in 24 hours
- If you don't verify your email within this time, you'll need to request a new verification link

What happens after verification:
- Your account will be fully activated
- You can access all features of FitSmart
- You can place orders and manage your subscriptions
- You'll receive important updates about your deliveries

Need help? Contact our support team:
- Email: support@fitsmart.ca
- Phone: +91-98765-43210

Best regards,
The FitSmart Team
        """
        
        return send_email(
            to_email=user.email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False

def send_password_reset_email(user, reset_token):
    """
    Send password reset email
    
    Args:
        user: User object
        reset_token: Reset token
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = "Password Reset Request - FitSmart"
        reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
        
        html_content = render_template('email/password_reset.html',
                                     user=user,
                                     reset_url=reset_url,
                                     now=datetime.now())
        
        text_content = f"""
Password Reset Request

Hello {user.name},

We received a request to reset your password for your FitSmart account. If you made this request, please use the link below to create a new password.

Reset your password:
{reset_url}

If the link doesn't work, copy and paste it into your browser.

Security Notice:
- This password reset link will expire in 1 hour
- If you didn't request this password reset, please ignore this email
- Your current password will remain unchanged until you complete the reset

Password Security Tips:
- Use at least 8 characters
- Include a mix of uppercase and lowercase letters
- Add numbers and special characters
- Avoid using personal information
- Don't reuse passwords from other accounts

If you didn't request this password reset, it's possible that:
- Someone else entered your email address by mistake
- You have another account with the same email address
- Someone is trying to access your account

If you're concerned about your account security:
1. Log into your account immediately and change your password
2. Check your account for any suspicious activity
3. Contact our support team if you notice anything unusual

Need help? Contact us:
- Email: fitsmart.ca@gmail.com
- Phone: +91-98765-43210
- Live Chat: Available on our website

Best regards,
The FitSmart Security Team
        """
        
        return send_email(
            to_email=user.email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False

# ============================================================================
# PAYMENT RELATED EMAILS
# ============================================================================

def send_payment_success_email(order):
    """
    Send payment success email
    
    Args:
        order: Order object
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = f"🎉 Payment Successful! - Order #{order.id}"
        
        # Create HTML content directly instead of using render_template
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
                .success {{ background: #d1fae5; border: 1px solid #10b981; padding: 15px; border-radius: 6px; margin: 15px 0; }}
                .order-details {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .next-steps {{ background: #e8f5e8; border: 1px solid #10b981; padding: 15px; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 20px; }}
                .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 Payment Successful!</h1>
                <p>Order #{order.id} - {order.created_at.strftime('%d/%m/%Y %I:%M %p')}</p>
            </div>
            
            <div class="content">
                <div class="success">
                    <h2>✅ Payment Confirmed!</h2>
                    <p>Hello {order.customer_name},</p>
                    <p>Great news! Your payment has been processed successfully and your order is now confirmed. We're excited to start preparing your healthy meals!</p>
                </div>
                
                <div class="order-details">
                    <h3>📋 Order Details</h3>
                    <p><strong>Order Number:</strong> #{order.id}</p>
                    <p><strong>Order Date:</strong> {order.created_at.strftime('%d/%m/%Y %I:%M %p')}</p>
                    <p><strong>Payment Method:</strong> {order.payment_method.title() if hasattr(order, 'payment_method') and order.payment_method else 'Online Payment'}</p>
                    <p><strong>Payment Status:</strong> Paid</p>
                    <p><strong>Total Amount:</strong> ₹{order.total_amount}</p>
                    
                    <h4>📍 Delivery Address</h4>
                    <p>{order.customer_address}<br>
                    {order.customer_city}, {order.customer_state} - {order.customer_pincode}</p>
                </div>
                
                <div class="next-steps">
                    <h3>🚀 What's Next?</h3>
                    <ul>
                        <li><strong>Order Processing:</strong> We'll start preparing your meals within 24 hours</li>
                        <li><strong>Delivery Schedule:</strong> You'll receive a delivery notification with your delivery time</li>
                        <li><strong>Tracking:</strong> You can track your order status in your account dashboard</li>
                        <li><strong>Support:</strong> Our team is available 24/7 if you need any assistance</li>
                    </ul>
                </div>
                
                <div class="order-details">
                    <h3>📞 Need Help?</h3>
                    <p><strong>Email:</strong> <a href="mailto:fitsmart.ca@gmail.com">fitsmart.ca@gmail.com</a></p>
                    <p><strong>Phone:</strong> <a href="tel:+919876543210">+91-98765-43210</a></p>
                    <p><strong>Live Chat:</strong> Available on our website</p>
                </div>
                
                <div class="order-details">
                    <h3>📱 Stay Connected</h3>
                    <p><strong>Facebook:</strong> @FitSmart</p>
                    <p><strong>Instagram:</strong> @fitsmart.ca</p>
                    <p><strong>Twitter:</strong> @FitSmart</p>
                </div>
                
                <p>Thank you for choosing FitSmart! We're committed to providing you with the best healthy meal experience.</p>
                
                <p>Best regards,<br>The FitSmart Team</p>
            </div>
            
            <div class="footer">
                <p>This is an automated email from FitSmart.</p>
                <p>&copy; {datetime.now().year} FitSmart. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
Payment Successful!

Hello {order.customer_name},

Great news! Your payment has been processed successfully and your order is now confirmed. We're excited to start preparing your healthy meals!

Order Details:
- Order Number: #{order.id}
- Order Date: {order.created_at.strftime('%d/%m/%Y %I:%M %p')}
- Payment Method: {order.payment_method.title() if hasattr(order, 'payment_method') and order.payment_method else 'Online Payment'}
- Payment Status: Paid
- Total Amount: ₹{order.total_amount}

Delivery Address:
{order.customer_address}
{order.customer_city}, {order.customer_state} - {order.customer_pincode}

What's Next?
- Order Processing: We'll start preparing your meals within 24 hours
- Delivery Schedule: You'll receive a delivery notification with your delivery time
- Tracking: You can track your order status in your account dashboard
- Support: Our team is available 24/7 if you need any assistance

Need Help?
- Email: fitsmart.ca@gmail.com
- Phone: +91-98765-43210
- Live Chat: Available on our website

Stay Connected:
- Facebook: @FitSmart
- Instagram: @fitsmart.ca
- Twitter: @FitSmart

Thank you for choosing FitSmart! We're committed to providing you with the best healthy meal experience.

Best regards,
The FitSmart Team
        """
        
        return send_email(
            to_email=order.customer_email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send payment success email to {order.customer_email}: {str(e)}")
        return False

def send_payment_failed_email(order):
    """
    Send payment failed email
    
    Args:
        order: Order object
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = f"⚠️ Payment Failed - Order #{order.id}"
        
        html_content = render_template('email/payment_failed.html',
                                     order=order,
                                     now=datetime.now())
        
        text_content = f"""
Payment Failed

Hello {order.customer_name},

We attempted to process your payment for order #{order.id}, but it was unsuccessful. Don't worry - this happens sometimes and is usually easy to resolve.

Order Details:
- Order Number: #{order.id}
- Order Date: {order.created_at.strftime('%d/%m/%Y %I:%M %p')}
- Amount: ₹{order.total_amount}

Delivery Address:
{order.customer_address}
{order.customer_city}, {order.customer_state} - {order.customer_pincode}

Common Reasons for Payment Failure:
- Insufficient funds in your account
- Card expired or incorrect card details
- Bank declined the transaction for security reasons
- Network issues during payment processing
- 3D Secure authentication was not completed

How to Retry Payment:
1. Log into your FitSmart account
2. Go to your order history
3. Find order #{order.id}
4. Click "Retry Payment"
5. Complete the payment process

Alternative Payment Methods:
- Use a different payment method (UPI, Net Banking, etc.)
- Contact your bank to ensure the card is active
- Check if your bank has any restrictions on online payments

Need Help?
- Email: fitsmart.ca@gmail.com
- Phone: +91-98765-43210
- Live Chat: Available on our website

Important: Your order will be held for 24 hours. If payment is not completed within this time, the order will be automatically cancelled.

We apologize for any inconvenience and look forward to serving you once the payment is completed.

Best regards,
The FitSmart Team
        """
        
        return send_email(
            to_email=order.customer_email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send payment failed email to {order.customer_email}: {str(e)}")
        return False

def send_payment_success_email(user, subscription, amount, period_end):
    """
    Send payment success email for recurring subscription payment
    
    Args:
        user: User object
        subscription: Subscription object
        amount: Amount paid (float)
        period_end: Period end date (datetime)
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = f"✅ Payment Successful - Your {subscription.meal_plan.name} Subscription Renewed"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
                .success {{ background: #d1fae5; border: 1px solid #10b981; padding: 15px; border-radius: 6px; margin: 15px 0; }}
                .subscription-details {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>✅ Payment Successful!</h1>
                <p>Your Subscription Has Been Renewed</p>
            </div>
            
            <div class="content">
                <div class="success">
                    <h2>🎉 Payment Confirmed!</h2>
                    <p>Hello {user.name},</p>
                    <p>Great news! Your recurring payment has been processed successfully. Your subscription has been renewed and your meal deliveries will continue without interruption.</p>
                </div>
                
                <div class="subscription-details">
                    <h3>📋 Payment Details</h3>
                    <p><strong>Meal Plan:</strong> {subscription.meal_plan.name}</p>
                    <p><strong>Amount Paid:</strong> ${amount:.2f} CAD</p>
                    <p><strong>Payment Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                    <p><strong>Next Billing Date:</strong> {period_end.strftime('%B %d, %Y')}</p>
                    <p><strong>Frequency:</strong> {subscription.frequency.value.title()}</p>
                </div>
                
                <div class="subscription-details">
                    <h3>🚀 What's Next?</h3>
                    <p>Your meal deliveries will continue as scheduled. No action is required from you - we'll automatically process your next payment on {period_end.strftime('%B %d, %Y')}.</p>
                </div>
                
                <p>Thank you for being a valued FitSmart customer!</p>
                
                <p>Best regards,<br>The FitSmart Team</p>
            </div>
            
            <div class="footer">
                <p>This is an automated email from FitSmart.</p>
                <p>&copy; {datetime.now().year} FitSmart. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
Payment Successful - Subscription Renewed

Hello {user.name},

Great news! Your recurring payment has been processed successfully. Your subscription has been renewed and your meal deliveries will continue without interruption.

Payment Details:
- Meal Plan: {subscription.meal_plan.name}
- Amount Paid: ${amount:.2f} CAD
- Payment Date: {datetime.now().strftime('%B %d, %Y')}
- Next Billing Date: {period_end.strftime('%B %d, %Y')}
- Frequency: {subscription.frequency.value.title()}

Your meal deliveries will continue as scheduled. No action is required from you - we'll automatically process your next payment on {period_end.strftime('%B %d, %Y')}.

Thank you for being a valued FitSmart customer!

Best regards,
The FitSmart Team
        """
        
        return send_email(
            to_email=user.email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send payment success email to {user.email}: {str(e)}")
        return False

def send_payment_failed_email(user, subscription, amount, attempt_count):
    """
    Send payment failed email for recurring subscription payment
    
    Args:
        user: User object
        subscription: Subscription object
        amount: Amount due (float)
        attempt_count: Number of payment attempts (int)
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = f"⚠️ Payment Failed - Action Required for Your {subscription.meal_plan.name} Subscription"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #ef4444; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
                .warning {{ background: #fee2e2; border: 1px solid #ef4444; padding: 15px; border-radius: 6px; margin: 15px 0; }}
                .subscription-details {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .button {{ display: inline-block; background: #ef4444; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 15px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚠️ Payment Failed</h1>
                <p>Action Required</p>
            </div>
            
            <div class="content">
                <div class="warning">
                    <h2>Payment Could Not Be Processed</h2>
                    <p>Hello {user.name},</p>
                    <p>We attempted to process your recurring payment for your {subscription.meal_plan.name} subscription, but it was unsuccessful. This is attempt #{attempt_count}.</p>
                </div>
                
                <div class="subscription-details">
                    <h3>📋 Payment Details</h3>
                    <p><strong>Meal Plan:</strong> {subscription.meal_plan.name}</p>
                    <p><strong>Amount Due:</strong> ${amount:.2f} CAD</p>
                    <p><strong>Attempt Number:</strong> {attempt_count}</p>
                    <p><strong>Frequency:</strong> {subscription.frequency.value.title()}</p>
                </div>
                
                <div class="subscription-details">
                    <h3>🔧 What You Need to Do</h3>
                    <ol>
                        <li><strong>Update Your Payment Method:</strong> Log into your account and update your payment information</li>
                        <li><strong>Check Your Card:</strong> Ensure your card has sufficient funds and is not expired</li>
                        <li><strong>Contact Your Bank:</strong> Verify there are no restrictions on your card</li>
                    </ol>
                    <p><a href="https://fitsmart.ca/profile" class="button">Update Payment Method</a></p>
                </div>
                
                <div class="warning">
                    <h3>⚠️ Important</h3>
                    <p>If payment is not updated within 3 attempts, your subscription will be automatically cancelled and meal deliveries will stop.</p>
                </div>
                
                <p>Need help? Contact us at fitsmart.ca@gmail.com or call us for assistance.</p>
                
                <p>Best regards,<br>The FitSmart Team</p>
            </div>
            
            <div class="footer">
                <p>This is an automated email from FitSmart.</p>
                <p>&copy; {datetime.now().year} FitSmart. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
Payment Failed - Action Required

Hello {user.name},

We attempted to process your recurring payment for your {subscription.meal_plan.name} subscription, but it was unsuccessful. This is attempt #{attempt_count}.

Payment Details:
- Meal Plan: {subscription.meal_plan.name}
- Amount Due: ${amount:.2f} CAD
- Attempt Number: {attempt_count}
- Frequency: {subscription.frequency.value.title()}

What You Need to Do:
1. Update Your Payment Method: Log into your account and update your payment information
2. Check Your Card: Ensure your card has sufficient funds and is not expired
3. Contact Your Bank: Verify there are no restrictions on your card

Update Payment Method: https://fitsmart.ca/profile

IMPORTANT: If payment is not updated within 3 attempts, your subscription will be automatically cancelled and meal deliveries will stop.

Need help? Contact us at fitsmart.ca@gmail.com

Best regards,
The FitSmart Team
        """
        
        return send_email(
            to_email=user.email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send payment failed email to {user.email}: {str(e)}")
        return False

def send_payment_reminder_email(user=None, subscription=None, amount=None, due_date=None):
    """
    Send payment reminder email before recurring payment
    
    Args:
        user: User object (optional, will use subscription.user if not provided)
        subscription: Subscription object (required)
        amount: Amount due (float, optional)
        due_date: Payment due date (datetime, optional)
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Handle legacy call with just subscription
    if subscription and not user:
        user = subscription.user
        # Try to get amount and due_date from subscription
        amount = amount or subscription.price
        due_date = due_date or subscription.current_period_end
    try:
        subject = f"⏰ Payment Reminder - Your {subscription.meal_plan.name} Subscription Renewal"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f59e0b; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
                .reminder {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 6px; margin: 15px 0; }}
                .subscription-details {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⏰ Payment Reminder</h1>
                <p>Subscription Renewal Due Soon</p>
            </div>
            
            <div class="content">
                <div class="reminder">
                    <h2>💰 Payment Due Soon</h2>
                    <p>Hello {user.name},</p>
                    <p>This is a friendly reminder that your subscription renewal payment will be processed automatically on {due_date.strftime('%B %d, %Y')}.</p>
                </div>
                
                <div class="subscription-details">
                    <h3>📋 Subscription Details</h3>
                    <p><strong>Meal Plan:</strong> {subscription.meal_plan.name}</p>
                    <p><strong>Amount:</strong> ${amount:.2f} CAD</p>
                    <p><strong>Due Date:</strong> {due_date.strftime('%B %d, %Y')}</p>
                    <p><strong>Frequency:</strong> {subscription.frequency.value.title()}</p>
                </div>
                
                <div class="subscription-details">
                    <h3>✅ No Action Required</h3>
                    <p>Your payment will be processed automatically using your saved payment method. To ensure uninterrupted meal deliveries, please:</p>
                    <ul>
                        <li>Ensure your payment method is up to date</li>
                        <li>Check that your card has sufficient funds</li>
                        <li>Verify your card is not expired</li>
                    </ul>
                    <p><a href="https://fitsmart.ca/profile">Update Payment Method</a></p>
                </div>
                
                <p>Thank you for being a valued FitSmart customer!</p>
                
                <p>Best regards,<br>The FitSmart Team</p>
            </div>
            
            <div class="footer">
                <p>This is an automated email from FitSmart.</p>
                <p>&copy; {datetime.now().year} FitSmart. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
Payment Reminder - Subscription Renewal Due Soon

Hello {user.name},

This is a friendly reminder that your subscription renewal payment will be processed automatically on {due_date.strftime('%B %d, %Y')}.

Subscription Details:
- Meal Plan: {subscription.meal_plan.name}
- Amount: ${amount:.2f} CAD
- Due Date: {due_date.strftime('%B %d, %Y')}
- Frequency: {subscription.frequency.value.title()}

No Action Required: Your payment will be processed automatically using your saved payment method. To ensure uninterrupted meal deliveries, please ensure your payment method is up to date and has sufficient funds.

Update Payment Method: https://fitsmart.ca/profile

Thank you for being a valued FitSmart customer!

Best regards,
The FitSmart Team
        """
        
        return send_email(
            to_email=user.email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send payment reminder email to {user.email}: {str(e)}")
        return False


# ============================================================================
# ADMIN NOTIFICATION EMAILS
# ============================================================================

def send_admin_new_order_notification(order):
    """
    Send notification to admin about new order
    
    Args:
        order: Order object
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@fitsmart.ca')
        subject = f"🆕 New Order Received! - Order #{order.id}"
        
        # Create HTML content directly instead of using render_template
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
                .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
                .info-section {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .actions {{ background: #e8f5e8; border: 1px solid #10b981; padding: 15px; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🆕 New Order Received!</h1>
                <p>Order #{order.id} - {order.created_at.strftime('%d/%m/%Y %I:%M %p')}</p>
            </div>
            
            <div class="content">
                <div class="info-grid">
                    <div class="info-section">
                        <h3>📋 Order Information</h3>
                        <p><strong>Order ID:</strong> #{order.id}</p>
                        <p><strong>Order Date:</strong> {order.created_at.strftime('%d/%m/%Y %I:%M %p')}</p>
                        <p><strong>Order Status:</strong> {order.status.title() if order.status else 'Pending'}</p>
                        <p><strong>Payment Status:</strong> {order.payment_status.title() if order.payment_status else 'Pending'}</p>
                        <p><strong>Total Amount:</strong> ₹{order.total_amount}</p>
                    </div>
                    
                    <div class="info-section">
                        <h3>👤 Customer Information</h3>
                        <p><strong>Name:</strong> {order.customer_name}</p>
                        <p><strong>Email:</strong> {order.customer_email}</p>
                        <p><strong>Phone:</strong> {order.customer_phone}</p>
                        <p><strong>Address:</strong> {order.customer_address}</p>
                        <p><strong>City:</strong> {order.customer_city}, {order.customer_state} - {order.customer_pincode}</p>
                    </div>
                </div>
                
                <div class="actions">
                    <h3>🔧 Required Actions</h3>
                    <ol>
                        <li><strong>Review Order:</strong> Check if all details are correct</li>
                        <li><strong>Verify Payment:</strong> Confirm payment has been received</li>
                        <li><strong>Schedule Delivery:</strong> Arrange delivery based on customer preferences</li>
                        <li><strong>Update Status:</strong> Mark order as confirmed in admin panel</li>
                    </ol>
                </div>
                
                <div class="info-section">
                    <h3>📞 Customer Contact</h3>
                    <p><strong>Email:</strong> <a href="mailto:{order.customer_email}">{order.customer_email}</a></p>
                    <p><strong>Phone:</strong> <a href="tel:{order.customer_phone}">{order.customer_phone}</a></p>
                </div>
                
                <p>Best regards,<br>FitSmart System</p>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from the FitSmart system.</p>
                <p>&copy; {datetime.now().year} FitSmart. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
New Order Notification

Hello Admin,

A new order has been placed on FitSmart. Please review the details below and take necessary action.

Order Information:
- Order ID: #{order.id}
- Order Date: {order.created_at.strftime('%d/%m/%Y %I:%M %p')}
- Order Status: {order.status.title() if order.status else 'Pending'}
- Payment Status: {order.payment_status.title() if order.payment_status else 'Pending'}
- Total Amount: ₹{order.total_amount}

Customer Information:
- Name: {order.customer_name}
- Email: {order.customer_email}
- Phone: {order.customer_phone}

Delivery Information:
- Address: {order.customer_address}
- City: {order.customer_city}, {order.customer_state} - {order.customer_pincode}

Required Actions:
1. Review Order: Check if all details are correct
2. Verify Payment: Confirm payment has been received
3. Schedule Delivery: Arrange delivery based on customer preferences
4. Update Status: Mark order as confirmed in admin panel

Customer Contact:
- Email: {order.customer_email}
- Phone: {order.customer_phone}

Best regards,
FitSmart System
        """
        
        return send_email(
            to_email=admin_email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send admin new order notification: {str(e)}")
        return False

def send_admin_new_user_notification(user):
    """
    Send notification to admin about new user registration
    
    Args:
        user: User object
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@fitsmart.ca')
        subject = f"👤 New User Registration - {user.name}"
        
        html_content = f"""
        <html>
        <body>
            <h2>New User Registration</h2>
            <p>Hello Admin,</p>
            <p>A new user has registered on FitSmart.</p>
            <p>User Details:</p>
            <ul>
                <li>Name: {user.name}</li>
                <li>Email: {user.email}</li>
                <li>Phone: {user.phone or 'Not provided'}</li>
                <li>Registration Date: {user.created_at.strftime('%d/%m/%Y %I:%M %p')}</li>
            </ul>
            <p>Best regards,<br>FitSmart System</p>
        </body>
        </html>
        """
        
        text_content = f"""
New User Registration

Hello Admin,

A new user has registered on FitSmart.

User Details:
- Name: {user.name}
- Email: {user.email}
- Phone: {user.phone or 'Not provided'}
- Registration Date: {user.created_at.strftime('%d/%m/%Y %I:%M %p')}

Best regards,
FitSmart System
        """
        
        return send_email(
            to_email=admin_email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send admin new user notification: {str(e)}")
        return False

# ============================================================================
# DELIVERY STATUS EMAILS
# ============================================================================

def send_delivery_status_update_email(delivery):
    """
    Send delivery status update email
    
    Args:
        delivery: Delivery object
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = f"Delivery Update - {delivery.status.title()}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Delivery Status Update</h2>
            <p>Hello {delivery.subscription.user.name},</p>
            <p>Your delivery status has been updated to: <strong>{delivery.status.title()}</strong></p>
            <p>Delivery Details:</p>
            <ul>
                <li>Date: {delivery.delivery_date.strftime('%d/%m/%Y')}</li>
                <li>Status: {delivery.status.title()}</li>
                <li>Meal Plan: {delivery.subscription.meal_plan.name}</li>
            </ul>
            <p>Best regards,<br>The FitSmart Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
Delivery Status Update

Hello {delivery.subscription.user.name},

Your delivery status has been updated to: {delivery.status.title()}

Delivery Details:
- Date: {delivery.delivery_date.strftime('%d/%m/%Y')}
- Status: {delivery.status.title()}
- Meal Plan: {delivery.subscription.meal_plan.name}

Best regards,
The FitSmart Team
        """
        
        return send_email(
            to_email=delivery.subscription.user.email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send delivery status update email: {str(e)}")
        return False

# ============================================================================
# MEAL CANCELLATION & DONATION NOTIFICATIONS
# ============================================================================

def send_meal_cancellation_notification(subscription, meal_consumption_date, skip_type):
    """
    Send email notification to admin about cancelled meal (available for donation)
    
    Args:
        subscription: Subscription object
        meal_consumption_date: Date when customer would consume meals
        skip_type: 'donation' or 'no_delivery'
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@fitsmart.ca')
        subject = f"🎁 Meal Cancelled - Available for Donation - {meal_consumption_date.strftime('%B %d, %Y')}"
        
        # Get actual delivery date (evening before)
        from routes.subscription_management_routes import get_actual_delivery_date
        actual_delivery_date = get_actual_delivery_date(meal_consumption_date)
        
        # Count meals
        meal_count = 0
        meal_details = []
        if subscription.meal_plan.includes_breakfast:
            meal_count += 1
            meal_details.append("Breakfast")
        if subscription.meal_plan.includes_lunch:
            meal_count += 1
            meal_details.append("Lunch")
        if subscription.meal_plan.includes_dinner:
            meal_count += 1
            meal_details.append("Dinner")
        if subscription.meal_plan.includes_snacks:
            meal_count += 1
            meal_details.append("Snacks")
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {'#10b981' if skip_type == 'donation' else '#f59e0b'}; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
                .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
                .info-section {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .donation-box {{ background: #d1fae5; border: 2px solid #10b981; padding: 15px; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{'🎁 Meal Available for Donation' if skip_type == 'donation' else '⚠️ Meal Cancelled - No Delivery'}</h1>
                <p>Meal Date: {meal_consumption_date.strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="content">
                <div class="donation-box">
                    <h2>{'✅ Meal Available for Donation' if skip_type == 'donation' else '⚠️ Delivery Cancelled'}</h2>
                    <p><strong>Customer:</strong> {subscription.user.name} ({subscription.user.email})</p>
                    <p><strong>Meal Plan:</strong> {subscription.meal_plan.name}</p>
                    <p><strong>Meal Date:</strong> {meal_consumption_date.strftime('%B %d, %Y')} (delivered {actual_delivery_date.strftime('%B %d')} evening)</p>
                    <p><strong>Meals Included:</strong> {', '.join(meal_details)} ({meal_count} meals)</p>
                    <p><strong>Status:</strong> {'Available for donation to those in need' if skip_type == 'donation' else 'No delivery - meal prepared but not delivered'}</p>
                    <p><strong>Note:</strong> Customer was charged (meal already prepared)</p>
                </div>
                
                <div class="info-grid">
                    <div class="info-section">
                        <h3>👤 Customer Information</h3>
                        <p><strong>Name:</strong> {subscription.user.name}</p>
                        <p><strong>Email:</strong> {subscription.user.email}</p>
                        <p><strong>Phone:</strong> {subscription.user.phone or 'Not provided'}</p>
                        <p><strong>Subscription ID:</strong> #{subscription.id}</p>
                    </div>
                    
                    <div class="info-section">
                        <h3>🍽️ Meal Details</h3>
                        <p><strong>Meal Plan:</strong> {subscription.meal_plan.name}</p>
                        <p><strong>Meals:</strong> {', '.join(meal_details)}</p>
                        <p><strong>Total Meals:</strong> {meal_count}</p>
                        <p><strong>Vegetarian:</strong> {'Yes' if subscription.meal_plan.is_vegetarian else 'No'}</p>
                    </div>
                </div>
                
                <div class="info-section">
                    <h3>📍 Delivery Address (Not Needed)</h3>
                    <p>{subscription.delivery_address or 'N/A'}</p>
                    <p>{subscription.delivery_city or ''}, {subscription.delivery_province or ''} {subscription.delivery_postal_code or ''}</p>
                    <p class="text-muted"><em>Note: Delivery cancelled - address not needed</em></p>
                </div>
                
                <div class="donation-box">
                    <h3>{'🎁 Donation Action Required' if skip_type == 'donation' else '⚠️ Action Required'}</h3>
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        {'<li>Meal is available for donation to those in need</li>' if skip_type == 'donation' else '<li>Meal was prepared but delivery cancelled</li>'}
                        <li>Meal was already prepared (customer charged)</li>
                        <li>View in admin panel: Daily Orders → Skipped Deliveries</li>
                        <li>Coordinate donation pickup or distribution</li>
                    </ul>
                </div>
                
                <p>Best regards,<br>FitSmart System</p>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from the FitSmart system.</p>
                <p>&copy; {datetime.now().year} FitSmart. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
Meal Cancellation Notification

{'Meal Available for Donation' if skip_type == 'donation' else 'Meal Cancelled - No Delivery'}

Customer: {subscription.user.name} ({subscription.user.email})
Meal Plan: {subscription.meal_plan.name}
Meal Date: {meal_consumption_date.strftime('%B %d, %Y')} (delivered {actual_delivery_date.strftime('%B %d')} evening)
Meals Included: {', '.join(meal_details)} ({meal_count} meals)
Status: {'Available for donation to those in need' if skip_type == 'donation' else 'No delivery - meal prepared but not delivered'}
Note: Customer was charged (meal already prepared)

Customer Information:
- Name: {subscription.user.name}
- Email: {subscription.user.email}
- Phone: {subscription.user.phone or 'Not provided'}
- Subscription ID: #{subscription.id}

Meal Details:
- Meal Plan: {subscription.meal_plan.name}
- Meals: {', '.join(meal_details)}
- Total Meals: {meal_count}
- Vegetarian: {'Yes' if subscription.meal_plan.is_vegetarian else 'No'}

Next Steps:
- Meal is {'available for donation' if skip_type == 'donation' else 'prepared but delivery cancelled'}
- Meal was already prepared (customer charged)
- View in admin panel: Daily Orders → Skipped Deliveries
- Coordinate donation pickup or distribution

Best regards,
FitSmart System
        """
        
        return send_email(
            to_email=admin_email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send meal cancellation notification: {str(e)}")
        return False

def send_meal_skip_notification(subscription, meal_consumption_date):
    """
    Send email notification to admin about regular skip (before cutoff)
    
    Args:
        subscription: Subscription object
        meal_consumption_date: Date when customer would consume meals
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@fitsmart.ca')
        subject = f"✓ Meal Skipped (Regular) - {meal_consumption_date.strftime('%B %d, %Y')}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Meal Skipped (Regular Skip)</h2>
            <p>Hello Admin,</p>
            <p>A customer has skipped their meal delivery before the cutoff time.</p>
            <p><strong>Customer:</strong> {subscription.user.name} ({subscription.user.email})</p>
            <p><strong>Meal Plan:</strong> {subscription.meal_plan.name}</p>
            <p><strong>Meal Date:</strong> {meal_consumption_date.strftime('%B %d, %Y')}</p>
            <p><strong>Status:</strong> Regular skip (before cutoff) - Meal not prepared, subscription extended</p>
            <p>Best regards,<br>FitSmart System</p>
        </body>
        </html>
        """
        
        text_content = f"""
Meal Skipped (Regular Skip)

Customer: {subscription.user.name} ({subscription.user.email})
Meal Plan: {subscription.meal_plan.name}
Meal Date: {meal_consumption_date.strftime('%B %d, %Y')}
Status: Regular skip (before cutoff) - Meal not prepared, subscription extended

Best regards,
FitSmart System
        """
        
        return send_email(
            to_email=admin_email,
            from_email=os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca'),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send meal skip notification: {str(e)}")
        return False

# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_all_email_functions():
    """
    Test all email functions with sample data
    """
    from database.models import User, Order, Subscription, Delivery
    
    # Create test user
    test_user = User(
        name="Test User",
        email="test@example.com",
        phone="9876543210"
    )
    
    # Create test order
    test_order = Order(
        id=999,
        customer_name="Test Customer",
        customer_email="customer@example.com",
        customer_phone="9876543210",
        total_amount=1500.00,
        created_at=datetime.now()
    )
    
    print("🧪 Testing Email Functions...")
    
    # Test welcome email
    print("Testing welcome email...")
    result = send_welcome_email(test_user)
    print(f"Welcome email: {'✅ Success' if result else '❌ Failed'}")
    
    # Test payment success email
    print("Testing payment success email...")
    result = send_payment_success_email(test_order)
    print(f"Payment success email: {'✅ Success' if result else '❌ Failed'}")
    
    # Test payment failed email
    print("Testing payment failed email...")
    result = send_payment_failed_email(test_order)
    print(f"Payment failed email: {'✅ Success' if result else '❌ Failed'}")
    
    # Test admin notification
    print("Testing admin notification...")
    result = send_admin_new_order_notification(test_order)
    print(f"Admin notification: {'✅ Success' if result else '❌ Failed'}")
    
    print("🎉 Email function testing completed!")

if __name__ == "__main__":
    test_all_email_functions() 