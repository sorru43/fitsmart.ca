from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from database.models import db, Subscription, User, MealPlan, Payment
# Payment processing moved to main_routes.py with Stripe integration
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
            
            # Redirect to main checkout process which uses Stripe
            return jsonify({
                'success': False,
                'error': 'Please use the main checkout process',
                'redirect': url_for('main.meal_plans')
            }), 400
            
        except Exception as e:
            current_app.logger.error(f"Error in subscription: {str(e)}")
            return jsonify({'error': str(e)}), 500
            
    # GET request - show subscription page
    meal_plans = MealPlan.query.all()
    return render_template('subscription/subscribe.html', meal_plans=meal_plans)

# Payment verification is now handled by Stripe webhook in main_routes.py
# This route is deprecated - Stripe handles payment verification via webhooks 