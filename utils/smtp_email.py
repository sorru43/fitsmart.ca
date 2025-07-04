#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMTP Email Utility for HealthyRizz
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from flask import render_template, url_for
from flask_mail import Mail, Message

# Initialize Flask-Mail
mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app configuration"""
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'healthyrizz.in@gmail.com')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'qjrl pfep hzds ddbv')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'healthyrizz.in@gmail.com')
    
    mail.init_app(app)

def send_email(to_email, subject, html_content=None, text_content=None, attachments=None):
    """
    Send email using Flask-Mail
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        html_content (str): HTML email body
        text_content (str): Plain text email body
        attachments (list): List of attachment file paths
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html_content,
            body=text_content
        )
        
        # Add attachments if provided
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        attachment = MIMEBase('application', 'octet-stream')
                        attachment.set_payload(f.read())
                        encoders.encode_base64(attachment)
                        attachment.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(attachment)
        
        mail.send(msg)
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        return False

def send_trial_request_notification(trial_request):
    """
    Send notification email for new trial request
    
    Args:
        trial_request: TrialRequest object
    """
    subject = f"New Trial Request - {trial_request.name}"
    
    html_content = f"""
    <html>
    <body>
        <h2>New Trial Request Received</h2>
        <p><strong>Name:</strong> {trial_request.name}</p>
        <p><strong>Email:</strong> {trial_request.email}</p>
        <p><strong>Phone:</strong> {trial_request.phone}</p>
        <p><strong>Address:</strong> {trial_request.address}</p>
        <p><strong>City:</strong> {trial_request.city}</p>
        <p><strong>State:</strong> {trial_request.province}</p>
        <p><strong>PIN Code:</strong> {trial_request.postal_code}</p>
        <p><strong>Meal Plan:</strong> {trial_request.meal_plan.name if trial_request.meal_plan else 'Unknown'}</p>
        <p><strong>Requested Date:</strong> {trial_request.created_at.strftime('%Y-%m-%d %H:%M')}</p>
        
        <p>Please contact the customer to confirm delivery details.</p>
    </body>
    </html>
    """
    
    text_content = f"""
    New Trial Request Received
    
    Name: {trial_request.name}
    Email: {trial_request.email}
    Phone: {trial_request.phone}
    Address: {trial_request.address}
    City: {trial_request.city}
    State: {trial_request.province}
    PIN Code: {trial_request.postal_code}
    Meal Plan: {trial_request.meal_plan.name if trial_request.meal_plan else 'Unknown'}
    Requested Date: {trial_request.created_at.strftime('%Y-%m-%d %H:%M')}
    
    Please contact the customer to confirm delivery details.
    """
    
    # Send to admin
    admin_email = os.getenv('ADMIN_EMAIL', 'healthyrizz.in@gmail.com')
    return send_email(admin_email, subject, html_content, text_content)

def send_trial_confirmation(trial_request):
    """
    Send confirmation email to customer for trial request
    
    Args:
        trial_request: TrialRequest object
    """
    subject = "Trial Request Confirmed - HealthyRizz"
    
    html_content = f"""
    <html>
    <body>
        <h2>Thank you for your trial request!</h2>
        <p>Dear {trial_request.name},</p>
        
        <p>We have received your trial request for <strong>{trial_request.meal_plan.name if trial_request.meal_plan else 'Unknown'}</strong>.</p>
        
        <h3>Your Details:</h3>
        <ul>
            <li><strong>Name:</strong> {trial_request.name}</li>
            <li><strong>Email:</strong> {trial_request.email}</li>
            <li><strong>Phone:</strong> {trial_request.phone}</li>
            <li><strong>Delivery Address:</strong> {trial_request.address}, {trial_request.city}, {trial_request.province} - {trial_request.postal_code}</li>
        </ul>
        
        <p>Our team will contact you within 24 hours to confirm your delivery schedule.</p>
        
        <p>If you have any questions, please call us at +91-98765-43210 or email us at healthyrizz.in@gmail.com</p>
        
        <p>Best regards,<br>
        Team HealthyRizz</p>
    </body>
    </html>
    """
    
    text_content = f"""
    Thank you for your trial request!
    
    Dear {trial_request.name},
    
    We have received your trial request for {trial_request.meal_plan.name if trial_request.meal_plan else 'Unknown'}.
    
    Your Details:
    - Name: {trial_request.name}
    - Email: {trial_request.email}
    - Phone: {trial_request.phone}
    - Delivery Address: {trial_request.address}, {trial_request.city}, {trial_request.province} - {trial_request.postal_code}
    
    Our team will contact you within 24 hours to confirm your delivery schedule.
    
    If you have any questions, please call us at +91-98765-43210 or email us at healthyrizz.in@gmail.com
    
    Best regards,
    Team HealthyRizz
    """
    
    return send_email(trial_request.email, subject, html_content, text_content)

def send_order_confirmation(order):
    """
    Send order confirmation email to customer
    
    Args:
        order: Order object
    """
    subject = f"Order Confirmed - Order #{order.id}"
    
    html_content = f"""
    <html>
    <body>
        <h2>Order Confirmed!</h2>
        <p>Dear {order.customer_name},</p>
        
        <p>Thank you for your order. Your order has been confirmed and is being processed.</p>
        
        <h3>Order Details:</h3>
        <ul>
            <li><strong>Order ID:</strong> #{order.id}</li>
            <li><strong>Order Date:</strong> {order.created_at.strftime('%Y-%m-%d %H:%M')}</li>
            <li><strong>Total Amount:</strong> ₹{order.total_amount}</li>
            <li><strong>Delivery Address:</strong> {order.delivery_address}</li>
        </ul>
        
        <p>We will notify you when your order is ready for delivery.</p>
        
        <p>Best regards,<br>
        Team HealthyRizz</p>
    </body>
    </html>
    """
    
    text_content = f"""
    Order Confirmed!
    
    Dear {order.customer_name},
    
    Thank you for your order. Your order has been confirmed and is being processed.
    
    Order Details:
    - Order ID: #{order.id}
    - Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}
    - Total Amount: ₹{order.total_amount}
    - Delivery Address: {order.delivery_address}
    
    We will notify you when your order is ready for delivery.
    
    Best regards,
    Team HealthyRizz
    """
    
    return send_email(order.customer_email, subject, html_content, text_content)

def send_delivery_notification(order):
    """
    Send delivery notification email to customer
    
    Args:
        order: Order object
    """
    subject = f"Your order is out for delivery - Order #{order.id}"
    
    html_content = f"""
    <html>
    <body>
        <h2>Your order is on the way!</h2>
        <p>Dear {order.customer_name},</p>
        
        <p>Great news! Your order #{order.id} is out for delivery and will reach you soon.</p>
        
        <p><strong>Expected Delivery:</strong> Today between 6:00 PM - 8:00 PM</p>
        <p><strong>Delivery Address:</strong> {order.delivery_address}</p>
        
        <p>Please ensure someone is available to receive the delivery.</p>
        
        <p>If you have any questions, please call us at +91-98765-43210</p>
        
        <p>Best regards,<br>
        Team HealthyRizz</p>
    </body>
    </html>
    """
    
    text_content = f"""
    Your order is on the way!
    
    Dear {order.customer_name},
    
    Great news! Your order #{order.id} is out for delivery and will reach you soon.
    
    Expected Delivery: Today between 6:00 PM - 8:00 PM
    Delivery Address: {order.delivery_address}
    
    Please ensure someone is available to receive the delivery.
    
    If you have any questions, please call us at +91-98765-43210
    
    Best regards,
    Team HealthyRizz
    """
    
    return send_email(order.customer_email, subject, html_content, text_content)

def send_water_reminder(user_email, user_name):
    """
    Send water reminder email to user
    
    Args:
        user_email (str): User's email address
        user_name (str): User's name
    """
    subject = "Time to hydrate! 💧 - HealthyRizz"
    
    html_content = f"""
    <html>
    <body>
        <h2>💧 Time to drink water!</h2>
        <p>Hi {user_name},</p>
        
        <p>Don't forget to stay hydrated! It's time for your water break.</p>
        
        <p><strong>Benefits of staying hydrated:</strong></p>
        <ul>
            <li>Boosts energy levels</li>
            <li>Improves digestion</li>
            <li>Helps with weight management</li>
            <li>Keeps your skin healthy</li>
        </ul>
        
        <p>Remember to drink at least 8 glasses of water daily!</p>
        
        <p>Best regards,<br>
        Team HealthyRizz</p>
    </body>
    </html>
    """
    
    text_content = f"""
    Time to drink water!
    
    Hi {user_name},
    
    Don't forget to stay hydrated! It's time for your water break.
    
    Benefits of staying hydrated:
    - Boosts energy levels
    - Improves digestion
    - Helps with weight management
    - Keeps your skin healthy
    
    Remember to drink at least 8 glasses of water daily!
    
    Best regards,
    Team HealthyRizz
    """
    
    return send_email(user_email, subject, html_content, text_content)

def test_smtp_connection():
    """Test SMTP connection and send a test email"""
    try:
        # Get SMTP settings
        smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('MAIL_PORT', 587))
        username = os.getenv('MAIL_USERNAME', 'healthyrizz.in@gmail.com')
        password = os.getenv('MAIL_PASSWORD', 'qjrl pfep hzds ddbv')
        
        # Test connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.quit()
        
        print("✅ SMTP connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ SMTP connection test failed: {e}")
        return False 