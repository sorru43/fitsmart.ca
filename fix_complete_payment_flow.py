#!/usr/bin/env python3
"""
Complete Payment Flow Fix for HealthyRizz
This script fixes all issues from checkout to payment success, database updates, and profile display
"""

import os
import sys
import secrets
from datetime import datetime

def fix_csrf_configuration():
    """Fix CSRF configuration for production"""
    print("🔧 Fixing CSRF Configuration...")
    
    # Update .env file with proper CSRF settings
    env_content = f"""# HealthyRizz Production Environment - Complete Fix
SECRET_KEY={secrets.token_hex(32)}
WTF_CSRF_SECRET_KEY={secrets.token_hex(32)}

# Environment
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=sqlite:///healthyrizz.db

# CSRF Configuration - FIXED
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=7200
WTF_CSRF_SSL_STRICT=False
WTF_CSRF_HEADERS=['X-CSRFToken', 'X-CSRF-Token']
WTF_CSRF_METHODS=['POST', 'PUT', 'PATCH', 'DELETE']
WTF_CSRF_FIELD_NAME=csrf_token

# Security Settings - FIXED
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=1800

# Payment Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=your-webhook-secret

# Domain
DOMAIN_NAME=healthyrizz.in
BASE_URL=https://healthyrizz.in
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ CSRF configuration fixed")

def fix_checkout_template():
    """Fix checkout template CSRF and form issues"""
    print("🔧 Fixing Checkout Template...")
    
    # Create a fixed checkout template
    checkout_template = '''{% extends "base.html" %}

{% block title %}Checkout - HealthyRizz{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold text-white mb-8">Complete Your Order</h1>
        
        <div class="grid md:grid-cols-2 gap-8">
            <!-- Order Form -->
            <div class="bg-darker p-6 rounded-lg border border-gray-800">
                <h2 class="text-xl font-semibold mb-6 text-white">Customer Information</h2>
                
                <form id="checkout-form" method="POST" action="{{ url_for('main.process_checkout') }}">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                    <input type="hidden" name="plan_id" value="{{ meal_plan.id }}">
                    <input type="hidden" name="frequency" value="{{ frequency }}">
                    <input type="hidden" name="total_amount" value="{{ total_amount }}">
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">Full Name *</label>
                            <input type="text" name="customer_name" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600" 
                                   value="{{ current_user.name if current_user.is_authenticated else '' }}">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">Email Address *</label>
                            <input type="email" name="customer_email" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600"
                                   value="{{ current_user.email if current_user.is_authenticated else '' }}">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">Phone Number *</label>
                            <input type="tel" name="customer_phone" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600"
                                   value="{{ current_user.phone if current_user.is_authenticated else '' }}">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">Address *</label>
                            <textarea name="customer_address" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600" rows="3">{{ current_user.address if current_user.is_authenticated else '' }}</textarea>
                        </div>
                        
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium mb-2 text-white">City *</label>
                                <input type="text" name="customer_city" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600"
                                       value="{{ current_user.city if current_user.is_authenticated else '' }}">
                            </div>
                            <div>
                                <label class="block text-sm font-medium mb-2 text-white">State *</label>
                                <input type="text" name="customer_state" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600"
                                       value="{{ current_user.state if current_user.is_authenticated else '' }}">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">PIN Code *</label>
                            <input type="text" name="customer_pincode" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600"
                                   value="{{ current_user.postal_code if current_user.is_authenticated else '' }}">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">Delivery Instructions</label>
                            <textarea name="delivery_instructions" class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600" rows="2"></textarea>
                        </div>
                    </div>
                    
                    <div class="mt-6">
                        <button type="submit" id="pay-button" class="w-full bg-primary text-white py-3 px-6 rounded-md hover:bg-green-600 font-semibold">
                            <i class="fas fa-credit-card mr-2"></i>Proceed to Payment (₹{{ total_amount }})
                        </button>
                    </div>
                </form>
            </div>
            
            <!-- Order Summary -->
            <div class="bg-darker p-6 rounded-lg border border-gray-800">
                <h2 class="text-xl font-semibold mb-6 text-white">Order Summary</h2>
                
                <div class="space-y-4">
                    <div class="flex justify-between">
                        <span class="text-gray-300">Plan:</span>
                        <span class="text-white font-semibold">{{ meal_plan.name }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-300">Frequency:</span>
                        <span class="text-white">{{ frequency.title() }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-300">Base Price:</span>
                        <span class="text-white">₹{{ base_price }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-300">GST (5%):</span>
                        <span class="text-white">₹{{ gst_amount }}</span>
                    </div>
                    <div class="border-t border-gray-700 pt-4">
                        <div class="flex justify-between font-semibold text-lg">
                            <span class="text-white">Total:</span>
                            <span class="text-primary">₹{{ total_amount }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
<script>
document.getElementById('checkout-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const button = document.getElementById('pay-button');
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
    
    const formData = new FormData(this);
    
    fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrf_token')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const options = {
                key: data.key_id,
                amount: data.amount,
                currency: data.currency,
                name: 'HealthyRizz',
                description: data.description,
                order_id: data.order_id,
                handler: function(response) {
                    // Payment successful - submit verification
                    const verifyForm = document.createElement('form');
                    verifyForm.method = 'POST';
                    verifyForm.action = '{{ url_for("main.verify_payment") }}';
                    verifyForm.style.display = 'none';
                    
                    // Add CSRF token
                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrf_token';
                    csrfInput.value = formData.get('csrf_token');
                    verifyForm.appendChild(csrfInput);
                    
                    // Add payment details
                    const paymentIdInput = document.createElement('input');
                    paymentIdInput.type = 'hidden';
                    paymentIdInput.name = 'razorpay_payment_id';
                    paymentIdInput.value = response.razorpay_payment_id;
                    verifyForm.appendChild(paymentIdInput);
                    
                    const orderIdInput = document.createElement('input');
                    orderIdInput.type = 'hidden';
                    orderIdInput.name = 'razorpay_order_id';
                    orderIdInput.value = response.razorpay_order_id;
                    verifyForm.appendChild(orderIdInput);
                    
                    const signatureInput = document.createElement('input');
                    signatureInput.type = 'hidden';
                    signatureInput.name = 'razorpay_signature';
                    signatureInput.value = response.razorpay_signature;
                    verifyForm.appendChild(signatureInput);
                    
                    document.body.appendChild(verifyForm);
                    verifyForm.submit();
                },
                prefill: {
                    name: formData.get('customer_name'),
                    email: formData.get('customer_email'),
                    contact: formData.get('customer_phone')
                },
                theme: {
                    color: '#4CAF50'
                }
            };
            
            const rzp = new Razorpay(options);
            rzp.open();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while processing your checkout.');
    })
    .finally(() => {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-credit-card mr-2"></i>Proceed to Payment (₹{{ total_amount }})';
    });
});
</script>
{% endblock %}
'''
    
    # Write the fixed template
    os.makedirs('templates', exist_ok=True)
    with open('templates/checkout_fixed.html', 'w') as f:
        f.write(checkout_template)
    
    print("✅ Fixed checkout template created")

def fix_payment_routes():
    """Fix payment processing routes"""
    print("🔧 Fixing Payment Routes...")
    
    # Create fixed payment routes
    routes_fix = '''
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
'''
    
    with open('routes_payment_fix.py', 'w') as f:
        f.write(routes_fix)
    
    print("✅ Fixed payment routes created")

def fix_success_template():
    """Create fixed checkout success template"""
    print("🔧 Creating Checkout Success Template...")
    
    success_template = '''{% extends "base.html" %}

{% block title %}Order Successful - HealthyRizz{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-2xl mx-auto text-center">
        <!-- Success Icon -->
        <div class="mb-8">
            <div class="mx-auto w-16 h-16 bg-green-500 rounded-full flex items-center justify-center">
                <i class="fas fa-check text-white text-2xl"></i>
            </div>
        </div>
        
        <!-- Success Message -->
        <h1 class="text-3xl font-bold text-white mb-4">Order Successful!</h1>
        <p class="text-gray-300 mb-8">Thank you for your purchase. Your order has been confirmed.</p>
        
        <!-- Order Details -->
        <div class="bg-darker p-6 rounded-lg border border-gray-800 mb-8">
            <h2 class="text-xl font-semibold text-white mb-4">Order Details</h2>
            
            <div class="space-y-3 text-left">
                <div class="flex justify-between">
                    <span class="text-gray-300">Order ID:</span>
                    <span class="text-white font-mono">#{{ order.id }}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-300">Payment ID:</span>
                    <span class="text-white font-mono">{{ order.payment_id[:20] }}...</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-300">Meal Plan:</span>
                    <span class="text-white">{{ meal_plan.name if meal_plan else 'N/A' }}</span>
                </div>
                {% if subscription %}
                <div class="flex justify-between">
                    <span class="text-gray-300">Frequency:</span>
                    <span class="text-white">{{ subscription.frequency.value.title() }}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-300">Next Delivery:</span>
                    <span class="text-white">{{ subscription.current_period_end.strftime('%Y-%m-%d') }}</span>
                </div>
                {% endif %}
                <div class="flex justify-between border-t border-gray-700 pt-3">
                    <span class="text-gray-300 font-semibold">Total Amount:</span>
                    <span class="text-primary font-bold text-lg">₹{{ "%.2f"|format(order.amount) }}</span>
                </div>
            </div>
        </div>
        
        <!-- Next Steps -->
        <div class="bg-darker p-6 rounded-lg border border-gray-800 mb-8">
            <h3 class="text-lg font-semibold text-white mb-4">What's Next?</h3>
            <div class="space-y-3 text-gray-300 text-sm">
                <p>✅ Your subscription is now active</p>
                <p>📧 You'll receive email confirmation shortly</p>
                <p>🚚 First delivery will be scheduled soon</p>
                <p>👤 Check your profile for subscription management</p>
            </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="space-y-4">
            {% if current_user.is_authenticated %}
            <a href="{{ url_for('main.profile') }}" class="inline-block bg-primary text-white px-6 py-3 rounded-md hover:bg-green-600 font-semibold">
                View My Profile
            </a>
            {% else %}
            <a href="{{ url_for('main.login') }}" class="inline-block bg-primary text-white px-6 py-3 rounded-md hover:bg-green-600 font-semibold">
                Login to Manage Subscription
            </a>
            {% endif %}
            
            <div>
                <a href="{{ url_for('main.meal_plans') }}" class="text-gray-400 hover:text-white">
                    ← Back to Meal Plans
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    with open('templates/checkout_success_fixed.html', 'w') as f:
        f.write(success_template)
    
    print("✅ Fixed checkout success template created")

def main():
    """Main function to run all fixes"""
    print("🔧 HealthyRizz Complete Payment Flow Fix")
    print("=" * 60)
    
    if not os.path.exists('main.py'):
        print("❌ main.py not found. Please run this script from the app directory.")
        return
    
    # Run all fixes
    fix_csrf_configuration()
    fix_checkout_template()
    fix_payment_routes()
    fix_success_template()
    
    print("\n🎉 Complete Payment Flow Fix Completed!")
    print("=" * 60)
    print("Files created:")
    print("1. .env - Fixed CSRF configuration")
    print("2. templates/checkout_fixed.html - Fixed checkout template")
    print("3. routes_payment_fix.py - Fixed payment routes")
    print("4. templates/checkout_success_fixed.html - Fixed success template")
    print("\nNext steps:")
    print("1. Replace your existing templates with the fixed ones")
    print("2. Update your routes with the fixed payment logic")
    print("3. Restart your application")
    print("4. Test the complete payment flow")

if __name__ == "__main__":
    main() 