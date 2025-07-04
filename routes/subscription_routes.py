from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from database.models import db, Subscription, User, MealPlan, Payment
from utils.payment_utils import create_order, verify_payment_signature
from datetime import datetime, timedelta
import json

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        try:
            data = request.get_json()
            meal_plan_id = data.get('meal_plan_id')
            is_vegetarian = data.get('is_vegetarian', True)
            
            # Get meal plan details
            meal_plan = MealPlan.query.get(meal_plan_id)
            if not meal_plan:
                return jsonify({'error': 'Invalid meal plan'}), 400
            
            # Calculate amount in paise (multiply by 100 for Razorpay)
            amount = int(meal_plan.price * 100)
            
            # Create Razorpay order
            order = create_order(amount)
            
            # Store order details in session
            session['order_details'] = {
                'meal_plan_id': meal_plan_id,
                'is_vegetarian': is_vegetarian,
                'razorpay_order_id': order['id'],
                'amount': amount
            }
            
            return jsonify({
                'success': True,
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key': current_app.config['RAZORPAY_KEY_ID']
            })
            
        except Exception as e:
            current_app.logger.error(f"Error in subscription: {str(e)}")
            return jsonify({'error': str(e)}), 500
            
    # GET request - show subscription page
    meal_plans = MealPlan.query.all()
    return render_template('subscription/subscribe.html', meal_plans=meal_plans)

@subscription_bp.route('/payment/verify', methods=['POST'])
def verify_payment():
    try:
        data = request.get_json()
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        
        # Verify payment signature
        if not verify_payment_signature(payment_id, order_id, signature):
            return jsonify({'error': 'Invalid payment signature'}), 400
        
        # Get order details from session
        order_details = session.get('order_details')
        if not order_details:
            return jsonify({'error': 'Order details not found'}), 400
        
        # Create subscription
        subscription = Subscription(
            user_id=session.get('user_id'),
            meal_plan_id=order_details['meal_plan_id'],
            is_vegetarian=order_details['is_vegetarian'],
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            status='active'
        )
        db.session.add(subscription)
        
        # Create payment record
        payment = Payment(
            subscription_id=subscription.id,
            amount=order_details['amount'] / 100,  # Convert back from paise
            payment_id=payment_id,
            order_id=order_id,
            status='completed',
            payment_date=datetime.now()
        )
        db.session.add(payment)
        
        db.session.commit()
        
        # Clear session
        session.pop('order_details', None)
        
        return jsonify({
            'success': True,
            'message': 'Payment successful',
            'subscription_id': subscription.id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in payment verification: {str(e)}")
        return jsonify({'error': str(e)}), 500 