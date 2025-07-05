
@main_bp.route('/process_checkout', methods=['POST'])
def process_checkout():
    """Process checkout form and create Razorpay order with location handling"""
    try:
        # Get form data
        plan_id = request.form.get('plan_id')
        frequency = request.form.get('frequency')
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        delivery_location_id = request.form.get('delivery_location_id')
        customer_address = request.form.get('customer_address')
        customer_pincode = request.form.get('customer_pincode')
        delivery_instructions = request.form.get('delivery_instructions', '')
        total_amount = request.form.get('total_amount')
        
        # Validate required fields
        if not all([plan_id, frequency, customer_name, customer_email, customer_phone, 
                   delivery_location_id, customer_address, customer_pincode, total_amount]):
            return jsonify({
                'success': False,
                'message': 'Please fill in all required fields.'
            }), 400
        
        # Get meal plan
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
        # Get delivery location
        delivery_location = DeliveryLocation.query.get_or_404(delivery_location_id)
        if not delivery_location.is_active:
            return jsonify({
                'success': False,
                'message': 'Selected delivery location is not available.'
            }), 400
        
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
                'delivery_location_id': delivery_location_id,
                'customer_city': delivery_location.city,
                'customer_state': delivery_location.province,
                'customer_address': customer_address,
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
