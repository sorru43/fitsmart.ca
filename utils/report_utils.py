import os
import csv
import pandas as pd
from datetime import datetime, timedelta
import json

# Import fpdf2 for PDF generation with better error handling
try:
    # First try to import fpdf2
    from fpdf2 import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    try:
        # Fallback to fpdf if fpdf2 is not available
        from fpdf import FPDF
        FPDF_AVAILABLE = True
    except ImportError:
        # If neither is available, create a dummy class
        class FPDF:
            def __init__(self, *args, **kwargs):
                raise ImportError("Neither fpdf2 nor fpdf is installed. Please install one with: pip install fpdf2")
        FPDF_AVAILABLE = False

from io import BytesIO
import tempfile
from flask import current_app as app

from database.models import (
    Subscription, SkippedDelivery, User, MealPlan, 
    SubscriptionStatus, db, DeliveryStatus, Delivery, 
    SubscriptionFrequency
)
from utils.email_utils import send_email
from utils.timezone_utils import convert_to_ist

def get_daily_orders(date=None):
    """
    Get real orders for a specific date from the database.
    Filters out skipped meals and inactive subscriptions.
    
    Args:
        date (datetime.date, optional): The date to get orders for. Defaults to today.
        
    Returns:
        list: List of active order dictionaries from real database data
    """
    if not date:
        date = datetime.now().date()
    
    try:
        # Get all active subscriptions
        active_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).all()
        
        orders = []
        
        for subscription in active_subscriptions:
            # Check if this subscription should have a delivery on the given date
            if should_deliver_on_date(subscription, date):
                user = subscription.user
                meal_plan = subscription.meal_plan
                
                # Check if delivery is skipped for this date
                skipped_delivery = SkippedDelivery.query.filter_by(
                    subscription_id=subscription.id,
                    delivery_date=date
                ).first()
                
                if skipped_delivery:
                    continue  # Skip this delivery
                
                # Get existing delivery record if it exists
                delivery = Delivery.query.filter_by(
                    subscription_id=subscription.id,
                    delivery_date=date
                ).first()
                
                # Determine if this is a vegetarian day
                veg_days = []
                if subscription.vegetarian_days:
                    try:
                        veg_days = json.loads(subscription.vegetarian_days)
                    except:
                        veg_days = []
                
                weekday = date.weekday()  # 0 = Monday, 6 = Sunday
                is_veg_day = weekday in veg_days or meal_plan.is_vegetarian
                
                # Convert created_at to IST before formatting
                created_at_ist = convert_to_ist(subscription.created_at)
                
                # Create order dictionary
                order = {
                    'id': subscription.id,
                    'user_id': user.id,
                    'user_name': user.name,
                    'user_email': user.email,
                    'user_phone': user.phone,
                    'delivery_address': subscription.delivery_address,
                    'delivery_city': subscription.delivery_city,
                    'delivery_state': subscription.delivery_province,  # Using province as state
                    'delivery_postal_code': subscription.delivery_postal_code,
                    'meal_plan_name': meal_plan.name,
                    'is_vegetarian': is_veg_day,
                    'with_breakfast': meal_plan.includes_breakfast,  # Use meal plan setting instead
                    'notes': '',  # No delivery_notes field in Subscription model
                    'subscription_id': subscription.id,
                    'delivery_status': delivery.status.value if delivery else 'PENDING',
                    'is_skipped': False,
                    'subscription_status': subscription.status.value,
                    'delivery_id': delivery.id if delivery else None,
                    'created_at': created_at_ist.strftime('%Y-%m-%d %H:%M:%S'),
                    'frequency': subscription.frequency.value,
                    'delivery_days': subscription.delivery_days
                }
                
                orders.append(order)
        
        return orders
        
    except Exception as e:
        app.logger.error(f"Error getting daily orders: {str(e)}")
        # Fallback to sample data if there's an error
        return create_sample_orders(date)

def should_deliver_on_date(subscription, check_date):
    """
    Check if a subscription should have a delivery on a specific date
    
    Args:
        subscription: Subscription object
        check_date: datetime.date object to check
        
    Returns:
        bool: True if delivery should happen on this date
    """
    try:
        # Parse delivery days
        delivery_days = []
        if subscription.delivery_days:
            try:
                delivery_days = json.loads(subscription.delivery_days)
            except:
                delivery_days = []
        
        # If no delivery days specified, assume daily delivery
        if not delivery_days:
            return True
        
        # Get the weekday (0 = Monday, 6 = Sunday)
        weekday = check_date.weekday()
        
        # Check if this weekday is in the delivery days
        return weekday in delivery_days
        
    except Exception as e:
        app.logger.error(f"Error checking delivery date: {str(e)}")
        return True  # Default to True if there's an error

def get_skipped_deliveries(date):
    """
    Get deliveries that have been skipped for a specific date
    This includes both SkippedDelivery records and cancelled deliveries
    
    Args:
        date (datetime.date): The date to get skipped deliveries for
        
    Returns:
        list: List of dictionaries containing skipped delivery information
    """
    try:
        skipped = []
        
        # 1. Get skipped deliveries from SkippedDelivery table
        skipped_deliveries = SkippedDelivery.query.filter_by(
            delivery_date=date
        ).all()
        
        for skipped_delivery in skipped_deliveries:
            subscription = Subscription.query.get(skipped_delivery.subscription_id)
            if not subscription:
                continue
                
            user = User.query.get(subscription.user_id)
            meal_plan = MealPlan.query.get(subscription.meal_plan_id)
            
            if not user or not meal_plan:
                continue
                
            skip_type = getattr(skipped_delivery, 'skip_type', 'regular')
            skip_notes = getattr(skipped_delivery, 'notes', '')
            skipped.append({
                'subscription_id': subscription.id,
                'user_id': user.id,
                'user_name': user.name,
                'user_email': user.email,
                'user_phone': user.phone,
                'meal_plan_name': meal_plan.name,
                'delivery_date': date,
                'delivery_id': None,  # No delivery record for skipped meals
                'notes': skip_notes or f'Skipped by customer on {skipped_delivery.created_at.strftime("%Y-%m-%d %H:%M")}',
                'skip_type': skip_type,  # 'regular', 'donation', 'no_delivery'
                'skip_type_display': 'Regular Skip' if skip_type == 'regular' else 'Donation' if skip_type == 'donation' else 'No Delivery',
                'available_for_donation': skip_type in ['donation', 'regular'],
                'skip_date': skipped_delivery.created_at,
                'delivery_address': subscription.delivery_address,
                'delivery_city': subscription.delivery_city,
                'delivery_state': subscription.delivery_province,
                'delivery_postal_code': subscription.delivery_postal_code
            })
        
        # 2. Get cancelled deliveries from Delivery table
        cancelled_deliveries = Delivery.query.filter_by(
            delivery_date=date,
            status=DeliveryStatus.CANCELLED
        ).all()
        
        for delivery in cancelled_deliveries:
            subscription = Subscription.query.get(delivery.subscription_id)
            user = User.query.get(delivery.user_id)
            meal_plan = MealPlan.query.get(subscription.meal_plan_id) if subscription else None
            
            if not user or not meal_plan:
                continue
                
            skipped.append({
                'subscription_id': delivery.subscription_id,
                'user_id': user.id,
                'user_name': user.name,
                'user_email': user.email,
                'user_phone': user.phone,
                'meal_plan_name': meal_plan.name,
                'delivery_date': date,
                'delivery_id': delivery.id,
                'notes': delivery.notes or 'Cancelled by admin',
                'skip_type': 'admin_cancelled',
                'delivery_address': subscription.delivery_address if subscription else 'N/A',
                'delivery_city': subscription.delivery_city if subscription else 'N/A',
                'delivery_state': subscription.delivery_province if subscription else 'N/A',
                'delivery_postal_code': subscription.delivery_postal_code if subscription else 'N/A'
            })
                
        return skipped
        
    except Exception as e:
        app.logger.error(f"Error getting skipped deliveries: {str(e)}")
        return []

def generate_orders_spreadsheet(date_str=None):
    """Generate a CSV spreadsheet of orders and skipped deliveries for a specific date"""
    temp_file = None
    try:
        # Parse date if provided
        target_date = None
        if date_str:
            try:
                if isinstance(date_str, str):
                    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:
                    target_date = date_str  # Assume it's already a date object
            except ValueError:
                app.logger.error(f"Invalid date format: {date_str}")
                return None
        else:
            target_date = datetime.now().date()

        # Get orders and skipped deliveries
        orders = get_daily_orders(target_date)
        skipped_deliveries = get_skipped_deliveries(target_date)

        # Create temporary file with a unique name
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='')
        
        writer = csv.writer(temp_file)
        
        # Write headers
        writer.writerow([
            'Order ID', 'Customer Name', 'Email', 'Phone', 'Address',
            'City', 'Province', 'Postal Code', 'Meal Plan', 'Status',
            'Delivery Date', 'Created At'
        ])
        
        # Write orders
        for order in orders:
            writer.writerow([
                order.get('subscription_id', 'N/A'),
                order.get('user_name', 'N/A'),
                order.get('user_email', 'N/A'),
                order.get('user_phone', 'N/A'),
                order.get('delivery_address', 'N/A'),
                order.get('delivery_city', 'N/A'),
                order.get('delivery_province', 'N/A'),
                order.get('delivery_postal_code', 'N/A'),
                order.get('meal_plan_name', 'N/A'),
                order.get('delivery_status', 'Active'),
                target_date.strftime('%Y-%m-%d'),
                order.get('created_at', 'N/A')
            ])

        # Write summary section
        writer.writerow([])  # Empty row as separator
        writer.writerow(['SUMMARY'])
        writer.writerow(['Total Active Orders', len(orders)])
        writer.writerow(['Total Skipped Meals', len(skipped_deliveries)])
        writer.writerow(['Net Meals to Prepare', len(orders) - len(skipped_deliveries)])

        # Write skipped deliveries section
        if skipped_deliveries:
            writer.writerow([])  # Empty row as separator
            writer.writerow(['SKIPPED DELIVERIES'])
            writer.writerow([
                'Subscription ID', 'Customer Name', 'Email', 'Phone', 'Address',
                'City', 'Province', 'Postal Code', 'Meal Plan', 'Skip Type', 'Notes',
                'Delivery Date'
            ])
            
            for skip in skipped_deliveries:
                writer.writerow([
                    skip.get('subscription_id', 'N/A'),
                    skip.get('user_name', 'N/A'),
                    skip.get('user_email', 'N/A'),
                    skip.get('user_phone', 'N/A'),
                    skip.get('delivery_address', 'N/A'),
                    skip.get('delivery_city', 'N/A'),
                    skip.get('delivery_state', 'N/A'),
                    skip.get('delivery_postal_code', 'N/A'),
                    skip.get('meal_plan_name', 'N/A'),
                    skip.get('skip_type', 'N/A'),
                    skip.get('notes', 'N/A'),
                    target_date.strftime('%Y-%m-%d')
                ])

        # Make sure to close the file to flush the buffer
        temp_file.close()
        
        return temp_file.name

    except Exception as e:
        app.logger.error(f"Error generating orders spreadsheet: {str(e)}")
        if temp_file:
            try:
                temp_file.close()
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            except Exception as cleanup_error:
                app.logger.error(f"Error cleaning up temporary file: {str(cleanup_error)}")
        return None

def generate_shipping_labels(date=None):
    """
    Generate premium black and white 4x6 inch PDF shipping labels with data visualization.
    Only generates labels for active orders (non-skipped meals and active subscriptions).
    
    Args:
        date (datetime.date, optional): The date to generate labels for. Defaults to today.
        
    Returns:
        BytesIO: PDF file as bytes for direct label printer printing
    """
    if not date:
        date = datetime.now().date()
    
    # Get orders (already filtered for non-skipped meals and active subscriptions)
    orders = get_daily_orders(date)
    
    if not orders:
        return None
    
    # Sort orders by postal code for more efficient delivery
    orders.sort(key=lambda x: x.get('delivery_postal_code', ''))
    
    # Create PDF object - 4x6 inch = 101.6mm x 152.4mm (landscape orientation)
    pdf = FPDF(orientation='L', unit='mm', format=(101.6, 152.4))
    pdf.set_auto_page_break(auto=False)
    
    # Set default text color to black
    pdf.set_text_color(0, 0, 0)
    
    # Generate a shipping label for each active order
    for order in orders:
        # Skip if meal is marked as skipped or subscription is inactive
        if order.get('is_skipped', False) or order.get('subscription_status', '') != 'ACTIVE':
            continue
            
        # Add a new page for each label
        pdf.add_page()
        
        # Set margins and dimensions
        margin = 3
        label_width = 152.4 - (margin * 2)
        label_height = 101.6 - (margin * 2)
        
        # Main border around entire label - thick and black
        pdf.set_line_width(1.5)
        pdf.set_draw_color(0, 0, 0)
        pdf.rect(margin, margin, label_width, label_height)
        
        # Header section with company name and date
        pdf.set_xy(margin + 2, margin + 2)
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(0, 0, 0)  # Pure black
        pdf.cell(label_width - 4, 8, 'HEALTHYRIZZ', 0, 1, 'L')
        
        # Delivery date
        pdf.set_xy(margin + 2, margin + 10)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(0, 0, 0)  # Pure black
        pdf.cell(label_width - 4, 5, f"DELIVERY DATE: {date.strftime('%B %d, %Y')}", 0, 1, 'L')
        
        # Generate unique delivery ID
        user_id = order.get('user_id', 'N/A')
        delivery_id = f"FS-{user_id}-{date.strftime('%Y%m%d')}"
        
        # Delivery ID section with barcode
        pdf.set_line_width(0.5)
        pdf.set_draw_color(0, 0, 0)
        pdf.rect(margin + 2, margin + 17, label_width - 4, 15)
        
        pdf.set_xy(margin + 3, margin + 19)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(0, 0, 0)  # Pure black
        pdf.cell(label_width - 6, 6, f"DELIVERY ID: {delivery_id}", 0, 1, 'L')
        
        # Add barcode
        try:
            from barcode import Code128
            from barcode.writer import ImageWriter
            import io
            
            barcode = Code128(delivery_id, writer=ImageWriter())
            barcode_buffer = io.BytesIO()
            barcode.write(barcode_buffer)
            barcode_buffer.seek(0)
            
            pdf.image(barcode_buffer, x=margin + 3, y=margin + 25, w=label_width - 6, h=5)
        except:
            pdf.set_xy(margin + 3, margin + 25)
            pdf.set_font('Arial', '', 8)
            pdf.set_text_color(0, 0, 0)  # Pure black
            pdf.cell(label_width - 6, 4, "Barcode not available", 0, 1, 'L')
        
        # Customer information section
        customer_section_y = margin + 35
        customer_section_height = 30
        
        # Customer section border
        pdf.set_line_width(0.5)
        pdf.rect(margin + 2, customer_section_y, label_width - 4, customer_section_height)
        
        # Customer details
        pdf.set_xy(margin + 3, customer_section_y + 2)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(0, 0, 0)  # Pure black
        pdf.cell(label_width - 6, 6, "CUSTOMER DETAILS:", 0, 1, 'L')
        
        # Customer name
        pdf.set_xy(margin + 3, customer_section_y + 8)
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(0, 0, 0)  # Pure black
        customer_name = order.get('user_name', 'N/A')
        pdf.cell(label_width - 6, 7, customer_name, 0, 1, 'L')
        
        # Address
        pdf.set_xy(margin + 3, customer_section_y + 15)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(0, 0, 0)  # Pure black
        address = order.get('delivery_address', 'N/A')
        pdf.multi_cell(label_width - 6, 5, address)
        
        # City, State, Postal
        pdf.set_xy(margin + 3, pdf.get_y())
        pdf.set_text_color(0, 0, 0)  # Pure black
        city_state = f"{order.get('delivery_city', 'N/A')}, {order.get('delivery_state', 'N/A')} {order.get('delivery_postal_code', 'N/A')}"
        pdf.cell(label_width - 6, 5, city_state, 0, 1, 'L')
        
        # Order details section
        order_section_y = customer_section_y + customer_section_height + 2
        order_section_height = 25
        
        # Order section border
        pdf.set_line_width(0.5)
        pdf.rect(margin + 2, order_section_y, label_width - 4, order_section_height)
        
        # Order details
        pdf.set_xy(margin + 3, order_section_y + 2)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(0, 0, 0)  # Pure black
        pdf.cell(label_width - 6, 6, "ORDER DETAILS:", 0, 1, 'L')
        
        # Meal plan and type
        pdf.set_xy(margin + 3, order_section_y + 8)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(0, 0, 0)  # Pure black
        meal_plan = f"Plan: {order.get('meal_plan_name', 'N/A')}"
        pdf.cell((label_width - 8) / 2, 5, meal_plan, 0, 0, 'L')
        
        meal_type = 'Vegetarian' if order.get('is_vegetarian', False) else 'Non-Vegetarian'
        pdf.set_xy(margin + 3 + (label_width - 8) / 2, order_section_y + 8)
        pdf.set_text_color(0, 0, 0)  # Pure black
        meal_type_text = f"Type: {meal_type}"
        pdf.cell((label_width - 8) / 2, 5, meal_type_text, 0, 1, 'L')
        
        # Special instructions
        if order.get('notes'):
            pdf.set_xy(margin + 3, order_section_y + 13)
            pdf.set_font('Arial', 'B', 9)
            pdf.set_text_color(0, 0, 0)  # Pure black
            instructions = f"Instructions: {order.get('notes')}"
            pdf.multi_cell(label_width - 6, 4, instructions)
        
        # Footer with company info
        pdf.set_xy(margin + 2, label_height + margin - 5)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(0, 0, 0)  # Pure black
        pdf.cell(label_width - 4, 3, 'HealthyRizz - Fresh, Healthy, Delivered Daily | Contact: info@healthyrizz.in', 0, 1, 'C')
    
    # Save to buffer
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    
    return buffer

def generate_simple_labels(date=None):
    """
    Generate professional 4x6 inch simple labels with enhanced visibility
    Optimized for fast printing with essential information clearly displayed
    """
    if not date:
        date = datetime.now().date()
    
    # Get orders
    orders = get_daily_orders(date)
    
    if not orders:
        return None
    
    # Sort by postal code
    orders.sort(key=lambda x: x.get('delivery_postal_code', ''))
    
    # Create PDF with professional design
    pdf = FPDF(orientation='L', unit='mm', format=(101.6, 152.4))
    pdf.set_auto_page_break(auto=False)
    
    for order in orders:
        pdf.add_page()
        
        # Set margins and dimensions
        margin = 5
        label_width = 152.4 - (margin * 2)
        label_height = 101.6 - (margin * 2)
        
        # Main border around entire label
        pdf.set_line_width(2.0)
        pdf.set_draw_color(0, 0, 0)
        pdf.rect(margin, margin, label_width, label_height)
        
        # Header with company name
        pdf.set_fill_color(52, 152, 219)  # Blue background
        pdf.rect(margin + 2, margin + 2, label_width - 4, 15, 'F')
        
        pdf.set_xy(margin + 3, margin + 4)
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(label_width - 6, 11, 'HEALTHYRIZZ DELIVERY', 0, 1, 'C')
        
        # Customer name - very large and prominent
        pdf.set_xy(margin + 5, margin + 22)
        pdf.set_font('Arial', 'B', 24)
        pdf.set_text_color(0, 0, 0)
        customer_name = order.get('user_name', 'N/A')
        if len(customer_name) > 15:
            customer_name = customer_name[:15] + '...'
        pdf.cell(label_width - 10, 12, customer_name, 0, 1, 'C')
        
        # VEG/NON-VEG indicator - very prominent with thick border
        veg_y = margin + 38
        veg_height = 18
        
        if order.get('is_vegetarian', False):
            # Bright green for vegetarian
            pdf.set_fill_color(46, 204, 113)
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(2.0)
            pdf.rect(margin + 10, veg_y, label_width - 20, veg_height, 'FD')
            
            pdf.set_xy(margin + 10, veg_y + 2)
            pdf.set_font('Arial', 'B', 20)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(label_width - 20, veg_height - 4, 'VEGETARIAN', 0, 1, 'C')
        else:
            # Bright red for non-vegetarian
            pdf.set_fill_color(231, 76, 60)
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(2.0)
            pdf.rect(margin + 10, veg_y, label_width - 20, veg_height, 'FD')
            
            pdf.set_xy(margin + 10, veg_y + 2)
            pdf.set_font('Arial', 'B', 20)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(label_width - 20, veg_height - 4, 'NON-VEGETARIAN', 0, 1, 'C')
        
        # Address section with background
        pdf.set_fill_color(245, 245, 245)
        pdf.rect(margin + 5, margin + 62, label_width - 10, 20, 'F')
        
        # Address - clear and readable
        pdf.set_xy(margin + 7, margin + 64)
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(0, 0, 0)
        address = order.get('delivery_address', 'N/A')
        if len(address) > 25:
            address = address[:25] + '...'
        pdf.cell(label_width - 14, 6, address, 0, 1, 'C')
        
        # City and postal code
        pdf.set_xy(margin + 7, margin + 71)
        pdf.set_font('Arial', 'B', 12)
        city_postal = f"{order.get('delivery_city', 'N/A')}, {order.get('delivery_postal_code', 'N/A')}"
        if len(city_postal) > 30:
            city_postal = city_postal[:30] + '...'
        pdf.cell(label_width - 14, 6, city_postal, 0, 1, 'C')
        
        # Delivery date - prominent
        pdf.set_xy(margin + 7, margin + 78)
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(label_width - 14, 4, date.strftime('%A, %B %d, %Y'), 0, 1, 'C')
        
        # Order number at bottom with border
        pdf.set_line_width(1.0)
        pdf.set_draw_color(150, 150, 150)
        pdf.line(margin + 10, margin + 86, margin + label_width - 10, margin + 86)
        
        pdf.set_xy(margin + 5, margin + 88)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(label_width - 10, 6, f"Order #{order.get('subscription_id', 'N/A')}", 0, 1, 'C')
    
    # Return PDF
    pdf_bytes = BytesIO()
    pdf_bytes.write(pdf.output(dest='S').encode('latin1'))
    pdf_bytes.seek(0)
    return pdf_bytes

def email_daily_orders_report(date=None, recipient_email=None):
    """
    Generate and email the daily orders report
    
    Args:
        date (datetime.date, optional): The date to generate the report for. Defaults to today.
        recipient_email (str, optional): Email to send the report to. Defaults to admin email.
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not date:
        date = datetime.now().date()
        
    if not recipient_email:
        # Default to admin email from config
        recipient_email = os.environ.get('ADMIN_EMAIL', 'admin@healthyrizz.in')
    
    # Generate the spreadsheet
    spreadsheet_path = generate_orders_spreadsheet(date)
    if not spreadsheet_path:
        app.logger.error("Failed to generate orders spreadsheet")
        return False
    
    # Generate shipping labels
    labels_pdf = generate_shipping_labels(date)
    if not labels_pdf:
        app.logger.error("Failed to generate shipping labels PDF")
        os.unlink(spreadsheet_path)  # Remove temp CSV file
        return False
    
    # Get orders for email body
    orders = get_daily_orders(date)
    skipped = get_skipped_deliveries(date)
    
    # Create email subject and body
    subject = f"Fit Smart Daily Orders Report - {date.strftime('%A, %B %d, %Y')}"
    
    # Create HTML email body
    html_content = f"""
    <html>
    <head>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Fit Smart Daily Orders Report</h1>
        <h2>{date.strftime('%A, %B %d, %Y')}</h2>
        
        <h3>Summary</h3>
        <p><strong>Total Orders:</strong> {len(orders)}</p>
        <p><strong>Total Skipped Deliveries:</strong> {len(skipped)}</p>
        
        <h3>Orders by Meal Plan</h3>
        <table>
            <tr>
                <th>Meal Plan</th>
                <th>Count</th>
            </tr>
    """
    
    # Count meals by type
    meal_counts = {}
    for order in orders:
        meal_key = f"{order['meal_plan_name']} ({'Veg' if order['is_vegetarian'] else 'Non-Veg'}, {'w/Breakfast' if order['with_breakfast'] else 'No Breakfast'})"
        meal_counts[meal_key] = meal_counts.get(meal_key, 0) + 1
    
    for meal, count in meal_counts.items():
        html_content += f"""
            <tr>
                <td>{meal}</td>
                <td>{count}</td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <h3>Orders by Location</h3>
        <table>
            <tr>
                <th>Location</th>
                <th>Count</th>
            </tr>
    """
    
    # Count by location
    location_counts = {}
    for order in orders:
        location_key = f"{order['delivery_city']}, {order['delivery_state']}"
        location_counts[location_key] = location_counts.get(location_key, 0) + 1
    
    for location, count in location_counts.items():
        html_content += f"""
            <tr>
                <td>{location}</td>
                <td>{count}</td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <p>Please see the attached CSV file for complete order details and the PDF file for printable shipping labels.</p>
        
        <p>Thank you,<br>
        Fit Smart Order System</p>
    </body>
    </html>
    """
    
    # Send email
    try:
        attachments = [
            {"filename": f"orders_{date.strftime('%Y-%m-%d')}.csv", "path": spreadsheet_path},
            {"filename": f"shipping_labels_{date.strftime('%Y-%m-%d')}.pdf", "content": labels_pdf.getvalue()}
        ]
        
        success = send_email(
            to_email=recipient_email,
            from_email="orders@healthyrizz.in",
            subject=subject,
            html_content=html_content,
            attachments=attachments
        )
        
        # Clean up temporary file
        os.unlink(spreadsheet_path)
        
        return success
    except Exception as e:
        app.logger.error(f"Error sending daily orders email: {str(e)}")
        # Clean up temporary file
        os.unlink(spreadsheet_path)
        return False

def create_test_subscriptions():
    """Create test subscriptions for daily orders testing."""
    from datetime import datetime, timedelta
    from database.models import db, Subscription, User, MealPlan, DeliveryStatus
    
    # Create test users if they don't exist
    test_users = [
        {
            'email': 'test1@example.com',
            'name': 'Test User 1',
            'phone': '1234567890',
            'address': '123 Test St',
            'city': 'Toronto',
            'province': 'ON',
            'postal_code': 'M5V 2T6'
        },
        {
            'email': 'test2@example.com',
            'name': 'Test User 2',
            'phone': '2345678901',
            'address': '456 Test Ave',
            'city': 'Vancouver',
            'province': 'BC',
            'postal_code': 'V6B 1A1'
        },
        {
            'email': 'test3@example.com',
            'name': 'Test User 3',
            'phone': '3456789012',
            'address': '789 Test Rd',
            'city': 'Montreal',
            'province': 'QC',
            'postal_code': 'H2Y 1C6'
        }
    ]
    
    users = []
    for user_data in test_users:
        user = User.query.filter_by(email=user_data['email']).first()
        if not user:
            user = User(
                email=user_data['email'],
                name=user_data['name'],
                phone=user_data['phone'],
                address=user_data['address'],
                city=user_data['city'],
                province=user_data['province'],
                postal_code=user_data['postal_code']
            )
            db.session.add(user)
            users.append(user)
        else:
            users.append(user)
    
    # Create test meal plans if they don't exist
    meal_plans = [
        {
            'name': 'Standard Plan',
            'description': 'Our most popular plan with balanced nutrition for everyday health and wellness.',
            'calories': '1800-2200',
            'protein': '120-140g',
            'fat': '60-70g',
            'carbs': '180-220g',
            'price_weekly': 149.99,
            'price_monthly': 529.99,
            'is_vegetarian': False,
            'includes_breakfast': False
        },
        {
            'name': 'Vegetarian Plan',
            'description': 'A plant-based meal plan rich in nutrients and flavors for vegetarians.',
            'calories': '1600-2000',
            'protein': '80-100g',
            'fat': '50-60g',
            'carbs': '200-250g',
            'price_weekly': 159.99,
            'price_monthly': 559.99,
            'is_vegetarian': True,
            'includes_breakfast': True
        },
        {
            'name': 'Premium Plan',
            'description': 'Our premium plan with high-quality ingredients and gourmet recipes.',
            'calories': '2000-2400',
            'protein': '140-160g',
            'fat': '70-80g',
            'carbs': '200-250g',
            'price_weekly': 179.99,
            'price_monthly': 629.99,
            'is_vegetarian': False,
            'includes_breakfast': True
        }
    ]
    
    plans = []
    for plan_data in meal_plans:
        plan = MealPlan.query.filter_by(name=plan_data['name']).first()
        if not plan:
            plan = MealPlan(**plan_data)
            db.session.add(plan)
            plans.append(plan)
        else:
            plans.append(plan)
    
    # Create test subscriptions
    today = datetime.now().date()
    delivery_dates = [today + timedelta(days=i) for i in range(7)]
    
    for user in users:
        for plan in plans:
            subscription = Subscription(
                user_id=user.id,
                meal_plan_id=plan.id,
                status='active',
                frequency=SubscriptionFrequency.WEEKLY,
                price=plan.price_weekly,
                start_date=today,
                end_date=today + timedelta(days=30),
                delivery_days='0,2,4',  # Monday, Wednesday, Friday as comma-separated string
                created_at=datetime.now()
            )
            db.session.add(subscription)
            
            # Create deliveries for the next 7 days
            for delivery_date in delivery_dates:
                if delivery_date.weekday() in [0, 2, 4]:  # Monday, Wednesday, Friday
                    delivery = Delivery(
                        subscription_id=subscription.id,
                        user_id=user.id,
                        delivery_date=delivery_date,
                        status=DeliveryStatus.PENDING,
                        created_at=datetime.now()
                    )
                    db.session.add(delivery)
    
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating test subscriptions: {str(e)}")
        return False

def create_sample_orders(date=None):
    """
    Create sample orders for testing shipping label generation
    
    Args:
        date (datetime.date, optional): The date to create sample orders for. Defaults to today.
        
    Returns:
        list: List of sample order dictionaries
    """
    if not date:
        date = datetime.now().date()
        
    sample_orders = [
        # Original test orders
        {
            'id': 1001,
            'user_id': '1001',
            'user_name': 'John Smith',
            'delivery_address': '123 Main Street, Apartment 4B',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400001',
            'meal_plan_name': 'Premium Weight Loss Plan',
            'is_vegetarian': False,
            'notes': 'Please deliver before 9 AM',
            'subscription_id': 'SUB-1001',
            'delivery_status': 'PENDING',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1001,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1002,
            'user_id': '1002',
            'user_name': 'Priya Patel',
            'delivery_address': '456 Park Avenue, Flat 302',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400002',
            'meal_plan_name': 'Vegetarian Fitness Plan',
            'is_vegetarian': True,
            'notes': 'Leave at security desk',
            'subscription_id': 'SUB-1002',
            'delivery_status': 'PREPARING',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1002,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1003,
            'user_id': '1003',
            'user_name': 'Rajesh Kumar',
            'delivery_address': '789 Lake View Road, House 15',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400003',
            'meal_plan_name': 'Muscle Gain Plan',
            'is_vegetarian': False,
            'notes': 'Ring doorbell twice',
            'subscription_id': 'SUB-1003',
            'delivery_status': 'PACKED',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1003,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1004,
            'user_id': '1004',
            'user_name': 'Ananya Sharma',
            'delivery_address': '321 Garden Street, Villa 7',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400004',
            'meal_plan_name': 'Balanced Nutrition Plan',
            'is_vegetarian': True,
            'notes': 'Call before delivery',
            'subscription_id': 'SUB-1004',
            'delivery_status': 'OUT_FOR_DELIVERY',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1004,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1005,
            'user_id': '1005',
            'user_name': 'Vikram Singh',
            'delivery_address': '654 Hill Road, Apartment 12C',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400005',
            'meal_plan_name': 'Weight Management Plan',
            'is_vegetarian': False,
            'notes': 'Leave with neighbor if not home',
            'subscription_id': 'SUB-1005',
            'delivery_status': 'DELIVERED',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1005,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1006,
            'user_id': '1006',
            'user_name': 'Meera Patel',
            'delivery_address': '987 Ocean Drive, Suite 5',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400006',
            'meal_plan_name': 'Weight Loss Plan',
            'is_vegetarian': True,
            'notes': 'Leave with doorman',
            'subscription_id': 'SUB-1006',
            'delivery_status': 'DELAYED',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1006,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1007,
            'user_id': '1007',
            'user_name': 'Rahul Verma',
            'delivery_address': '111 Tech Park, Unit 8',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400007',
            'meal_plan_name': 'Fitness Pro Plan',
            'is_vegetarian': False,
            'notes': 'Deliver to reception',
            'subscription_id': 'SUB-1007',
            'delivery_status': 'PENDING',
            'is_skipped': True,
            'subscription_status': 'ACTIVE',
            'delivery_id': None,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        # Additional test orders
        {
            'id': 1008,
            'user_id': '1008',
            'user_name': 'Sneha Gupta',
            'delivery_address': '222 Business Park, Office 15',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400008',
            'meal_plan_name': 'Corporate Wellness Plan',
            'is_vegetarian': True,
            'notes': 'Deliver to office reception',
            'subscription_id': 'SUB-1008',
            'delivery_status': 'PENDING',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1008,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1009,
            'user_id': '1009',
            'user_name': 'Arjun Reddy',
            'delivery_address': '333 Sports Complex, Room 45',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400009',
            'meal_plan_name': 'Athlete Performance Plan',
            'is_vegetarian': False,
            'notes': 'Leave with security guard',
            'subscription_id': 'SUB-1009',
            'delivery_status': 'PREPARING',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1009,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1010,
            'user_id': '1010',
            'user_name': 'Pooja Shah',
            'delivery_address': '444 Medical Center, Suite 12',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400010',
            'meal_plan_name': 'Health Recovery Plan',
            'is_vegetarian': True,
            'notes': 'Deliver to nurse station',
            'subscription_id': 'SUB-1010',
            'delivery_status': 'PACKED',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1010,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1011,
            'user_id': '1011',
            'user_name': 'Karan Malhotra',
            'delivery_address': '555 University Campus, Hostel Block A',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400011',
            'meal_plan_name': 'Student Fitness Plan',
            'is_vegetarian': False,
            'notes': 'Leave at hostel reception',
            'subscription_id': 'SUB-1011',
            'delivery_status': 'OUT_FOR_DELIVERY',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1011,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1012,
            'user_id': '1012',
            'user_name': 'Neha Kapoor',
            'delivery_address': '666 Fitness Center, Locker 23',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400012',
            'meal_plan_name': 'Gym Enthusiast Plan',
            'is_vegetarian': True,
            'notes': 'Leave with front desk',
            'subscription_id': 'SUB-1012',
            'delivery_status': 'DELIVERED',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1012,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1013,
            'user_id': '1013',
            'user_name': 'Vivek Sharma',
            'delivery_address': '777 IT Park, Building C',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400013',
            'meal_plan_name': 'Tech Professional Plan',
            'is_vegetarian': False,
            'notes': 'Deliver to security desk',
            'subscription_id': 'SUB-1013',
            'delivery_status': 'DELAYED',
            'is_skipped': False,
            'subscription_status': 'ACTIVE',
            'delivery_id': 1013,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 1014,
            'user_id': '1014',
            'user_name': 'Divya Patel',
            'delivery_address': '888 Shopping Mall, Store 34',
            'delivery_city': 'Mumbai',
            'delivery_state': 'Maharashtra',
            'delivery_postal_code': '400014',
            'meal_plan_name': 'Retail Worker Plan',
            'is_vegetarian': True,
            'notes': 'Leave with store manager',
            'subscription_id': 'SUB-1014',
            'delivery_status': 'PENDING',
            'is_skipped': True,
            'subscription_status': 'ACTIVE',
            'delivery_id': None,
            'created_at': date.strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    return sample_orders

def get_order_completion_notifications():
    """
    Get order completion notifications for display
    
    Returns:
        list: List of notification dictionaries
    """
    try:
        # For now, return empty notifications
        # In production, this would query the database for actual notifications
        notifications = []
        
        # Sample notification structure (commented out):
        # notifications = [
        #     {
        #         'id': 1,
        #         'title': 'Order Completed',
        #         'message': 'Order #1001 has been delivered successfully',
        #         'type': 'success',
        #         'created_at': datetime.now(),
        #         'is_read': False
        #     }
        # ]
        
        return notifications
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting order completion notifications: {str(e)}")
        return []

def generate_barcode_labels_4x4(date=None):
    """
    Generate 4x4 inch stylish black and white labels for label printers.
    Each label contains essential information optimized for packing.
    
    Args:
        date (datetime.date, optional): The date to generate labels for. Defaults to today.
        
    Returns:
        BytesIO: PDF file as bytes optimized for 4x4 inch label printers
    """
    if not date:
        date = datetime.now().date()
    
    # Get orders for the date
    orders = get_daily_orders(date)
    
    if not orders:
        return None
    
    # Sort orders by postal code for efficient delivery
    orders.sort(key=lambda x: x.get('delivery_postal_code', ''))
    
    # Create PDF - 4x4 inch = 101.6mm x 101.6mm (square format)
    pdf = FPDF(orientation='P', unit='mm', format=(101.6, 101.6))
    pdf.set_auto_page_break(auto=False)
    
    # Set default text color to black
    pdf.set_text_color(0, 0, 0)
    
    # Generate a label for each active order
    for order in orders:
        # Skip cancelled deliveries
        if order.get('is_skipped', False):
            continue
            
        pdf.add_page()
        
        # Set margins and dimensions for 4x4 inch label
        margin = 4  # Slightly larger margins for cleaner look
        label_width = 101.6 - (margin * 2)
        label_height = 101.6 - (margin * 2)
        
        # Main border around entire label with rounded corners effect
        pdf.set_line_width(1.5)
        pdf.set_draw_color(0, 0, 0)
        pdf.rect(margin, margin, label_width, label_height)
        
        # Inner border for stylish effect
        pdf.set_line_width(0.5)
        pdf.rect(margin + 2, margin + 2, label_width - 4, label_height - 4)
        
        # Header section with company name and date
        header_height = 15
        pdf.set_fill_color(0, 0, 0)  # Black background
        pdf.rect(margin + 3, margin + 3, label_width - 6, header_height, 'F')
        
        pdf.set_xy(margin + 4, margin + 5)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(label_width - 8, 6, 'HEALTHYRIZZ', 0, 1, 'C')
        
        pdf.set_xy(margin + 4, margin + 11)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(label_width - 8, 4, f"Date: {date.strftime('%d/%m/%Y')}", 0, 1, 'C')
        
        # Customer name - prominent display
        customer_y = margin + header_height + 6
        pdf.set_xy(margin + 4, customer_y)
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(0, 0, 0)
        customer_name = order.get('user_name', 'N/A')
        if len(customer_name) > 18:
            customer_name = customer_name[:18] + '...'
        pdf.cell(label_width - 8, 8, customer_name, 0, 1, 'C')
        
        # VEG/NON-VEG indicator (smaller)
        veg_y = customer_y + 12
        veg_height = 6
        
        veg_text = 'VEG' if order.get('is_vegetarian', False) else 'NON-VEG'
        
        # Simple black border for VEG/NON-VEG
        pdf.set_line_width(0.8)
        pdf.rect(margin + 4, veg_y, label_width - 8, veg_height)
        pdf.set_xy(margin + 4, veg_y + 1)
        pdf.set_font('Arial', 'B', 8)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(label_width - 8, 4, veg_text, 0, 1, 'C')
        
        # Meal plan information
        meal_y = veg_y + veg_height + 4
        pdf.set_xy(margin + 4, meal_y)
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        meal_plan = order.get('meal_plan_name', 'N/A')
        if len(meal_plan) > 22:
            meal_plan = meal_plan[:22] + '...'
        pdf.cell(label_width - 8, 5, meal_plan, 0, 1, 'C')
        
        # Address section
        address_y = meal_y + 8
        pdf.set_xy(margin + 4, address_y)
        pdf.set_font('Arial', 'B', 9)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(label_width - 8, 4, "ADDRESS:", 0, 1, 'L')
        
        pdf.set_xy(margin + 4, address_y + 4)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(0, 0, 0)
        address = order.get('delivery_address', 'N/A')
        if address and len(str(address)) > 35:
            address = str(address)[:35] + '...'
        pdf.multi_cell(label_width - 8, 3.5, str(address))
        
        # Phone number (if available)
        phone_y = address_y + 12
        pdf.set_xy(margin + 4, phone_y)
        pdf.set_font('Arial', 'B', 9)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(label_width - 8, 4, "PHONE:", 0, 1, 'L')
        
        pdf.set_xy(margin + 4, phone_y + 4)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(0, 0, 0)
        phone = order.get('user_phone', 'N/A')
        if phone and len(str(phone)) > 20:
            phone = str(phone)[:20] + '...'
        pdf.cell(label_width - 8, 3.5, str(phone), 0, 1, 'L')
        
        # Special instructions (if any)
        if order.get('notes'):
            notes_y = phone_y + 10
            pdf.set_xy(margin + 4, notes_y)
            pdf.set_font('Arial', 'B', 8)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(label_width - 8, 3, "NOTES:", 0, 1, 'L')
            
            pdf.set_xy(margin + 4, notes_y + 3)
            pdf.set_font('Arial', '', 7)
            pdf.set_text_color(0, 0, 0)
            notes = order.get('notes')
            if notes and len(str(notes)) > 40:
                notes = str(notes)[:40] + '...'
            pdf.multi_cell(label_width - 8, 3, str(notes))
        
        # Delivery ID (small, bottom right)
        delivery_id = str(order.get('delivery_id', 'N/A'))
        pdf.set_xy(margin + 4, label_height + margin - 6)
        pdf.set_font('Arial', 'B', 7)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(label_width - 8, 3, f"ID: {delivery_id}", 0, 1, 'R')
    
    # Convert to bytes
    pdf_bytes = pdf.output(dest='S')
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    
    return buffer