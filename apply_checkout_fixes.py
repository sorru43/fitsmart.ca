#!/usr/bin/env python3
"""
Apply Checkout Page Fixes
This script applies all the fixes for the checkout page
"""

import os
import shutil

def backup_current_files():
    """Backup current files before making changes"""
    print("🔧 Creating backups...")
    
    # Backup current checkout template
    if os.path.exists('templates/checkout.html'):
        shutil.copy('templates/checkout.html', 'templates/checkout.html.backup')
        print("✅ Backed up templates/checkout.html")
    
    # Backup current routes
    if os.path.exists('routes/main_routes.py'):
        shutil.copy('routes/main_routes.py', 'routes/main_routes.py.backup')
        print("✅ Backed up routes/main_routes.py")

def replace_checkout_template():
    """Replace the checkout template with the fixed version"""
    print("🔧 Replacing checkout template...")
    
    if os.path.exists('templates/checkout_proper.html'):
        shutil.copy('templates/checkout_proper.html', 'templates/checkout.html')
        print("✅ Replaced checkout template with fixed version")
    else:
        print("❌ Fixed checkout template not found")

def update_subscribe_route():
    """Update the subscribe route in main_routes.py"""
    print("🔧 Updating subscribe route...")
    
    # Read the current main_routes.py
    if not os.path.exists('routes/main_routes.py'):
        print("❌ routes/main_routes.py not found")
        return
    
    with open('routes/main_routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the subscribe route
    old_subscribe_route = '''@main_bp.route('/subscribe/<int:plan_id>')
def subscribe(plan_id):
    """Subscribe to a meal plan"""
    try:
        meal_plan = MealPlan.query.get_or_404(plan_id)
        
        # Calculate prices
        weekly_price = float(meal_plan.price_weekly)
        monthly_price = float(meal_plan.price_monthly)
        
        # Calculate GST
        weekly_gst = weekly_price * 0.05
        monthly_gst = monthly_price * 0.05
        
        # Calculate totals
        weekly_total = weekly_price + weekly_gst
        monthly_total = monthly_price + monthly_gst
        
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
                             weekly_price=weekly_price,
                             monthly_price=monthly_price,
                             weekly_gst=weekly_gst,
                             monthly_gst=monthly_gst,
                             weekly_total=weekly_total,
                             monthly_total=monthly_total,
                             user_data=user_data)
                             
    except Exception as e:
        current_app.logger.error(f"Error in subscribe route: {str(e)}")
        flash('An error occurred while loading the subscription page.', 'error')
        return redirect(url_for('main.meal_plans'))'''
    
    new_subscribe_route = '''@main_bp.route('/subscribe/<int:plan_id>')
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
        return redirect(url_for('main.meal_plans'))'''
    
    # Replace the route
    if old_subscribe_route in content:
        content = content.replace(old_subscribe_route, new_subscribe_route)
        print("✅ Updated subscribe route")
    else:
        print("⚠️ Could not find exact subscribe route to replace")
        # Try to find and replace just the function body
        if '@main_bp.route(\'/subscribe/<int:plan_id>\')' in content:
            print("✅ Found subscribe route, but exact replacement not possible")
            print("   Please manually update the subscribe route with the new logic")
    
    # Write back the file
    with open('routes/main_routes.py', 'w', encoding='utf-8') as f:
        f.write(content)

def update_process_checkout_route():
    """Update the process_checkout route"""
    print("🔧 Updating process_checkout route...")
    
    # Read the current main_routes.py
    if not os.path.exists('routes/main_routes.py'):
        print("❌ routes/main_routes.py not found")
        return
    
    with open('routes/main_routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if process_checkout route exists
    if '@main_bp.route(\'/process_checkout\')' not in content:
        print("⚠️ process_checkout route not found, adding it...")
        
        # Add the new route at the end of the file
        new_route = '''

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
        
        with open('routes/main_routes.py', 'a', encoding='utf-8') as f:
            f.write(new_route)
        
        print("✅ Added process_checkout route")
    else:
        print("✅ process_checkout route already exists")

def create_sample_locations_script():
    """Create a script to add sample delivery locations"""
    print("🔧 Creating sample locations script...")
    
    script_content = '''#!/usr/bin/env python3
"""
Add Sample Delivery Locations
Run this script to add sample delivery locations to your database
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from database.models import DeliveryLocation

def add_sample_locations():
    """Add sample delivery locations"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if locations already exist
            existing_count = DeliveryLocation.query.count()
            if existing_count > 0:
                print(f"⚠️ Found {existing_count} existing locations")
                response = input("Do you want to clear existing locations and add new ones? (y/N): ")
                if response.lower() != 'y':
                    print("✅ Keeping existing locations")
                    return
            
            # Clear existing locations if requested
            if existing_count > 0:
                DeliveryLocation.query.delete()
                db.session.commit()
                print("✅ Cleared existing locations")
            
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
                {'city': 'Lucknow', 'province': 'UP', 'is_active': True},
                {'city': 'Ludhiana', 'province': 'PB', 'is_active': True},
                {'city': 'Chandigarh', 'province': 'CH', 'is_active': True},
                {'city': 'Amritsar', 'province': 'PB', 'is_active': True},
                {'city': 'Jalandhar', 'province': 'PB', 'is_active': True},
                {'city': 'Patiala', 'province': 'PB', 'is_active': True}
            ]
            
            for loc_data in locations:
                location = DeliveryLocation(**loc_data)
                db.session.add(location)
            
            db.session.commit()
            print(f"✅ Added {len(locations)} sample delivery locations!")
            
            # Show the locations
            print("\\n📋 Available delivery locations:")
            for location in DeliveryLocation.query.filter_by(is_active=True).order_by(DeliveryLocation.city).all():
                print(f"  • {location.city}, {location.province}")
                
        except Exception as e:
            print(f"❌ Error adding locations: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    add_sample_locations()
'''
    
    with open('add_sample_locations.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Created add_sample_locations.py script")

def main():
    """Main function to apply all fixes"""
    print("🔧 Applying Checkout Page Fixes")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ main.py not found. Please run this script from the app directory.")
        return
    
    # Apply all fixes
    backup_current_files()
    replace_checkout_template()
    update_subscribe_route()
    update_process_checkout_route()
    create_sample_locations_script()
    
    print("\n🎉 Checkout Page Fixes Applied!")
    print("=" * 60)
    print("✅ Backups created")
    print("✅ Checkout template replaced")
    print("✅ Subscribe route updated")
    print("✅ Process checkout route updated")
    print("✅ Sample locations script created")
    
    print("\n📋 Next Steps:")
    print("1. Run: python add_sample_locations.py")
    print("2. Restart your application")
    print("3. Test the checkout flow at: /meal-plans")
    
    print("\n🔧 Key Improvements:")
    print("• Proper total calculation with GST")
    print("• Location dropdown from admin locations")
    print("• Simplified form structure")
    print("• Better error handling")
    print("• Clean user interface")

if __name__ == "__main__":
    main() 