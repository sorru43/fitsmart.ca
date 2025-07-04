import os
import sys
from flask import current_app as app, url_for
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, 
                                  FileName, FileType, Disposition, ContentId)
import base64
from io import BytesIO
import mimetypes
from datetime import datetime
from flask_mail import Message
from extensions import mail

def send_email(to_email, from_email, subject, html_content=None, text_content=None, attachments=None):
    """
    Send an email using SendGrid
    
    Args:
        to_email (str): Recipient email address
        from_email (str): Sender email address
        subject (str): Email subject
        html_content (str, optional): HTML content of the email
        text_content (str, optional): Text content of the email (fallback for HTML)
        attachments (list, optional): List of attachment dictionaries with 'filename' and either 'path' or 'content'
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    sendgrid_key = os.environ.get('SENDGRID_API_KEY')
    if not sendgrid_key:
        app.logger.error("SendGrid API key is not set")
        return False
    
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject
    )
    
    # Add content
    if html_content:
        message.add_content(html_content, 'text/html')
    if text_content:
        message.add_content(text_content, 'text/plain')
    
    # Add attachments
    if attachments:
        for attachment_data in attachments:
            attachment = Attachment()
            
            if 'path' in attachment_data:
                # File is on disk
                with open(attachment_data['path'], 'rb') as f:
                    content = base64.b64encode(f.read()).decode()
                    mime_type = mimetypes.guess_type(attachment_data['path'])[0]
            elif 'content' in attachment_data:
                # Content is provided as bytes
                if isinstance(attachment_data['content'], bytes):
                    content = base64.b64encode(attachment_data['content']).decode()
                else:
                    content = base64.b64encode(attachment_data['content']).decode()
                
                # Try to guess mime type from filename
                mime_type = mimetypes.guess_type(attachment_data['filename'])[0]
                
                # Default mime types for common extensions
                if not mime_type:
                    ext = attachment_data['filename'].split('.')[-1].lower()
                    if ext == 'pdf':
                        mime_type = 'application/pdf'
                    elif ext == 'csv':
                        mime_type = 'text/csv'
                    elif ext in ['jpg', 'jpeg']:
                        mime_type = 'image/jpeg'
                    elif ext == 'png':
                        mime_type = 'image/png'
                    else:
                        mime_type = 'application/octet-stream'
            else:
                # Skip if neither path nor content is provided
                continue
            
            attachment.file_content = FileContent(content)
            attachment.file_name = FileName(attachment_data['filename'])
            attachment.file_type = FileType(mime_type)
            attachment.disposition = Disposition('attachment')
            attachment.content_id = ContentId(attachment_data['filename'])
            
            message.add_attachment(attachment)
    
    # Send email
    try:
        sg = SendGridAPIClient(sendgrid_key)
        response = sg.send(message)
        
        # Log the response status
        app.logger.info(f"SendGrid response status: {response.status_code}")
        
        # Return True if status code is 2xx
        return 200 <= response.status_code < 300
        
    except Exception as e:
        app.logger.error(f"Error sending email: {str(e)}")
        return False
        
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
    from_email = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@healthyrizz.in')
    
    # Create the email subject
    subject = f"HealthyRizz Delivery Update: {delivery_status.capitalize()}"
    
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
                <h1>HealthyRizz Delivery Update</h1>
            </div>
            <div class="content">
                <p>Hello {customer_name},</p>
                
                <p>We have an update regarding your HealthyRizz meal delivery scheduled for <strong>{formatted_date}</strong>.</p>
                
                <p>Your delivery status is now: <span class="status">{delivery_status.capitalize()}</span></p>
                
                <div class="message">
                    <p>{message_text}</p>
                </div>
                
                <p>You can view more details about your delivery by logging into your account:</p>
                
                <a href="https://healthyrizz.in/login" class="button">View Delivery Details</a>
                
                <p>If you have any questions, please contact our customer support team.</p>
                
                <p>Thank you for choosing HealthyRizz for your nutritional needs!</p>
                
                <p>Warm regards,<br>The HealthyRizz Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>&copy; {datetime.now().year} HealthyRizz. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create the text content (fallback for email clients that don't support HTML)
    text_content = f"""
Hello {customer_name},

We have an update regarding your HealthyRizz meal delivery scheduled for {formatted_date}.

Your delivery status is now: {delivery_status.capitalize()}

Message: {message_text}

You can view more details about your delivery by logging into your account at https://healthyrizz.in/login

If you have any questions, please contact our customer support team.

Thank you for choosing HealthyRizz for your nutritional needs!

Warm regards,
The HealthyRizz Team

This is an automated message. Please do not reply to this email.
© {datetime.now().year} HealthyRizz. All rights reserved.
    """
    
    # Send the email
    return send_email(to_email, from_email, subject, html_content, text_content)

def send_password_reset_email(to_email, token):
    """Send a password reset email to the user"""
    reset_url = url_for('main.reset_password', token=token, _external=True)
    msg = Message(
        subject="Password Reset Request - HealthyRizz",
        sender=current_app.config.get("MAIL_DEFAULT_SENDER", "noreply@healthyrizz.in"),
        recipients=[to_email]
    )
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email.
'''
    mail.send(msg)

def send_contact_notification(inquiry):
    """
    Send a notification email to admin about a new contact inquiry
    
    Args:
        inquiry (ContactInquiry): The contact inquiry object
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Get admin email from environment or use default
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@healthyrizz.in')
    from_email = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@healthyrizz.in')
    
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
                    <p>This is an automated notification from the HealthyRizz contact form.</p>
                    <p>Inquiry ID: {inquiry.id}</p>
                    <p>&copy; {datetime.now().year} HealthyRizz. All rights reserved.</p>
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