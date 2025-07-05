
@main_bp.route('/subscribe/<int:plan_id>')
def subscribe(plan_id):
    """Subscribe to a meal plan with proper total calculation and location dropdown"""
    try:
        # Get meal plan
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
        # Get frequency from query params (default to weekly)
        frequency = request.args.get('frequency', 'weekly')
        
        # Calculate prices properly
        if frequency == 'weekly':
            base_price = float(meal_plan.price_weekly)
        else:
            base_price = float(meal_plan.price_monthly)
        
        # Calculate GST (5%)
        gst_amount = base_price * 0.05
        total_amount = base_price + gst_amount
        
        # Get all active delivery locations for dropdown
        delivery_locations = DeliveryLocation.query.filter_by(is_active=True).order_by(DeliveryLocation.city).all()
        
        # Get user data if logged in
        user_data = None
        if current_user.is_authenticated:
            user_data = {
                'name': current_user.name,
                'email': current_user.email,
                'phone': current_user.phone,
                'address': current_user.address,
                'city': current_user.city,
                'state': current_user.state,
                'postal_code': current_user.postal_code
            }
        
        return render_template('checkout.html',
                             meal_plan=meal_plan,
                             frequency=frequency,
                             base_price=base_price,
                             gst_amount=gst_amount,
                             total_amount=total_amount,
                             delivery_locations=delivery_locations,
                             user_data=user_data)
                             
    except Exception as e:
        current_app.logger.error(f"Error in subscribe route: {str(e)}")
        flash('An error occurred while loading the subscription page.', 'error')
        return redirect(url_for('main.meal_plans'))
