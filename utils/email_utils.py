import os
import sys
from flask import current_app as app, url_for
from datetime import datetime
from flask_mail import Message
from extensions import mail

def send_email_flask_mail(to_email, subject, html_content=None, text_content=None):
    """
    Send email using Flask-Mail (SMTP) instead of SendGrid
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        html_content (str, optional): HTML content
        text_content (str, optional): Text content
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        from flask import current_app
        from flask_mail import Message
        from extensions import mail
        
        # Get SMTP configuration from environment variables
        smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('MAIL_PORT', 587))
        username = os.getenv('MAIL_USERNAME', 'info@fitsmart.ca')
        password = os.getenv('MAIL_PASSWORD', '')
        default_sender = os.getenv('MAIL_DEFAULT_SENDER', 'info@fitsmart.ca')
        
        # Create message with proper sender
        msg = Message(
            subject=subject,
            sender=default_sender,
            recipients=[to_email]
        )
        
        if html_content:
            msg.html = html_content
        if text_content:
            msg.body = text_content
        elif html_content:
            # Strip HTML tags for text fallback
            import re
            msg.body = re.sub(r'<[^>]+>', '', html_content)
        
        # Send email
        mail.send(msg)
        current_app.logger.info(f"Email sent successfully to {to_email}")
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to_email}: {str(e)}")
        print(f"❌ Error sending email to {to_email}: {e}")
        return False

def send_email(to_email, from_email, subject, html_content=None, text_content=None, attachments=None):
    """
    Send email using Flask-Mail (SMTP) - Updated to work with Gmail
    
    Args:
        to_email (str): Recipient email address
        from_email (str): Sender email address (ignored, uses config)
        subject (str): Email subject
        html_content (str, optional): HTML content
        text_content (str, optional): Text content
        attachments (list, optional): List of attachments (not implemented yet)
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    return send_email_flask_mail(to_email, subject, html_content, text_content)
        
def send_delivery_status_email(to_email, customer_name, delivery_date, message_text, delivery_status):
    """
    Send an email notification about a delivery status update
    
    Args:
        to_email (str): Customer's email address
        customer_name (str): Customer's name
        delivery_date (datetime.date): Date of the delivery
        message_text (str): Custom message about the delivery
        delivery_status (str): Current status of the delivery
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Format the delivery date
    formatted_date = delivery_date
    if hasattr(delivery_date, 'strftime'):
        formatted_date = delivery_date.strftime('%A, %B %d, %Y')
    
    # Default sender from environment variable or use a fallback
    from_email = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca')
    
    # Create the email subject
    subject = f"FitSmart Delivery Update: {delivery_status.capitalize()}"
    
    # Create the HTML content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #379777; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .message {{ border-left: 4px solid #379777; padding-left: 15px; margin: 20px 0; }}
            .footer {{ font-size: 12px; color: #777; padding-top: 20px; border-top: 1px solid #eee; }}
            .button {{ display: inline-block; background-color: #379777; color: white; padding: 10px 20px; 
                      text-decoration: none; border-radius: 4px; margin-top: 20px; }}
            .status {{ font-weight: bold; color: #379777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>FitSmart Delivery Update</h1>
            </div>
            <div class="content">
                <p>Hello {customer_name},</p>
                
                <p>We have an update regarding your FitSmart meal delivery scheduled for <strong>{formatted_date}</strong>.</p>
                
                <p>Your delivery status is now: <span class="status">{delivery_status.capitalize()}</span></p>
                
                <div class="message">
                    <p>{message_text}</p>
                </div>
                
                <p>You can view more details about your delivery by logging into your account:</p>
                
                <a href="https://fitsmart.ca/login" class="button">View Delivery Details</a>
                
                <p>If you have any questions, please contact our customer support team.</p>
                
                <p>Thank you for choosing FitSmart for your nutritional needs!</p>
                
                <p>Warm regards,<br>The FitSmart Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>&copy; {datetime.now().year} FitSmart. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create the text content (fallback for email clients that don't support HTML)
    text_content = f"""
Hello {customer_name},

We have an update regarding your FitSmart meal delivery scheduled for {formatted_date}.

Your delivery status is now: {delivery_status.capitalize()}

Message: {message_text}

You can view more details about your delivery by logging into your account at https://fitsmart.ca/login

If you have any questions, please contact our customer support team.

Thank you for choosing FitSmart for your nutritional needs!

Warm regards,
The FitSmart Team

This is an automated message. Please do not reply to this email.
© {datetime.now().year} FitSmart. All rights reserved.
    """
    
    # Send the email
    return send_email(to_email, from_email, subject, html_content, text_content)

def send_password_reset_email(to_email, token):
    """Send a password reset email to the user"""
    try:
        # Use hardcoded URL instead of url_for to avoid request context issues
        reset_url = f"https://fitsmart.ca/reset-password/{token}"
        
        subject = "Password Reset Request - FitSmart 🔐"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
                .reset-box {{ background: #d1fae5; border: 1px solid #10b981; padding: 15px; border-radius: 6px; margin: 15px 0; text-align: center; }}
                .warning {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 6px; margin: 15px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 20px; }}
                .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔐 Password Reset Request</h1>
                <p>FitSmart - Secure Your Account</p>
            </div>
            
            <div class="content">
                <p>Hello,</p>
                
                <p>We received a request to reset your password for your FitSmart account. If you made this request, please use the button below to create a new password.</p>
                
                <div class="reset-box">
                    <h2>🔄 Reset Your Password</h2>
                    <p>Click the button below to reset your password:</p>
                    
                    <a href="{reset_url}" class="button">Reset Password</a>
                    
                    <p style="margin-top: 20px; font-size: 14px; color: #666;">
                        If the button doesn't work, copy and paste this link into your browser:<br>
                        <a href="{reset_url}" style="color: #379777; word-break: break-all;">{reset_url}</a>
                    </p>
                </div>
                
                <div class="warning">
                    <h3>⚠️ Security Notice</h3>
                    <ul>
                        <li>This password reset link will expire in <strong>1 hour</strong></li>
                        <li>If you didn't request this password reset, please ignore this email</li>
                        <li>Your current password will remain unchanged until you complete the reset</li>
                    </ul>
                </div>
                
                <h3>🔒 Password Security Tips:</h3>
                <ul>
                    <li>Use at least 8 characters</li>
                    <li>Include a mix of uppercase and lowercase letters</li>
                    <li>Add numbers and special characters</li>
                    <li>Avoid using personal information</li>
                    <li>Don't reuse passwords from other accounts</li>
                </ul>
                
                <p>If you didn't request this password reset, it's possible that someone else entered your email address by mistake. You can safely ignore this email.</p>
                
                <p>Need help? Contact us:<br>
                📧 Email: fitsmart.ca@gmail.com<br>
                📞 Phone: +91-98765-43210</p>
                
                <p>Best regards,<br>
                The FitSmart Security Team</p>
            </div>
            
            <div class="footer">
                <p>This email was sent to {to_email}</p>
                <p>If you didn't request a password reset, please ignore this email.</p>
                <p>&copy; {datetime.now().year} FitSmart. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
Password Reset Request - FitSmart

Hello,

We received a request to reset your password for your FitSmart account. If you made this request, please use the link below to create a new password.

Reset your password:
{reset_url}

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

If you didn't request this password reset, it's possible that someone else entered your email address by mistake. You can safely ignore this email.

Need help? Contact us:
- Email: fitsmart.ca@gmail.com
- Phone: +91-98765-43210

Best regards,
The FitSmart Security Team

This email was sent to {to_email}
If you didn't request a password reset, please ignore this email.
© {datetime.now().year} FitSmart. All rights reserved.
        """
        
        # Use the working send_email function
        return send_email(
            to_email=to_email,
            from_email="fitsmart.ca@gmail.com",
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        print(f"❌ Error sending password reset email to {to_email}: {e}")
        return False

def send_contact_notification(inquiry):
    """
    Send a notification email to admin about a new contact inquiry
    
    Args:
        inquiry (ContactInquiry): The contact inquiry object
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Get admin email from environment or use default
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@fitsmart.ca')
    from_email = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@fitsmart.ca')
    
    # Create the email subject
    subject = f"New Contact Inquiry: {inquiry.inquiry_type.replace('_', ' ').title()} - {inquiry.name}"
    
    # Format inquiry type for display
    inquiry_type_display = inquiry.inquiry_type.replace('_', ' ').title()
    
    # Create the HTML content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #379777; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
            .info-section {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
            .priority-urgent {{ background-color: #ffebee; border-left: 4px solid #f44336; }}
            .priority-high {{ background-color: #fff3e0; border-left: 4px solid #ff9800; }}
            .priority-normal {{ background-color: #e8f5e8; border-left: 4px solid #4caf50; }}
            .priority-low {{ background-color: #f5f5f5; border-left: 4px solid #9e9e9e; }}
            .message-box {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .footer {{ font-size: 12px; color: #777; padding-top: 20px; border-top: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>New Contact Inquiry</h1>
                <p>Inquiry Type: {inquiry_type_display}</p>
            </div>
            <div class="content">
                <div class="info-grid">
                    <div class="info-section">
                        <h3>Contact Information</h3>
                        <p><strong>Name:</strong> {inquiry.name}</p>
                        <p><strong>Email:</strong> {inquiry.email}</p>
                        <p><strong>Phone:</strong> {inquiry.phone or 'Not provided'}</p>
                        <p><strong>Subject:</strong> {inquiry.subject}</p>
                    </div>
                    <div class="info-section priority-{inquiry.priority}">
                        <h3>Inquiry Details</h3>
                        <p><strong>Type:</strong> {inquiry_type_display}</p>
                        <p><strong>Priority:</strong> {inquiry.priority.title()}</p>
                        <p><strong>Status:</strong> {inquiry.status.title()}</p>
                        <p><strong>Created:</strong> {inquiry.created_at.strftime('%Y-%m-%d %H:%M')}</p>
                    </div>
                </div>
                
                <div class="message-box">
                    <h3>Message</h3>
                    <p>{inquiry.message}</p>
                </div>
    """
    
    # Add specific fields based on inquiry type
    if inquiry.inquiry_type == 'location_request':
        html_content += f"""
                <div class="info-section">
                    <h3>Location Details</h3>
                    <p><strong>City:</strong> {inquiry.city or 'Not provided'}</p>
                    <p><strong>State:</strong> {inquiry.state or 'Not provided'}</p>
                    <p><strong>PIN Code:</strong> {inquiry.pincode or 'Not provided'}</p>
                </div>
        """
    elif inquiry.inquiry_type == 'franchise':
        html_content += f"""
                <div class="info-section">
                    <h3>Franchise Information</h3>
                    <p><strong>Investment Range:</strong> {inquiry.investment_range or 'Not provided'}</p>
                    <p><strong>Business Experience:</strong> {inquiry.business_experience or 'Not provided'}</p>
                    <p><strong>Preferred Location:</strong> {inquiry.preferred_location or 'Not provided'}</p>
                </div>
        """
    elif inquiry.inquiry_type == 'expert_consultation':
        html_content += f"""
                <div class="info-section">
                    <h3>Consultation Details</h3>
                    <p><strong>Consultation Type:</strong> {inquiry.consultation_type or 'Not provided'}</p>
                    <p><strong>Preferred Time:</strong> {inquiry.preferred_time or 'Not provided'}</p>
                    <p><strong>Preferred Date:</strong> {inquiry.preferred_date.strftime('%Y-%m-%d') if inquiry.preferred_date else 'Not specified'}</p>
                </div>
        """
    
    html_content += f"""
                <div class="footer">
                    <p>This is an automated notification from the FitSmart contact form.</p>
                    <p>Inquiry ID: {inquiry.id}</p>
                    <p>&copy; {datetime.now().year} FitSmart. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create the text content (fallback for email clients that don't support HTML)
    text_content = f"""
New Contact Inquiry

Inquiry Type: {inquiry_type_display}
Name: {inquiry.name}
Email: {inquiry.email}
Phone: {inquiry.phone or 'Not provided'}
Subject: {inquiry.subject}
Priority: {inquiry.priority.title()}
Status: {inquiry.status.title()}
Created: {inquiry.created_at.strftime('%Y-%m-%d %H:%M')}

Message:
{inquiry.message}

"""
    
    # Add specific fields to text content
    if inquiry.inquiry_type == 'location_request':
        text_content += f"""
Location Details:
City: {inquiry.city or 'Not provided'}
State: {inquiry.state or 'Not provided'}
PIN Code: {inquiry.pincode or 'Not provided'}
"""
    elif inquiry.inquiry_type == 'franchise':
        text_content += f"""
Franchise Information:
Investment Range: {inquiry.investment_range or 'Not provided'}
Business Experience: {inquiry.business_experience or 'Not provided'}
Preferred Location: {inquiry.preferred_location or 'Not provided'}
"""
    elif inquiry.inquiry_type == 'expert_consultation':
        text_content += f"""
Consultation Details:
Consultation Type: {inquiry.consultation_type or 'Not provided'}
Preferred Time: {inquiry.preferred_time or 'Not provided'}
Preferred Date: {inquiry.preferred_date.strftime('%Y-%m-%d') if inquiry.preferred_date else 'Not specified'}
"""
    
    text_content += f"""
Inquiry ID: {inquiry.id}
"""
    
    # Send the email
    return send_email(admin_email, from_email, subject, html_content, text_content)