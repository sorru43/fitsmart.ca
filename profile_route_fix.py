
@main_bp.route('/profile')
@login_required
def profile():
    """Enhanced user profile page with complete order and payment history"""
    try:
        current_app.logger.info(f"Profile accessed by user: {current_user.email}")
        
        # Get user's orders (all orders)
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        
        # Get user's subscriptions
        subscriptions = Subscription.query.filter_by(user_id=current_user.id).order_by(Subscription.created_at.desc()).all()
        
        # Group subscriptions by status
        active_subscriptions = [s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE]
        paused_subscriptions = [s for s in subscriptions if s.status == SubscriptionStatus.PAUSED]
        canceled_subscriptions = [s for s in subscriptions if s.status == SubscriptionStatus.CANCELED]
        
        # Prepare order data with meal plan information
        order_history = []
        for order in orders:
            try:
                meal_plan = MealPlan.query.get(order.meal_plan_id)
                meal_plan_name = meal_plan.name if meal_plan else 'Unknown Plan'
                
                order_data = {
                    'id': order.id,
                    'amount': order.amount,
                    'status': order.status,
                    'payment_status': order.payment_status,
                    'payment_id': order.payment_id,
                    'created_at': order.created_at,
                    'meal_plan_name': meal_plan_name,
                    'delivery_address': getattr(order, 'delivery_address', None)
                }
                order_history.append(order_data)
            except Exception as e:
                current_app.logger.error(f"Error processing order {order.id}: {str(e)}")
        
        # Calculate statistics
        total_spent = sum(order.amount for order in orders if order.payment_status == 'captured')
        total_orders = len(orders)
        total_subscriptions = len(subscriptions)
        
        # Prepare payment history
        payment_history = []
        for order in orders:
            if order.payment_id and order.payment_status:
                payment_history.append({
                    'order_id': order.id,
                    'payment_id': order.payment_id,
                    'amount': order.amount,
                    'status': order.payment_status,
                    'date': order.created_at,
                    'meal_plan_name': next((od['meal_plan_name'] for od in order_history if od['id'] == order.id), 'N/A')
                })
        
        current_app.logger.info(f"Profile data loaded: {total_orders} orders, {total_subscriptions} subscriptions")
        
        return render_template('profile.html',
                             user=current_user,
                             orders=order_history,
                             active_subscriptions=active_subscriptions,
                             paused_subscriptions=paused_subscriptions,
                             canceled_subscriptions=canceled_subscriptions,
                             payment_history=payment_history,
                             total_spent=total_spent,
                             total_orders=total_orders,
                             total_subscriptions=total_subscriptions,
                             now=datetime.now())
                             
    except Exception as e:
        current_app.logger.error(f"Error in profile route: {str(e)}")
        # Return safe fallback
        return render_template('profile.html',
                             user=current_user,
                             orders=[],
                             active_subscriptions=[],
                             paused_subscriptions=[],
                             canceled_subscriptions=[],
                             payment_history=[],
                             total_spent=0,
                             total_orders=0,
                             total_subscriptions=0,
                             now=datetime.now())
