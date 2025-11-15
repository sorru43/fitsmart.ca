from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, send_file
from flask_login import login_required
from functools import wraps
from datetime import datetime
import csv
from io import StringIO
from database.models import db, DeliveryStatus, Subscription, Delivery, SkippedDelivery, User, MealPlan, SubscriptionStatus
from utils.email_functions import send_delivery_status_update_email

enhanced_orders_bp = Blueprint('enhanced_orders', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@enhanced_orders_bp.route('/daily-orders')
@login_required
@admin_required
def admin_daily_orders():
    """Enhanced daily orders management with meal-specific filtering"""
    
    # Get today's date or selected date from query parameters
    date_str = request.args.get('date')
    meal_filter = request.args.get('meal_type', 'all')  # breakfast, lunch, dinner, all
    status_filter = request.args.get('status', 'all')  # pending, preparing, packed, etc.
    
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()
    
    try:
        # Get active subscriptions for the selected date
        active_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).all()
        
        daily_orders = []
        skipped_orders = []
        
        for subscription in active_subscriptions:
            # Check if this subscription should have delivery on the selected date
            if subscription.is_delivery_day(selected_date):
                # Check if delivery is skipped
                skipped_delivery = SkippedDelivery.query.filter_by(
                    subscription_id=subscription.id,
                    delivery_date=selected_date
                ).first()
                
                if skipped_delivery:
                    # Add to skipped orders
                    skipped_order = {
                        'subscription_id': subscription.id,
                        'user_name': subscription.user.name,
                        'user_email': subscription.user.email,
                        'user_phone': subscription.user.phone,
                        'meal_plan_name': subscription.meal_plan.name,
                        'delivery_address': subscription.delivery_address,
                        'delivery_city': subscription.delivery_city,
                        'delivery_province': subscription.delivery_province,
                        'delivery_postal_code': subscription.delivery_postal_code,
                        'is_vegetarian': (subscription.vegetarian_days and selected_date.weekday() in [int(d) for d in subscription.vegetarian_days.split(',') if d]),
                        'includes_breakfast': subscription.meal_plan.includes_breakfast,
                        'includes_lunch': subscription.meal_plan.includes_lunch,
                        'includes_dinner': subscription.meal_plan.includes_dinner,
                        'includes_snacks': subscription.meal_plan.includes_snacks,
                        'skip_reason': getattr(skipped_delivery, 'reason', 'user_request'),
                        'skip_date': skipped_delivery.created_at,
                        'type': 'skipped'
                    }
                    skipped_orders.append(skipped_order)
                else:
                    # Get or create delivery record
                    delivery = Delivery.query.filter_by(
                        subscription_id=subscription.id,
                        delivery_date=selected_date
                    ).first()
                    
                    if not delivery:
                        delivery = Delivery(
                            subscription_id=subscription.id,
                            user_id=subscription.user_id,
                            delivery_date=selected_date,
                            status=DeliveryStatus.PENDING
                        )
                        db.session.add(delivery)
                        db.session.commit()
                    
                    # Apply meal type filter
                    if meal_filter != 'all':
                        if meal_filter == 'breakfast' and not subscription.meal_plan.includes_breakfast:
                            continue
                        elif meal_filter == 'lunch' and not subscription.meal_plan.includes_lunch:
                            continue
                        elif meal_filter == 'dinner' and not subscription.meal_plan.includes_dinner:
                            continue
                    
                    # Apply status filter
                    if status_filter != 'all' and delivery.status.value != status_filter:
                        continue
                    
                    # Add to daily orders
                    order = {
                        'delivery_id': delivery.id,
                        'subscription_id': subscription.id,
                        'user_name': subscription.user.name,
                        'user_email': subscription.user.email,
                        'user_phone': subscription.user.phone,
                        'meal_plan_name': subscription.meal_plan.name,
                        'delivery_address': subscription.delivery_address,
                        'delivery_city': subscription.delivery_city,
                        'delivery_province': subscription.delivery_province,
                        'delivery_postal_code': subscription.delivery_postal_code,
                        'is_vegetarian': (subscription.vegetarian_days and selected_date.weekday() in [int(d) for d in subscription.vegetarian_days.split(',') if d]),
                        'includes_breakfast': subscription.meal_plan.includes_breakfast,
                        'includes_lunch': subscription.meal_plan.includes_lunch,
                        'includes_dinner': subscription.meal_plan.includes_dinner,
                        'includes_snacks': subscription.meal_plan.includes_snacks,
                        'delivery_status': delivery.status.value,
                        'tracking_number': delivery.tracking_number,
                        'notes': delivery.notes,
                        'status_updated_at': delivery.status_updated_at,
                        'created_at': delivery.created_at,
                        'type': 'delivery'
                    }
                    daily_orders.append(order)
        
        # Sort orders by user name
        daily_orders.sort(key=lambda x: x['user_name'])
        skipped_orders.sort(key=lambda x: x['user_name'])
        
        # Calculate statistics
        stats = {
            'total_orders': len(daily_orders),
            'total_skipped': len(skipped_orders),
            'pending': len([o for o in daily_orders if o['delivery_status'] == 'pending']),
            'preparing': len([o for o in daily_orders if o['delivery_status'] == 'preparing']),
            'packed': len([o for o in daily_orders if o['delivery_status'] == 'packed']),
            'out_for_delivery': len([o for o in daily_orders if o['delivery_status'] == 'out_for_delivery']),
            'delivered': len([o for o in daily_orders if o['delivery_status'] == 'delivered']),
            'delayed': len([o for o in daily_orders if o['delivery_status'] == 'delayed']),
            'breakfast_orders': len([o for o in daily_orders if o['includes_breakfast']]),
            'lunch_orders': len([o for o in daily_orders if o['includes_lunch']]),
            'dinner_orders': len([o for o in daily_orders if o['includes_dinner']]),
            'vegetarian_orders': len([o for o in daily_orders if o['is_vegetarian']])
        }
        
        # Get all delivery statuses for dropdown
        delivery_statuses = [status.value for status in DeliveryStatus]
        
        return render_template('admin/enhanced_daily_orders.html',
                              selected_date=selected_date,
                              daily_orders=daily_orders,
                              skipped_orders=skipped_orders,
                              stats=stats,
                              meal_filter=meal_filter,
                              status_filter=status_filter,
                              delivery_statuses=delivery_statuses)
                              
    except Exception as e:
        current_app.logger.error(f"Error loading daily orders: {str(e)}")
        flash('Error loading daily orders', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@enhanced_orders_bp.route('/daily-orders/update-status', methods=['POST'])
@login_required
@admin_required
def admin_update_daily_order_status():
    """Update delivery status with customer notification"""
    try:
        delivery_id = request.form.get('delivery_id')
        new_status = request.form.get('status')
        notes = request.form.get('notes', '')
        notify_customer = request.form.get('notify_customer', 'false') == 'true'
        
        if not delivery_id or not new_status:
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        delivery = Delivery.query.get_or_404(delivery_id)
        
        # Update delivery status
        old_status = delivery.status.value
        delivery.status = DeliveryStatus(new_status)
        delivery.status_updated_at = datetime.now()
        
        if notes:
            delivery.notes = notes if delivery.notes is None else f"{delivery.notes}\n{notes} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        
        # Add tracking number if status is out_for_delivery or delivered
        if new_status in ['out_for_delivery', 'delivered'] and not delivery.tracking_number:
            delivery.tracking_number = f"TRK{delivery.id:06d}"
        
        db.session.commit()
        
        # Send notification to customer if requested
        if notify_customer:
            try:
                send_delivery_status_update_email(delivery, old_status, new_status)
            except Exception as e:
                current_app.logger.error(f"Failed to send delivery notification: {str(e)}")
        
        return jsonify({
            'success': True, 
            'message': f'Delivery status updated to {new_status.title()} successfully',
            'tracking_number': delivery.tracking_number
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating delivery status: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating delivery status'})

@enhanced_orders_bp.route('/daily-orders/bulk-update', methods=['POST'])
@login_required
@admin_required
def admin_bulk_update_daily_orders():
    """Bulk update delivery statuses"""
    try:
        delivery_ids = request.form.getlist('delivery_ids[]')
        new_status = request.form.get('status')
        meal_type = request.form.get('meal_type', 'all')  # breakfast, lunch, dinner, all
        notify_customers = request.form.get('notify_customers', 'false') == 'true'
        
        if not delivery_ids or not new_status:
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        updated_count = 0
        failed_count = 0
        
        for delivery_id in delivery_ids:
            try:
                delivery = Delivery.query.get(delivery_id)
                if not delivery:
                    failed_count += 1
                    continue
                
                # Check meal type filter
                if meal_type != 'all':
                    subscription = delivery.subscription
                    if meal_type == 'breakfast' and not subscription.meal_plan.includes_breakfast:
                        continue
                    elif meal_type == 'lunch' and not subscription.meal_plan.includes_lunch:
                        continue
                    elif meal_type == 'dinner' and not subscription.meal_plan.includes_dinner:
                        continue
                
                # Update status
                old_status = delivery.status.value
                delivery.status = DeliveryStatus(new_status)
                delivery.status_updated_at = datetime.now()
                
                # Add tracking number if needed
                if new_status in ['out_for_delivery', 'delivered'] and not delivery.tracking_number:
                    delivery.tracking_number = f"TRK{delivery.id:06d}"
                
                updated_count += 1
                
                # Send notification if requested
                if notify_customers:
                    try:
                        send_delivery_status_update_email(delivery, old_status, new_status)
                    except Exception as e:
                        current_app.logger.error(f"Failed to send notification for delivery {delivery_id}: {str(e)}")
                
            except Exception as e:
                current_app.logger.error(f"Error updating delivery {delivery_id}: {str(e)}")
                failed_count += 1
        
        db.session.commit()
        
        message = f'Successfully updated {updated_count} deliveries to {new_status.title()}'
        if failed_count > 0:
            message += f'. {failed_count} updates failed.'
        
        return jsonify({
            'success': True,
            'message': message,
            'updated_count': updated_count,
            'failed_count': failed_count
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk update: {str(e)}")
        return jsonify({'success': False, 'message': 'Error performing bulk update'})

@enhanced_orders_bp.route('/daily-orders/meal-specific-update', methods=['POST'])
@login_required
@admin_required
def admin_meal_specific_update():
    """Update status for specific meal types only"""
    try:
        delivery_ids = request.form.getlist('delivery_ids[]')
        new_status = request.form.get('status')
        meal_type = request.form.get('meal_type')  # breakfast, lunch, dinner
        notify_customers = request.form.get('notify_customers', 'false') == 'true'
        
        if not delivery_ids or not new_status or not meal_type:
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        updated_count = 0
        failed_count = 0
        
        for delivery_id in delivery_ids:
            try:
                delivery = Delivery.query.get(delivery_id)
                if not delivery:
                    failed_count += 1
                    continue
                
                # Check if this delivery includes the specified meal type
                subscription = delivery.subscription
                includes_meal = False
                
                if meal_type == 'breakfast' and subscription.meal_plan.includes_breakfast:
                    includes_meal = True
                elif meal_type == 'lunch' and subscription.meal_plan.includes_lunch:
                    includes_meal = True
                elif meal_type == 'dinner' and subscription.meal_plan.includes_dinner:
                    includes_meal = True
                
                if not includes_meal:
                    continue  # Skip this delivery as it doesn't include the specified meal
                
                # Update status
                old_status = delivery.status.value
                delivery.status = DeliveryStatus(new_status)
                delivery.status_updated_at = datetime.now()
                
                # Add tracking number if needed
                if new_status in ['out_for_delivery', 'delivered'] and not delivery.tracking_number:
                    delivery.tracking_number = f"TRK{delivery.id:06d}"
                
                updated_count += 1
                
                # Send notification if requested
                if notify_customers:
                    try:
                        send_delivery_status_update_email(delivery, old_status, new_status, meal_type)
                    except Exception as e:
                        current_app.logger.error(f"Failed to send notification for delivery {delivery_id}: {str(e)}")
                
            except Exception as e:
                current_app.logger.error(f"Error updating delivery {delivery_id}: {str(e)}")
                failed_count += 1
        
        db.session.commit()
        
        message = f'Successfully updated {updated_count} {meal_type} deliveries to {new_status.title()}'
        if failed_count > 0:
            message += f'. {failed_count} updates failed.'
        
        return jsonify({
            'success': True,
            'message': message,
            'updated_count': updated_count,
            'failed_count': failed_count
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in meal-specific update: {str(e)}")
        return jsonify({'success': False, 'message': 'Error performing meal-specific update'})

@enhanced_orders_bp.route('/daily-orders/export', methods=['POST'])
@login_required
@admin_required
def admin_export_daily_orders():
    """Export daily orders to CSV"""
    try:
        date_str = request.form.get('date')
        meal_filter = request.form.get('meal_type', 'all')
        status_filter = request.form.get('status', 'all')
        
        if date_str:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            selected_date = datetime.now().date()
        
        # Get the same data as the main view
        active_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).all()
        
        csv_data = StringIO()
        writer = csv.writer(csv_data)
        
        # Write header
        writer.writerow([
            'Customer Name', 'Email', 'Phone', 'Meal Plan', 'Address', 'City', 'Province', 
            'Postal Code', 'Vegetarian', 'Breakfast', 'Lunch', 'Dinner', 'Snacks',
            'Delivery Status', 'Tracking Number', 'Notes', 'Status Updated At'
        ])
        
        for subscription in active_subscriptions:
            if subscription.is_delivery_day(selected_date):
                # Check if skipped
                skipped_delivery = SkippedDelivery.query.filter_by(
                    subscription_id=subscription.id,
                    delivery_date=selected_date
                ).first()
                
                if not skipped_delivery:
                    delivery = Delivery.query.filter_by(
                        subscription_id=subscription.id,
                        delivery_date=selected_date
                    ).first()
                    
                    if delivery:
                        # Apply filters
                        if meal_filter != 'all':
                            if meal_filter == 'breakfast' and not subscription.meal_plan.includes_breakfast:
                                continue
                            elif meal_filter == 'lunch' and not subscription.meal_plan.includes_lunch:
                                continue
                            elif meal_filter == 'dinner' and not subscription.meal_plan.includes_dinner:
                                continue
                        
                        if status_filter != 'all' and delivery.status.value != status_filter:
                            continue
                        
                        # Write row
                        writer.writerow([
                            subscription.user.name,
                            subscription.user.email,
                            subscription.user.phone,
                            subscription.meal_plan.name,
                            subscription.delivery_address,
                            subscription.delivery_city,
                            subscription.delivery_province,
                            subscription.delivery_postal_code,
                            'Yes' if (subscription.vegetarian_days and selected_date.weekday() in [int(d) for d in subscription.vegetarian_days.split(',') if d]) else 'No',
                            'Yes' if subscription.meal_plan.includes_breakfast else 'No',
                            'Yes' if subscription.meal_plan.includes_lunch else 'No',
                            'Yes' if subscription.meal_plan.includes_dinner else 'No',
                            'Yes' if subscription.meal_plan.includes_snacks else 'No',
                            delivery.status.value.title(),
                            delivery.tracking_number or '',
                            delivery.notes or '',
                            delivery.status_updated_at.strftime('%Y-%m-%d %H:%M:%S') if delivery.status_updated_at else ''
                        ])
        
        csv_data.seek(0)
        
        return send_file(
            StringIO(csv_data.getvalue()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'daily_orders_{selected_date.strftime("%Y-%m-%d")}.csv'
        )
        
    except Exception as e:
        current_app.logger.error(f"Error exporting daily orders: {str(e)}")
        flash('Error exporting daily orders', 'error')
        return redirect(url_for('enhanced_orders.admin_daily_orders'))
