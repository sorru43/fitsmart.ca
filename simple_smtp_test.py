#!/usr/bin/env python3
"""
Simple SMTP Test Script - Plain Text Email
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_smtp_connection():
    """Test SMTP connection and send a simple email"""
    
    # SMTP Configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "healthyrizz.in@gmail.com"
    password = "qjrl pfep hzds ddbv"  # Replace with your actual app password
    
    # Email details
    sender_email = username
    recipient_email = "healthyrizz.in@gmail.com"  # Send to yourself for testing
    subject = f"SMTP Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Simple plain text message
    message_body = f"""
Hello from HealthyRizz!

This is a test email sent via SMTP to verify the email configuration.

Test Details:
- Server: {smtp_server}
- Port: {smtp_port}
- Username: {username}
- Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you receive this email, SMTP is working correctly!

Best regards,
HealthyRizz Team
    """.strip()
    
    try:
        print("🧪 Testing SMTP Connection...")
        print(f"Server: {smtp_server}:{smtp_port}")
        print(f"Username: {username}")
        print(f"Recipient: {recipient_email}")
        print("-" * 50)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add plain text body
        msg.attach(MIMEText(message_body, 'plain'))
        
        # Connect to SMTP server
        print("📡 Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Login
        print("🔐 Logging in...")
        server.login(username, password)
        
        # Send email
        print("📧 Sending test email...")
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        
        # Close connection
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"📬 Check your inbox: {recipient_email}")
        print(f"📧 Subject: {subject}")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Make sure your app password is correct")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple SMTP Test")
    print("=" * 50)
    
    # Check if password is set
    if "your_app_password_here" in open(__file__).read():
        print("⚠️  Please update the password in this script first!")
        print("   Replace 'your_app_password_here' with your actual Gmail app password")
        exit(1)
    
    success = test_smtp_connection()
    
    if success:
        print("\n🎉 SMTP is working correctly!")
        print("   You can now use email notifications in your app.")
    else:
        print("\n❌ SMTP test failed!")
        print("   Check your configuration and try again.") 