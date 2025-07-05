
# Fixed Payment Routes for HealthyRizz

@main_bp.route('/process_checkout', methods=['POST'])
def process_checkout():
    """Process checkout form and create Razorpay order"""
    try:
        # Get form data
        plan_id = request.form.get('plan_id')
        frequency = request.form.get('frequency')
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        customer_address = request.form.get('customer_address')
        customer_city = request.form.get('customer_city')
        customer_state = request.form.get('customer_state')
        customer_pincode = request.form.get('customer_pincode')
        delivery_instructions = request.form.get('delivery_instructions', '')
        total_amount = request.form.get('total_amount')
        
        # Validate required fields
        if not all([plan_id, frequency, customer_name, customer_email, customer_phone, 
                   customer_address, customer_city, customer_state, customer_pincode, total_amount]):
            return jsonify({
                'success': False,
                'message': 'Please fill in all required fields.'
            }), 400
        
        # Get meal plan
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
        # Convert amount to paise
        amount_paise = int(float(total_amount) * 100)
        
        # Create Razorpay order
        razorpay_client = get_razorpay_client()
        order_data = {
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': f'receipt_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'notes': {
                'plan_id': plan_id,
                'frequency': frequency,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'customer_address': customer_address,
                'customer_city': customer_city,
                'customer_state': customer_state,
                'customer_pincode': customer_pincode,
                'delivery_instructions': delivery_instructions
            }
        }
        
        razorpay_order = razorpay_client.order.create(order_data)
        
        # Store order data in session
        session['razorpay_order'] = order_data
        session['razorpay_order']['order_id'] = razorpay_order['id']
        
        return jsonify({
            'success': True,
            'key_id': current_app.config['RAZORPAY_KEY_ID'],
            'amount': amount_paise,
            'currency': 'INR',
            'order_id': razorpay_order['id'],
            'description': f'{meal_plan.name} - {frequency.title()} Plan'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in process_checkout: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing your order. Please try again.'
        }), 500

@main_bp.route('/verify_payment', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment and create order/subscription"""
    try:
        # Get payment verification data
        razorpay_payment_id = request.form.get('razorpay_payment_id')
        razorpay_order_id = request.form.get('razorpay_order_id')
        razorpay_signature = request.form.get('razorpay_signature')
        
        # Get order data from session
        order_data = session.get('razorpay_order')
        if not order_data:
            flash('Invalid order session. Please try again.', 'error')
            return redirect(url_for('main.meal_plans'))
        
        # Verify payment signature (skip for test orders)
        if not razorpay_order_id.startswith('order_test_'):
            if not verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
                flash('Payment verification failed. Please contact support.', 'error')
                return redirect(url_for('main.meal_plans'))
        
        # Get or create user
        user = User.query.filter_by(email=order_data['notes']['customer_email']).first()
        if not user:
            # Create new user
            user = User(
                name=order_data['notes']['customer_name'],
                email=order_data['notes']['customer_email'],
                phone=order_data['notes']['customer_phone'],
                address=order_data['notes']['customer_address'],
                city=order_data['notes']['customer_city'],
                state=order_data['notes']['customer_state'],
                postal_code=order_data['notes']['customer_pincode'],
                password_hash=generate_password_hash('healthyrizz123'),  # Default password
                is_active=True
            )
            db.session.add(user)
            db.session.flush()
        
        # Create Order record
        order = Order(
            user_id=user.id,
            meal_plan_id=order_data['notes']['plan_id'],
            amount=float(order_data['amount']) / 100,  # Convert from paise to rupees
            status='confirmed',
            payment_status='captured',
            payment_id=razorpay_payment_id,
            order_id=razorpay_order_id,
            delivery_address=order_data['notes']['customer_address'],
            delivery_instructions=order_data['notes']['delivery_instructions'],
            created_at=datetime.now()
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create Subscription record
        from database.models import SubscriptionFrequency, SubscriptionStatus
        frequency = SubscriptionFrequency.WEEKLY if order_data['notes']['frequency'] == 'weekly' else SubscriptionFrequency.MONTHLY
        
        subscription = Subscription(
            user_id=user.id,
            meal_plan_id=order_data['notes']['plan_id'],
            frequency=frequency,
            status=SubscriptionStatus.ACTIVE,
            price=float(order_data['amount']) / 100,
            order_id=order.id,
            delivery_address=order_data['notes']['customer_address'],
            start_date=datetime.now(),
            current_period_start=datetime.now(),
            current_period_end=(
                datetime.now() + timedelta(days=7) if frequency == SubscriptionFrequency.WEEKLY 
                else datetime.now() + timedelta(days=30)
            )
        )
        db.session.add(subscription)
        db.session.commit()
        
        # Clear session data
        session.pop('razorpay_order', None)
        
        # Log in the user if not already logged in
        if not current_user.is_authenticated:
            login_user(user)
        
        flash('Your subscription has been created successfully!', 'success')
        return redirect(url_for('main.checkout_success', order_id=order.id))
        
    except Exception as e:
        current_app.logger.error(f"Error verifying payment: {str(e)}")
        db.session.rollback()
        flash('An error occurred while processing your payment. Please contact support.', 'error')
        return redirect(url_for('main.meal_plans'))

@main_bp.route('/checkout-success')
def checkout_success():
    """Checkout success page with order details"""
    order_id = request.args.get('order_id')
    
    if not order_id:
        flash('Invalid order reference.', 'error')
        return redirect(url_for('main.meal_plans'))
    
    try:
        # Get order details
        order = Order.query.get_or_404(order_id)
        
        # Get associated subscription
        subscription = Subscription.query.filter_by(order_id=order.id).first()
        
        # Get meal plan details
        meal_plan = MealPlan.query.get(order.meal_plan_id)
        
        return render_template('checkout_success.html',
                             order=order,
                             subscription=subscription,
                             meal_plan=meal_plan)
        
    except Exception as e:
        current_app.logger.error(f"Error in checkout_success: {str(e)}")
        flash('An error occurred while loading your order details.', 'error')
        return redirect(url_for('main.meal_plans'))
