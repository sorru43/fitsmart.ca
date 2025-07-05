#!/usr/bin/env python3
"""
Fix Profile and Admin Views for HealthyRizz
This script fixes profile page and admin panel to properly display orders and subscriptions
"""

import os

def fix_profile_route():
    """Fix profile route to properly display orders and payment history"""
    print("🔧 Fixing Profile Route...")
    
    profile_route_fix = '''
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
'''
    
    with open('profile_route_fix.py', 'w') as f:
        f.write(profile_route_fix)
    
    print("✅ Profile route fix created")

def fix_profile_template():
    """Fix profile template to properly display orders and subscriptions"""
    print("🔧 Fixing Profile Template...")
    
    profile_template = '''{% extends "base.html" %}

{% block title %}Profile - HealthyRizz{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-white mb-2">My Profile</h1>
            <p class="text-gray-400">Welcome back, {{ user.name }}!</p>
        </div>
        
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-darker p-6 rounded-lg border border-gray-800">
                <div class="text-2xl font-bold text-primary">{{ total_orders }}</div>
                <div class="text-sm text-gray-400">Total Orders</div>
            </div>
            <div class="bg-darker p-6 rounded-lg border border-gray-800">
                <div class="text-2xl font-bold text-green-500">₹{{ "%.2f"|format(total_spent) }}</div>
                <div class="text-sm text-gray-400">Total Spent</div>
            </div>
            <div class="bg-darker p-6 rounded-lg border border-gray-800">
                <div class="text-2xl font-bold text-blue-500">{{ total_subscriptions }}</div>
                <div class="text-sm text-gray-400">Subscriptions</div>
            </div>
            <div class="bg-darker p-6 rounded-lg border border-gray-800">
                <div class="text-2xl font-bold text-yellow-500">{{ active_subscriptions|length }}</div>
                <div class="text-sm text-gray-400">Active Plans</div>
            </div>
        </div>
        
        <!-- Tab Navigation -->
        <div class="mb-6">
            <nav class="flex space-x-8">
                <button onclick="showTab('overview')" id="overview-tab" class="tab-button active">
                    <i class="fas fa-chart-pie mr-2"></i>Overview
                </button>
                <button onclick="showTab('orders')" id="orders-tab" class="tab-button">
                    <i class="fas fa-shopping-cart mr-2"></i>Orders ({{ orders|length }})
                </button>
                <button onclick="showTab('subscriptions')" id="subscriptions-tab" class="tab-button">
                    <i class="fas fa-repeat mr-2"></i>Subscriptions ({{ total_subscriptions }})
                </button>
                <button onclick="showTab('payments')" id="payments-tab" class="tab-button">
                    <i class="fas fa-credit-card mr-2"></i>Payments ({{ payment_history|length }})
                </button>
            </nav>
        </div>
        
        <!-- Tab Content -->
        
        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="grid md:grid-cols-2 gap-6">
                <!-- Recent Orders -->
                <div class="bg-darker p-6 rounded-lg border border-gray-800">
                    <h3 class="text-lg font-semibold text-white mb-4">Recent Orders</h3>
                    {% if orders %}
                        <div class="space-y-3">
                            {% for order in orders[:5] %}
                            <div class="flex justify-between items-center py-2 border-b border-gray-700">
                                <div>
                                    <div class="text-white font-semibold">#{{ order.id }}</div>
                                    <div class="text-sm text-gray-400">{{ order.meal_plan_name }}</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-primary font-semibold">₹{{ "%.2f"|format(order.amount) }}</div>
                                    <div class="text-xs text-gray-400">{{ order.created_at.strftime('%d %b %Y') }}</div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        <div class="mt-4">
                            <button onclick="showTab('orders')" class="text-primary hover:text-green-600 text-sm">
                                View all orders →
                            </button>
                        </div>
                    {% else %}
                        <p class="text-gray-400">No orders yet</p>
                        <a href="{{ url_for('main.meal_plans') }}" class="text-primary hover:text-green-600 text-sm">
                            Browse meal plans →
                        </a>
                    {% endif %}
                </div>
                
                <!-- Active Subscriptions -->
                <div class="bg-darker p-6 rounded-lg border border-gray-800">
                    <h3 class="text-lg font-semibold text-white mb-4">Active Subscriptions</h3>
                    {% if active_subscriptions %}
                        <div class="space-y-3">
                            {% for subscription in active_subscriptions %}
                            <div class="border border-gray-700 rounded-lg p-3">
                                <div class="text-white font-semibold">{{ subscription.meal_plan.name if subscription.meal_plan else 'Unknown Plan' }}</div>
                                <div class="text-sm text-gray-400">{{ subscription.frequency.value.title() }} - ₹{{ "%.2f"|format(subscription.price) }}</div>
                                <div class="text-xs text-green-500 mt-1">{{ subscription.status.value.title() }}</div>
                            </div>
                            {% endfor %}
                        </div>
                        <div class="mt-4">
                            <button onclick="showTab('subscriptions')" class="text-primary hover:text-green-600 text-sm">
                                Manage subscriptions →
                            </button>
                        </div>
                    {% else %}
                        <p class="text-gray-400">No active subscriptions</p>
                        <a href="{{ url_for('main.meal_plans') }}" class="text-primary hover:text-green-600 text-sm">
                            Subscribe to a plan →
                        </a>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <!-- Orders Tab -->
        <div id="orders" class="tab-content">
            <div class="bg-darker rounded-lg border border-gray-800">
                <div class="p-6 border-b border-gray-700">
                    <h3 class="text-lg font-semibold text-white">Order History</h3>
                </div>
                
                {% if orders %}
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead class="bg-gray-900">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Order ID</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Meal Plan</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Amount</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Date</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-700">
                            {% for order in orders %}
                            <tr>
                                <td class="px-6 py-4 text-sm text-white font-mono">#{{ order.id }}</td>
                                <td class="px-6 py-4 text-sm text-white">{{ order.meal_plan_name }}</td>
                                <td class="px-6 py-4 text-sm text-primary font-semibold">₹{{ "%.2f"|format(order.amount) }}</td>
                                <td class="px-6 py-4">
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full 
                                        {% if order.status == 'confirmed' %}bg-green-100 text-green-800{% else %}bg-gray-100 text-gray-800{% endif %}">
                                        {{ order.status.title() }}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-sm text-gray-400">{{ order.created_at.strftime('%d %b %Y, %I:%M %p') }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="p-6 text-center">
                    <p class="text-gray-400">No orders found</p>
                    <a href="{{ url_for('main.meal_plans') }}" class="text-primary hover:text-green-600 text-sm">
                        Browse meal plans →
                    </a>
                </div>
                {% endif %}
            </div>
        </div>
        
        <!-- Subscriptions Tab -->
        <div id="subscriptions" class="tab-content">
            <div class="space-y-6">
                {% if active_subscriptions %}
                <div class="bg-darker rounded-lg border border-gray-800">
                    <div class="p-6 border-b border-gray-700">
                        <h3 class="text-lg font-semibold text-white">Active Subscriptions</h3>
                    </div>
                    <div class="p-6">
                        <div class="grid gap-4">
                            {% for subscription in active_subscriptions %}
                            <div class="border border-gray-700 rounded-lg p-4">
                                <div class="flex justify-between items-start">
                                    <div>
                                        <h4 class="text-white font-semibold">{{ subscription.meal_plan.name if subscription.meal_plan else 'Unknown Plan' }}</h4>
                                        <p class="text-gray-400 text-sm">{{ subscription.frequency.value.title() }} Subscription</p>
                                        <p class="text-primary font-semibold">₹{{ "%.2f"|format(subscription.price) }}</p>
                                    </div>
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                        {{ subscription.status.value.title() }}
                                    </span>
                                </div>
                                <div class="mt-3 text-sm text-gray-400">
                                    <p>Started: {{ subscription.start_date.strftime('%d %b %Y') }}</p>
                                    <p>Next billing: {{ subscription.current_period_end.strftime('%d %b %Y') }}</p>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if paused_subscriptions or canceled_subscriptions %}
                <div class="bg-darker rounded-lg border border-gray-800">
                    <div class="p-6 border-b border-gray-700">
                        <h3 class="text-lg font-semibold text-white">Inactive Subscriptions</h3>
                    </div>
                    <div class="p-6">
                        <div class="grid gap-4">
                            {% for subscription in paused_subscriptions + canceled_subscriptions %}
                            <div class="border border-gray-700 rounded-lg p-4 opacity-75">
                                <div class="flex justify-between items-start">
                                    <div>
                                        <h4 class="text-white font-semibold">{{ subscription.meal_plan.name if subscription.meal_plan else 'Unknown Plan' }}</h4>
                                        <p class="text-gray-400 text-sm">{{ subscription.frequency.value.title() }} Subscription</p>
                                    </div>
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full 
                                        {% if subscription.status.value == 'paused' %}bg-yellow-100 text-yellow-800{% else %}bg-red-100 text-red-800{% endif %}">
                                        {{ subscription.status.value.title() }}
                                    </span>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                {% if not active_subscriptions and not paused_subscriptions and not canceled_subscriptions %}
                <div class="bg-darker rounded-lg border border-gray-800 p-6 text-center">
                    <p class="text-gray-400">No subscriptions found</p>
                    <a href="{{ url_for('main.meal_plans') }}" class="text-primary hover:text-green-600 text-sm">
                        Subscribe to a meal plan →
                    </a>
                </div>
                {% endif %}
            </div>
        </div>
        
        <!-- Payments Tab -->
        <div id="payments" class="tab-content">
            <div class="bg-darker rounded-lg border border-gray-800">
                <div class="p-6 border-b border-gray-700">
                    <h3 class="text-lg font-semibold text-white">Payment History</h3>
                </div>
                
                {% if payment_history %}
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead class="bg-gray-900">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Payment ID</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Order</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Amount</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Date</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-700">
                            {% for payment in payment_history %}
                            <tr>
                                <td class="px-6 py-4 text-sm text-white font-mono">{{ payment.payment_id[:15] }}...</td>
                                <td class="px-6 py-4 text-sm text-white">#{{ payment.order_id }}</td>
                                <td class="px-6 py-4 text-sm text-primary font-semibold">₹{{ "%.2f"|format(payment.amount) }}</td>
                                <td class="px-6 py-4">
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full 
                                        {% if payment.status == 'captured' %}bg-green-100 text-green-800{% else %}bg-gray-100 text-gray-800{% endif %}">
                                        {{ payment.status.title() }}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-sm text-gray-400">{{ payment.date.strftime('%d %b %Y, %I:%M %p') }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="p-6 text-center">
                    <p class="text-gray-400">No payment history found</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<style>
.tab-button {
    @apply px-4 py-2 text-gray-400 hover:text-white border-b-2 border-transparent hover:border-primary transition-colors;
}

.tab-button.active {
    @apply text-white border-primary;
}

.tab-content {
    @apply hidden;
}

.tab-content.active {
    @apply block;
}
</style>

<script>
function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show the selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to the selected tab button
    document.getElementById(tabName + '-tab').classList.add('active');
}
</script>
{% endblock %}
'''
    
    with open('templates/profile_fixed.html', 'w') as f:
        f.write(profile_template)
    
    print("✅ Fixed profile template created")

def fix_admin_orders_route():
    """Fix admin orders route to properly display orders and subscriptions"""
    print("🔧 Fixing Admin Orders Route...")
    
    admin_fix = '''
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
'''
    
    with open('admin_routes_fix.py', 'w') as f:
        f.write(admin_fix)
    
    print("✅ Fixed admin routes created")

def main():
    """Main function to run all profile and admin fixes"""
    print("🔧 HealthyRizz Profile and Admin Views Fix")
    print("=" * 60)
    
    # Run all fixes
    fix_profile_route()
    fix_profile_template()
    fix_admin_orders_route()
    
    print("\n🎉 Profile and Admin Views Fix Completed!")
    print("=" * 60)
    print("Files created:")
    print("1. profile_route_fix.py - Fixed profile route")
    print("2. templates/profile_fixed.html - Fixed profile template")
    print("3. admin_routes_fix.py - Fixed admin routes")
    print("\nNext steps:")
    print("1. Update your routes with the fixed profile logic")
    print("2. Replace your profile template with the fixed one")
    print("3. Update your admin routes")
    print("4. Test profile and admin functionality")

if __name__ == "__main__":
    main() 