#!/usr/bin/env python3
"""
Fix Checkout Page with Proper Total Calculation and Location Dropdown
This script fixes the checkout page to use admin locations and calculate totals correctly
"""

import os

def fix_checkout_route():
    """Fix checkout route to pass locations and calculate totals properly"""
    print("🔧 Fixing Checkout Route...")
    
    checkout_route_fix = '''
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
'''
    
    with open('checkout_route_fix.py', 'w') as f:
        f.write(checkout_route_fix)
    
    print("✅ Fixed checkout route created")

def fix_checkout_template():
    """Fix checkout template with location dropdown and proper total calculation"""
    print("🔧 Fixing Checkout Template...")
    
    checkout_template = '''{% extends "base.html" %}

{% block title %}Checkout - {{ meal_plan.name }} - HealthyRizz{% endblock %}

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
                                   value="{{ user_data.name if user_data else '' }}">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">Email Address *</label>
                            <input type="email" name="customer_email" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600"
                                   value="{{ user_data.email if user_data else '' }}">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">Phone Number *</label>
                            <input type="tel" name="customer_phone" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600"
                                   value="{{ user_data.phone if user_data else '' }}">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">Delivery Location *</label>
                            <select name="delivery_location_id" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600">
                                <option value="">Select your delivery location</option>
                                {% for location in delivery_locations %}
                                <option value="{{ location.id }}" 
                                        data-city="{{ location.city }}" 
                                        data-province="{{ location.province }}">
                                    {{ location.city }}, {{ location.province }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">Complete Address *</label>
                            <textarea name="customer_address" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600" rows="3" 
                                      placeholder="Enter your complete delivery address">{{ user_data.address if user_data else '' }}</textarea>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">PIN Code *</label>
                            <input type="text" name="customer_pincode" required class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600"
                                   value="{{ user_data.postal_code if user_data else '' }}" maxlength="6" pattern="[0-9]{6}">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium mb-2 text-white">Delivery Instructions</label>
                            <textarea name="delivery_instructions" class="w-full px-3 py-2 rounded-md bg-dark text-white border border-gray-600" rows="2" 
                                      placeholder="Any special delivery instructions (optional)"></textarea>
                        </div>
                    </div>
                    
                    <div class="mt-6">
                        <button type="submit" id="pay-button" class="w-full bg-primary text-white py-3 px-6 rounded-md hover:bg-green-600 font-semibold">
                            <i class="fas fa-credit-card mr-2"></i>Proceed to Payment (₹{{ "%.2f"|format(total_amount) }})
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
                        <span class="text-white">₹{{ "%.2f"|format(base_price) }}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-300">GST (5%):</span>
                        <span class="text-white">₹{{ "%.2f"|format(gst_amount) }}</span>
                    </div>
                    <div class="border-t border-gray-700 pt-4">
                        <div class="flex justify-between font-semibold text-lg">
                            <span class="text-white">Total:</span>
                            <span class="text-primary">₹{{ "%.2f"|format(total_amount) }}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Plan Details -->
                <div class="mt-6 pt-6 border-t border-gray-700">
                    <h3 class="text-lg font-semibold text-white mb-3">Plan Details</h3>
                    <div class="space-y-2 text-sm text-gray-300">
                        <p>• {{ meal_plan.description }}</p>
                        <p>• {{ meal_plan.meals_per_day }} meals per day</p>
                        <p>• {{ meal_plan.days_per_week }} days per week</p>
                        {% if meal_plan.vegetarian_options %}
                        <p>• Vegetarian options available</p>
                        {% endif %}
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
    
    // Validate location selection
    const locationSelect = document.querySelector('select[name="delivery_location_id"]');
    if (!locationSelect.value) {
        alert('Please select a delivery location');
        return;
    }
    
    const button = document.getElementById('pay-button');
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
    
    const formData = new FormData(this);
    
    // Add location details to form data
    const selectedOption = locationSelect.options[locationSelect.selectedIndex];
    formData.append('customer_city', selectedOption.dataset.city);
    formData.append('customer_state', selectedOption.dataset.province);
    
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
        button.innerHTML = '<i class="fas fa-credit-card mr-2"></i>Proceed to Payment (₹{{ "%.2f"|format(total_amount) }})';
    });
});

// Auto-fill city and state when location is selected
document.querySelector('select[name="delivery_location_id"]').addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    if (selectedOption.value) {
        // You can auto-fill other fields if needed
        console.log('Selected location:', selectedOption.dataset.city, selectedOption.dataset.province);
    }
});
</script>
{% endblock %}
'''
    
    with open('templates/checkout_proper.html', 'w') as f:
        f.write(checkout_template)
    
    print("✅ Fixed checkout template created")

def fix_process_checkout_route():
    """Fix process_checkout route to handle location data properly"""
    print("🔧 Fixing Process Checkout Route...")
    
    process_checkout_fix = '''
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
'''
    
    with open('process_checkout_fix.py', 'w') as f:
        f.write(process_checkout_fix)
    
    print("✅ Fixed process checkout route created")

def create_sample_locations():
    """Create sample delivery locations for testing"""
    print("🔧 Creating Sample Delivery Locations...")
    
    sample_locations = '''
# Sample Delivery Locations for Testing
# Run this in your Flask shell or create a script

from app import create_app, db
from database.models import DeliveryLocation

app = create_app()

with app.app_context():
    # Clear existing locations
    DeliveryLocation.query.delete()
    
    # Create sample locations
    locations = [
        {'city': 'Mumbai', 'province': 'MH', 'is_active': True},
        {'city': 'Delhi', 'province': 'DL', 'is_active': True},
        {'city': 'Bangalore', 'province': 'KA', 'is_active': True},
        {'city': 'Hyderabad', 'province': 'TS', 'is_active': True},
        {'city': 'Chennai', 'province': 'TN', 'is_active': True},
        {'city': 'Kolkata', 'province': 'WB', 'is_active': True},
        {'city': 'Pune', 'province': 'MH', 'is_active': True},
        {'city': 'Ahmedabad', 'province': 'GJ', 'is_active': True},
        {'city': 'Jaipur', 'province': 'RJ', 'is_active': True},
        {'city': 'Lucknow', 'province': 'UP', 'is_active': True}
    ]
    
    for loc_data in locations:
        location = DeliveryLocation(**loc_data)
        db.session.add(location)
    
    db.session.commit()
    print("✅ Sample delivery locations created!")
'''
    
    with open('create_sample_locations.py', 'w') as f:
        f.write(sample_locations)
    
    print("✅ Sample locations script created")

def main():
    """Main function to run all checkout fixes"""
    print("🔧 HealthyRizz Checkout Page Fix")
    print("=" * 60)
    
    if not os.path.exists('main.py'):
        print("❌ main.py not found. Please run this script from the app directory.")
        return
    
    # Run all fixes
    fix_checkout_route()
    fix_checkout_template()
    fix_process_checkout_route()
    create_sample_locations()
    
    print("\n🎉 Checkout Page Fix Completed!")
    print("=" * 60)
    print("Files created:")
    print("1. checkout_route_fix.py - Fixed subscribe route")
    print("2. templates/checkout_proper.html - Fixed checkout template")
    print("3. process_checkout_fix.py - Fixed process checkout route")
    print("4. create_sample_locations.py - Sample locations script")
    print("\nNext steps:")
    print("1. Update your routes with the fixed checkout logic")
    print("2. Replace checkout template with the fixed one")
    print("3. Run create_sample_locations.py to add sample locations")
    print("4. Test the checkout flow with location dropdown")
    print("\nKey improvements:")
    print("✅ Proper total calculation with GST")
    print("✅ Location dropdown from admin locations")
    print("✅ Form validation and error handling")
    print("✅ Clean user interface")

if __name__ == "__main__":
    main() 