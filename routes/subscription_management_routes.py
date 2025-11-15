#!/usr/bin/env python3
"""
Enhanced subscription management routes for skip meal functionality with proper timing logic
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from database.models import Subscription, SkippedDelivery, SubscriptionStatus, Holiday, db, MealPlan, Delivery
from datetime import datetime, date, timedelta, time
from flask_wtf.csrf import validate_csrf
from enum import Enum

subscription_mgmt_bp = Blueprint('subscription_mgmt', __name__)

class MealType(Enum):
    """Enum for meal types"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    ALL_DAY = "all_day"

def get_cutoff_time_for_meal(meal_type, delivery_date):
    """
    Calculate cutoff time for skipping meals based on meal type and delivery date
    Rule: Must skip 1 day before delivery day with specific times based on meal type
    """
    # Base rule: 1 day before delivery
    cutoff_date = delivery_date - timedelta(days=1)
    
    # Set cutoff time based on meal type
    if meal_type == MealType.BREAKFAST:
        cutoff_time = time(19, 0)  # 7:00 PM
    elif meal_type == MealType.LUNCH:
        cutoff_time = time(19, 0)  # 7:00 PM
    elif meal_type == MealType.DINNER:
        cutoff_time = time(19, 0)  # 7:00 PM
    else:
        cutoff_time = time(19, 0)  # 7:00 PM (strictest for all-day plans)
    
    return datetime.combine(cutoff_date, cutoff_time)

def determine_meal_type_from_plan(meal_plan):
    """
    Determine meal type from meal plan configuration
    """
    includes_breakfast = getattr(meal_plan, 'includes_breakfast', True)
    includes_lunch = getattr(meal_plan, 'includes_lunch', False)
    includes_dinner = getattr(meal_plan, 'includes_dinner', False)
    
    # Determine meal type based on what's included
    if includes_breakfast and includes_lunch and includes_dinner:
        return MealType.ALL_DAY
    elif includes_breakfast and not includes_lunch and not includes_dinner:
        return MealType.BREAKFAST
    elif not includes_breakfast and includes_lunch and not includes_dinner:
        return MealType.LUNCH
    elif not includes_breakfast and not includes_lunch and includes_dinner:
        return MealType.DINNER
    else:
        return MealType.ALL_DAY  # Default

def can_skip_delivery(subscription, delivery_date):
    """
    Enhanced function to check if a delivery can be skipped based on timing rules
    """
    now = datetime.now()
    
    # Convert string date to date object if needed
    if isinstance(delivery_date, str):
        delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
    
    # Check if there's an active holiday that protects meals
    current_holiday = Holiday.get_current_holiday()
    if current_holiday and current_holiday.protect_meals:
        # If it's a holiday with meal protection, meals cannot be skipped
        return False, None, None
    
    # Determine meal type from subscription
    meal_type = determine_meal_type_from_plan(subscription.meal_plan)
    
    # Calculate cutoff time
    cutoff_datetime = get_cutoff_time_for_meal(meal_type, delivery_date)
    
    # Check if we're before the cutoff
    can_skip = now <= cutoff_datetime
    
    # Additional check: can't skip past deliveries
    if delivery_date < now.date():
        can_skip = False
    
    return can_skip, cutoff_datetime, meal_type

def calculate_skip_compensation(subscription, skipped_delivery_date):
    """
    Calculate compensation for skipped delivery using MealTracker
    """
    from utils.meal_tracking import MealTracker
    return MealTracker.handle_skip_compensation(subscription, skipped_delivery_date)

@subscription_mgmt_bp.route('/skip_delivery/<int:subscription_id>', methods=['POST'])
@login_required
def skip_delivery(subscription_id):
    """Enhanced skip delivery with proper timing validation"""
    try:
        # Get subscription and verify ownership
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            flash('You can only manage your own subscriptions.', 'error')
            return redirect(url_for('main.profile'))
        
        # Get delivery date from form
        delivery_date_str = request.form.get('delivery_date')
        if not delivery_date_str:
            flash('Delivery date is required.', 'error')
            return redirect(url_for('main.profile'))
        
        # Convert to date object
        try:
            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid delivery date format.', 'error')
            return redirect(url_for('main.profile'))
        
        # Check if delivery can be skipped with enhanced logic
        can_skip, cutoff_datetime, meal_type = can_skip_delivery(subscription, delivery_date)
        
        if not can_skip:
            # Provide specific error message based on timing
            now = datetime.now()
            if delivery_date < now.date():
                flash('Cannot skip past deliveries.', 'error')
            else:
                cutoff_str = cutoff_datetime.strftime('%B %d at %I:%M %p')
                flash(f'Cannot skip this {meal_type.value} delivery. Cutoff time was {cutoff_str}.', 'error')
            return redirect(url_for('main.profile'))
        
        # Check if delivery is already skipped
        existing_skip = SkippedDelivery.query.filter_by(
            subscription_id=subscription_id,
            delivery_date=delivery_date
        ).first()
        
        if existing_skip:
            flash('This delivery is already skipped.', 'warning')
            return redirect(url_for('main.profile'))
        
        # Calculate compensation
        compensation = calculate_skip_compensation(subscription, delivery_date)
        
        # Create skipped delivery record
        skipped = SkippedDelivery(
            subscription_id=subscription_id,
            delivery_date=delivery_date
        )
        
        # Add enhanced fields if they exist
        if hasattr(skipped, 'reason'):
            skipped.reason = 'user_request'
        if hasattr(skipped, 'meal_type'):
            skipped.meal_type = meal_type.value
        if hasattr(skipped, 'compensation_applied'):
            skipped.compensation_applied = True
        if hasattr(skipped, 'compensation_details'):
            skipped.compensation_details = compensation['description']
        
        db.session.add(skipped)
        
        # Apply compensation
        if compensation['days_extended'] > 0:
            if subscription.current_period_end:
                subscription.current_period_end += timedelta(days=compensation['days_extended'])
            else:
                # Set end date based on frequency
                if subscription.frequency.value == 'weekly':
                    subscription.current_period_end = datetime.now() + timedelta(days=7 + compensation['days_extended'])
                else:
                    subscription.current_period_end = datetime.now() + timedelta(days=30 + compensation['days_extended'])
        
        db.session.commit()
        
        # Success message
        flash(f'✅ {meal_type.value.title()} delivery for {delivery_date.strftime("%B %d")} has been skipped. {compensation["description"]}', 'success')
        current_app.logger.info(f"User {current_user.email} skipped {meal_type.value} delivery for {delivery_date}")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error skipping delivery: {str(e)}")
        flash('An error occurred while skipping the delivery.', 'error')
    
    return redirect(url_for('main.profile') + '#subscriptions')

@subscription_mgmt_bp.route('/unskip_delivery/<int:subscription_id>', methods=['POST'])
@login_required
def unskip_delivery(subscription_id):
    """Enhanced unskip delivery with proper timing validation"""
    try:
        # Get subscription and verify ownership
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            flash('You can only manage your own subscriptions.', 'error')
            return redirect(url_for('main.profile'))
        
        # Get delivery date from form
        delivery_date_str = request.form.get('delivery_date')
        if not delivery_date_str:
            flash('Delivery date is required.', 'error')
            return redirect(url_for('main.profile'))
        
        # Convert to date object
        try:
            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid delivery date format.', 'error')
            return redirect(url_for('main.profile'))
        
        # Check if delivery can be unskipped
        can_unskip, cutoff_datetime, meal_type = can_skip_delivery(subscription, delivery_date)
        
        if not can_unskip:
            # Provide specific error message
            now = datetime.now()
            if delivery_date < now.date():
                flash('Cannot restore past deliveries.', 'error')
            else:
                cutoff_str = cutoff_datetime.strftime('%B %d at %I:%M %p')
                flash(f'Cannot restore this {meal_type.value} delivery. Cutoff time was {cutoff_str}.', 'error')
            return redirect(url_for('main.profile'))
        
        # Find and delete the skipped delivery record
        skipped = SkippedDelivery.query.filter_by(
            subscription_id=subscription_id,
            delivery_date=delivery_date
        ).first()
        
        if not skipped:
            flash('This delivery was not skipped.', 'warning')
            return redirect(url_for('main.profile'))
        
        # Get compensation details before deleting
        compensation_applied = getattr(skipped, 'compensation_applied', False)
        
        # Remove the skip record
        db.session.delete(skipped)
        
        # Reverse compensation if it was applied
        if compensation_applied:
            compensation = calculate_skip_compensation(subscription, delivery_date)
            if compensation['days_extended'] > 0 and subscription.current_period_end:
                subscription.current_period_end -= timedelta(days=compensation['days_extended'])
        
        db.session.commit()
        
        # Success message
        flash(f'✅ {meal_type.value.title()} delivery for {delivery_date.strftime("%B %d")} has been restored.', 'success')
        current_app.logger.info(f"User {current_user.email} restored {meal_type.value} delivery for {delivery_date}")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error restoring delivery: {str(e)}")
        flash('An error occurred while restoring the delivery.', 'error')
    
    return redirect(url_for('main.profile') + '#subscriptions')

@subscription_mgmt_bp.route('/pause_subscription/<int:subscription_id>', methods=['POST'])
@login_required
def pause_subscription(subscription_id):
    """Pause a subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            flash('You can only manage your own subscriptions.', 'error')
            return redirect(url_for('main.profile'))
        
        if subscription.pause():
            db.session.commit()
            flash(f'Your {subscription.meal_plan.name} subscription has been paused.', 'success')
        else:
            flash('This subscription cannot be paused.', 'error')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error pausing subscription: {str(e)}")
        flash('An error occurred while pausing the subscription.', 'error')
    
    return redirect(url_for('main.profile') + '#subscriptions')

@subscription_mgmt_bp.route('/resume_subscription/<int:subscription_id>', methods=['POST'])
@login_required
def resume_subscription(subscription_id):
    """Resume a paused subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            flash('You can only manage your own subscriptions.', 'error')
            return redirect(url_for('main.profile'))
        
        if subscription.resume():
            subscription.current_period_start = datetime.now()
            if subscription.frequency.value == 'weekly':
                subscription.current_period_end = datetime.now() + timedelta(days=7)
            else:
                subscription.current_period_end = datetime.now() + timedelta(days=30)
            
            db.session.commit()
            flash(f'Your {subscription.meal_plan.name} subscription has been resumed.', 'success')
        else:
            flash('This subscription cannot be resumed.', 'error')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error resuming subscription: {str(e)}")
        flash('An error occurred while resuming the subscription.', 'error')
    
    return redirect(url_for('main.profile') + '#subscriptions')

@subscription_mgmt_bp.route('/cancel_subscription/<int:subscription_id>', methods=['POST'])
@login_required
def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            flash('You can only manage your own subscriptions.', 'error')
            return redirect(url_for('main.profile'))
        
        if subscription.cancel():
            subscription.end_date = datetime.now()
            db.session.commit()
            flash(f'Your {subscription.meal_plan.name} subscription has been cancelled.', 'info')
        else:
            flash('This subscription cannot be cancelled.', 'error')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cancelling subscription: {str(e)}")
        flash('An error occurred while cancelling the subscription.', 'error')
    
    return redirect(url_for('main.profile') + '#subscriptions')

@subscription_mgmt_bp.route('/get_upcoming_deliveries/<int:subscription_id>')
@login_required
def get_upcoming_deliveries(subscription_id):
    """Get upcoming deliveries for a subscription with enhanced skip information"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        upcoming = subscription.get_upcoming_deliveries(days=14)
        
        enhanced_deliveries = []
        for delivery in upcoming:
            delivery_date = delivery['date']
            can_skip, cutoff_datetime, meal_type = can_skip_delivery(subscription, delivery_date)
            
            enhanced_delivery = {
                **delivery,
                'can_skip': can_skip,
                'meal_type': meal_type.value,
                'cutoff_datetime': cutoff_datetime.isoformat(),
                'cutoff_formatted': cutoff_datetime.strftime('%B %d at %I:%M %p'),
                'time_until_cutoff': str(cutoff_datetime - datetime.now()) if cutoff_datetime > datetime.now() else 'Expired'
            }
            enhanced_deliveries.append(enhanced_delivery)
        
        return jsonify({
            'success': True,
            'deliveries': enhanced_deliveries,
            'meal_type_info': {
                'breakfast_cutoff': '7:00 PM day before',
                'lunch_cutoff': '7:00 PM day before',
                'dinner_cutoff': '7:00 PM day before',
                'all_day_cutoff': '7:00 PM day before'
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting upcoming deliveries: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@subscription_mgmt_bp.route('/skip_history/<int:subscription_id>')
@login_required
def skip_history(subscription_id):
    """Get skip history for a subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        skipped_deliveries = SkippedDelivery.query.filter_by(
            subscription_id=subscription_id
        ).order_by(SkippedDelivery.delivery_date.desc()).all()
        
        history = []
        for skip in skipped_deliveries:
            skip_info = {
                'delivery_date': skip.delivery_date.isoformat(),
                'delivery_date_formatted': skip.delivery_date.strftime('%B %d, %Y'),
                'created_at': skip.created_at.isoformat(),
                'created_at_formatted': skip.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'reason': getattr(skip, 'reason', 'user_request'),
                'meal_type': getattr(skip, 'meal_type', 'all'),
                'compensation_applied': getattr(skip, 'compensation_applied', False),
                'compensation_details': getattr(skip, 'compensation_details', 'No compensation details')
            }
            history.append(skip_info)
        
        return jsonify({
            'success': True,
            'skip_history': history,
            'total_skipped': len(history)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting skip history: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@subscription_mgmt_bp.route('/bulk_skip_deliveries/<int:subscription_id>', methods=['POST'])
@login_required
def bulk_skip_deliveries(subscription_id):
    """Skip multiple deliveries at once with enhanced validation"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            flash('You can only manage your own subscriptions.', 'error')
            return redirect(url_for('main.profile'))
        
        # Get delivery dates from form (JSON)
        import json
        delivery_dates_str = request.form.get('delivery_dates')
        if not delivery_dates_str:
            flash('No delivery dates provided.', 'error')
            return redirect(url_for('main.profile'))
        
        try:
            delivery_dates = json.loads(delivery_dates_str)
        except json.JSONDecodeError:
            flash('Invalid delivery dates format.', 'error')
            return redirect(url_for('main.profile'))
        
        # Skip each delivery with enhanced validation
        skipped_count = 0
        failed_count = 0
        failed_reasons = []
        
        for date_str in delivery_dates:
            try:
                delivery_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Check if can skip
                can_skip, cutoff_datetime, meal_type = can_skip_delivery(subscription, delivery_date)
                
                if can_skip:
                    # Check if already skipped
                    existing_skip = SkippedDelivery.query.filter_by(
                        subscription_id=subscription_id,
                        delivery_date=delivery_date
                    ).first()
                    
                    if not existing_skip:
                        # Calculate compensation
                        compensation = calculate_skip_compensation(subscription, delivery_date)
                        
                        # Create skip record
                        skipped = SkippedDelivery(
                            subscription_id=subscription_id,
                            delivery_date=delivery_date
                        )
                        
                        # Add enhanced fields if they exist
                        if hasattr(skipped, 'reason'):
                            skipped.reason = 'bulk_user_request'
                        if hasattr(skipped, 'meal_type'):
                            skipped.meal_type = meal_type.value
                        if hasattr(skipped, 'compensation_applied'):
                            skipped.compensation_applied = True
                        if hasattr(skipped, 'compensation_details'):
                            skipped.compensation_details = compensation['description']
                        
                        db.session.add(skipped)
                        
                        # Apply compensation
                        if compensation['days_extended'] > 0 and subscription.current_period_end:
                            subscription.current_period_end += timedelta(days=compensation['days_extended'])
                        
                        skipped_count += 1
                    else:
                        failed_count += 1
                        failed_reasons.append(f"{delivery_date.strftime('%B %d')}: Already skipped")
                else:
                    failed_count += 1
                    cutoff_str = cutoff_datetime.strftime('%B %d at %I:%M %p')
                    failed_reasons.append(f"{delivery_date.strftime('%B %d')}: Past cutoff ({cutoff_str})")
                    
            except (ValueError, Exception) as e:
                failed_count += 1
                failed_reasons.append(f"{date_str}: Invalid date or error")
        
        db.session.commit()
        
        # Provide detailed feedback
        if skipped_count > 0:
            flash(f'✅ Successfully skipped {skipped_count} deliveries.', 'success')
        if failed_count > 0:
            flash(f'⚠️ Failed to skip {failed_count} deliveries: {"; ".join(failed_reasons[:3])}', 'warning')
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error bulk skipping deliveries: {str(e)}")
        flash('An error occurred while skipping deliveries.', 'error')
    
    return redirect(url_for('main.profile') + '#subscriptions')
 
@subscription_mgmt_bp.route('/change_meal_plan/<int:subscription_id>', methods=['GET', 'POST'])
@login_required
def change_meal_plan(subscription_id):
    """Change meal plan for a subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            flash('You can only manage your own subscriptions.', 'error')
            return redirect(url_for('main.profile'))
        
        if request.method == 'GET':
            # Get all available meal plans
            meal_plans = MealPlan.query.filter_by(is_active=True).all()
            return render_template('subscription/change_meal_plan.html',
                                  subscription=subscription,
                                  meal_plans=meal_plans)
        
        # POST request - process meal plan change
        new_meal_plan_id = request.form.get('new_meal_plan_id')
        effective_date = request.form.get('effective_date', 'next_billing')
        
        if not new_meal_plan_id:
            flash('Please select a new meal plan.', 'error')
            return redirect(url_for('subscription_mgmt.change_meal_plan', subscription_id=subscription_id))
        
        new_meal_plan = MealPlan.query.get_or_404(new_meal_plan_id)
        
        # Calculate price difference
        old_price = float(subscription.price)
        if subscription.frequency.value == 'weekly':
            new_price = float(new_meal_plan.price_weekly)
        else:
            new_price = float(new_meal_plan.price_monthly)
        
        price_difference = new_price - old_price
        
        # Handle effective date
        if effective_date == 'immediate':
            # Change immediately
            subscription.meal_plan_id = new_meal_plan_id
            subscription.price = new_price
            subscription.updated_at = datetime.now()
            
            # Recalculate meal allocation
            from utils.meal_tracking import MealTracker
            meal_status = MealTracker.get_meal_status(subscription)
            if hasattr(subscription, 'total_meals_promised_this_period'):
                subscription.total_meals_promised_this_period = meal_status['promised_meals']
                subscription.meals_remaining_this_period = meal_status['remaining_meals']
            
            db.session.commit()
            flash(f'✅ Meal plan changed to {new_meal_plan.name} immediately.', 'success')
            
        else:
            # Change at next billing period
            subscription.next_meal_plan_id = new_meal_plan_id
            subscription.next_price = new_price
            subscription.meal_plan_change_date = subscription.current_period_end
            subscription.updated_at = datetime.now()
            
            db.session.commit()
            flash(f'✅ Meal plan will change to {new_meal_plan.name} at next billing period.', 'success')
        
        current_app.logger.info(f"User {current_user.email} changed meal plan for subscription {subscription_id} to {new_meal_plan.name}")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error changing meal plan: {str(e)}")
        flash('An error occurred while changing the meal plan.', 'error')
    
    return redirect(url_for('main.profile') + '#subscriptions')

@subscription_mgmt_bp.route('/compare_meal_plans/<int:subscription_id>')
@login_required
def compare_meal_plans(subscription_id):
    """Compare current meal plan with available plans"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all available meal plans
        meal_plans = MealPlan.query.filter_by(is_active=True).all()
        
        comparison_data = []
        for plan in meal_plans:
            # Calculate price difference
            current_price = float(subscription.price)
            if subscription.frequency.value == 'weekly':
                plan_price = float(plan.price_weekly)
            else:
                plan_price = float(plan.price_monthly)
            
            price_difference = plan_price - current_price
            
            comparison_data.append({
                'id': plan.id,
                'name': plan.name,
                'description': plan.description,
                'current_price': current_price,
                'plan_price': plan_price,
                'price_difference': price_difference,
                'is_current': plan.id == subscription.meal_plan_id,
                'calories': plan.calories,
                'protein': plan.protein,
                'includes_breakfast': plan.includes_breakfast,
                'includes_lunch': plan.includes_lunch,
                'includes_dinner': plan.includes_dinner,
                'includes_snacks': plan.includes_snacks,
                'dietary_tags': plan.dietary_tags
            })
        
        return jsonify({
            'success': True,
            'current_subscription': {
                'meal_plan_id': subscription.meal_plan_id,
                'frequency': subscription.frequency.value,
                'price': current_price
            },
            'comparison_data': comparison_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error comparing meal plans: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@subscription_mgmt_bp.route('/delivery_history/<int:subscription_id>')
@login_required
def delivery_history(subscription_id):
    """Get delivery history for a subscription"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get delivery history
        deliveries = Delivery.query.filter_by(
            subscription_id=subscription_id
        ).order_by(Delivery.delivery_date.desc()).all()
        
        # Get skipped deliveries
        skipped_deliveries = SkippedDelivery.query.filter_by(
            subscription_id=subscription_id
        ).order_by(SkippedDelivery.delivery_date.desc()).all()
        
        delivery_history = []
        
        # Process regular deliveries
        for delivery in deliveries:
            delivery_info = {
                'date': delivery.delivery_date.isoformat(),
                'date_formatted': delivery.delivery_date.strftime('%B %d, %Y'),
                'status': delivery.status.value,
                'type': 'delivery',
                'tracking_number': delivery.tracking_number,
                'notes': delivery.notes,
                'status_updated_at': delivery.status_updated_at.isoformat() if delivery.status_updated_at else None
            }
            delivery_history.append(delivery_info)
        
        # Process skipped deliveries
        for skipped in skipped_deliveries:
            skip_info = {
                'date': skipped.delivery_date.isoformat(),
                'date_formatted': skipped.delivery_date.strftime('%B %d, %Y'),
                'status': 'skipped',
                'type': 'skipped',
                'created_at': skipped.created_at.isoformat(),
                'reason': getattr(skipped, 'reason', 'user_request'),
                'compensation_applied': getattr(skipped, 'compensation_applied', False)
            }
            delivery_history.append(skip_info)
        
        # Sort by date (most recent first)
        delivery_history.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'delivery_history': delivery_history,
            'total_deliveries': len([d for d in delivery_history if d['type'] == 'delivery']),
            'total_skipped': len([d for d in delivery_history if d['type'] == 'skipped']),
            'subscription_info': {
                'meal_plan': subscription.meal_plan.name,
                'frequency': subscription.frequency.value,
                'start_date': subscription.start_date.isoformat()
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting delivery history: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@subscription_mgmt_bp.route('/subscription_history/<int:subscription_id>')
@login_required
def subscription_history(subscription_id):
    """Get complete subscription history"""
    try:
        subscription = Subscription.query.get_or_404(subscription_id)
        if subscription.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get subscription timeline
        timeline = []
        
        # Initial subscription
        timeline.append({
            'date': subscription.created_at.isoformat(),
            'date_formatted': subscription.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'event': 'subscription_created',
            'description': f'Started {subscription.meal_plan.name} subscription ({subscription.frequency.value})',
            'details': {
                'meal_plan': subscription.meal_plan.name,
                'frequency': subscription.frequency.value,
                'price': float(subscription.price)
            }
        })
        
        # Status changes
        if subscription.status == SubscriptionStatus.PAUSED:
            timeline.append({
                'date': subscription.updated_at.isoformat(),
                'date_formatted': subscription.updated_at.strftime('%B %d, %Y at %I:%M %p'),
                'event': 'subscription_paused',
                'description': 'Subscription paused',
                'details': {}
            })
        elif subscription.status == SubscriptionStatus.CANCELED:
            timeline.append({
                'date': subscription.updated_at.isoformat(),
                'date_formatted': subscription.updated_at.strftime('%B %d, %Y at %I:%M %p'),
                'event': 'subscription_canceled',
                'description': 'Subscription canceled',
                'details': {}
            })
        
        # Billing periods
        if subscription.current_period_start and subscription.current_period_end:
            timeline.append({
                'date': subscription.current_period_start.isoformat(),
                'date_formatted': subscription.current_period_start.strftime('%B %d, %Y'),
                'event': 'billing_period_start',
                'description': f'Billing period started ({subscription.frequency.value})',
                'details': {
                    'period_start': subscription.current_period_start.isoformat(),
                    'period_end': subscription.current_period_end.isoformat(),
                    'price': float(subscription.price)
                }
            })
        
        # Sort by date (most recent first)
        timeline.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'subscription_history': timeline,
            'subscription_info': {
                'id': subscription.id,
                'meal_plan': subscription.meal_plan.name,
                'status': subscription.status.value,
                'frequency': subscription.frequency.value,
                'created_at': subscription.created_at.isoformat(),
                'current_period_start': subscription.current_period_start.isoformat() if subscription.current_period_start else None,
                'current_period_end': subscription.current_period_end.isoformat() if subscription.current_period_end else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting subscription history: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500
 