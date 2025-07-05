
# Fixed Admin Orders Routes

@admin_orders_bp.route('/orders')
@login_required
@admin_required
def orders_dashboard():
    """Admin orders dashboard with proper order display"""
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        date_filter = request.args.get('date', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Build query
        query = Order.query.join(User).join(MealPlan)
        
        # Apply filters
        if status_filter != 'all':
            query = query.filter(Order.status == status_filter)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter(db.func.date(Order.created_at) == filter_date)
            except ValueError:
                pass
        
        # Get paginated results
        orders = query.order_by(desc(Order.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics
        total_orders = Order.query.count()
        confirmed_orders = Order.query.filter_by(status='confirmed').count()
        pending_orders = Order.query.filter_by(status='pending').count()
        total_revenue = db.session.query(db.func.sum(Order.amount)).filter_by(payment_status='captured').scalar() or 0
        
        stats = {
            'total_orders': total_orders,
            'confirmed_orders': confirmed_orders,
            'pending_orders': pending_orders,
            'total_revenue': float(total_revenue),
            'today_orders': Order.query.filter(db.func.date(Order.created_at) == datetime.now().date()).count()
        }
        
        return render_template('admin/orders_dashboard.html',
                             orders=orders,
                             stats=stats,
                             status_filter=status_filter,
                             date_filter=date_filter,
                             today=datetime.now().date())
                             
    except Exception as e:
        current_app.logger.error(f"Error in admin orders dashboard: {str(e)}")
        # Return empty data on error
        from collections import namedtuple
        EmptyPagination = namedtuple('Pagination', ['items', 'page', 'pages', 'per_page', 'total', 'has_prev', 'has_next'])
        empty_orders = EmptyPagination([], 1, 1, 20, 0, False, False)
        
        return render_template('admin/orders_dashboard.html',
                             orders=empty_orders,
                             stats={'total_orders': 0, 'confirmed_orders': 0, 'pending_orders': 0, 'total_revenue': 0, 'today_orders': 0},
                             status_filter='all',
                             date_filter='',
                             today=datetime.now().date())

@admin_orders_bp.route('/subscriptions')
@login_required
@admin_required
def subscriptions_dashboard():
    """Admin subscriptions dashboard"""
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        frequency_filter = request.args.get('frequency', 'all')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Build query
        query = Subscription.query.join(User).join(MealPlan)
        
        # Apply filters
        if status_filter != 'all':
            query = query.filter(Subscription.status == status_filter)
        
        if frequency_filter != 'all':
            query = query.filter(Subscription.frequency == frequency_filter)
        
        # Get paginated results
        subscriptions = query.order_by(desc(Subscription.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics
        total_subscriptions = Subscription.query.count()
        active_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).count()
        paused_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.PAUSED).count()
        canceled_subscriptions = Subscription.query.filter_by(status=SubscriptionStatus.CANCELED).count()
        
        stats = {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'paused_subscriptions': paused_subscriptions,
            'canceled_subscriptions': canceled_subscriptions
        }
        
        return render_template('admin/subscriptions_dashboard.html',
                             subscriptions=subscriptions,
                             stats=stats,
                             status_filter=status_filter,
                             frequency_filter=frequency_filter)
                             
    except Exception as e:
        current_app.logger.error(f"Error in admin subscriptions dashboard: {str(e)}")
        # Return empty data on error
        from collections import namedtuple
        EmptyPagination = namedtuple('Pagination', ['items', 'page', 'pages', 'per_page', 'total', 'has_prev', 'has_next'])
        empty_subs = EmptyPagination([], 1, 1, 20, 0, False, False)
        
        return render_template('admin/subscriptions_dashboard.html',
                             subscriptions=empty_subs,
                             stats={'total_subscriptions': 0, 'active_subscriptions': 0, 'paused_subscriptions': 0, 'canceled_subscriptions': 0},
                             status_filter='all',
                             frequency_filter='all')
