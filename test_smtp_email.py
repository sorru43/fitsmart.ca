#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean SMTP Test Script
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_smtp():
    """Test SMTP connection"""
    
    # Configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "healthyrizz.in@gmail.com"
    password = "qjrl pfep hzds ddbv"
    
    # Email details
    sender = username
    recipient = username  # Send to yourself
    subject = f"SMTP Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Simple message
    body = f"""
SMTP Test Email

This is a test email from HealthyRizz.
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you receive this, SMTP is working!
    """.strip()
    
    try:
        print("Testing SMTP...")
        print(f"Server: {smtp_server}")
        print(f"Username: {username}")
        print(f"Recipient: {recipient}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        
        text = msg.as_string()
        server.sendmail(sender, recipient, text)
        server.quit()
        
        print("SUCCESS: Email sent!")
        print(f"Check inbox: {recipient}")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("SMTP Test")
    print("=" * 30)
    test_smtp() 