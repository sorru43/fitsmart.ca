from flask import current_app, render_template
from flask_mail import Message
from extensions import mail

def send_order_confirmation_email(order):
    """Send order confirmation email to customer."""
    msg = Message(
        'Order Confirmation - Fit Smart',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[order.customer_email]
    )
    
    # Email body in HTML format
    msg.html = render_template(
        'email/order_confirmation.html',
        order=order,
        customer_name=order.customer_name
    )
    
    # Send email
    mail.send(msg)

def send_delivery_notification_email(order):
    """Send delivery notification email to customer."""
    msg = Message(
        'Your Fit Smart Delivery is on the way!',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[order.customer_email]
    )
    
    # Email body in HTML format
    msg.html = render_template(
        'email/delivery_notification.html',
        order=order,
        customer_name=order.customer_name
    )
    
    # Send email
    mail.send(msg) 