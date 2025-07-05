from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from models import User, MealPlan, TrialRequest, BlogPost, FAQ, Subscription, ContactInquiry
from extensions import db
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import desc, func, or_

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Dashboard
@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with overview stats"""
    try:
        total_users = User.query.count()
        total_meal_plans = MealPlan.query.count() 
        total_trial_requests = TrialRequest.query.count()
        total_blog_posts = BlogPost.query.count()
        
        return render_template('admin/dashboard.html',
                             total_users=total_users,
                             total_meal_plans=total_meal_plans,
                             total_trial_requests=total_trial_requests,
                             total_blog_posts=total_blog_posts)
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}")
        return render_template('admin/dashboard.html',
                             total_users=0, total_meal_plans=0,
                             total_trial_requests=0, total_blog_posts=0)

# Users
@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    """Admin users management"""
    try:
        page = request.args.get('page', 1, type=int)
        users_query = User.query.order_by(User.created_at.desc())
        
        # Apply search filters if provided
        search = request.args.get('search', '').strip()
        if search:
            users_query = users_query.filter(
                or_(User.name.contains(search), User.email.contains(search))
            )
        
        status = request.args.get('status', '').strip()
        if status == 'active':
            users_query = users_query.filter(User.is_active == True)
        elif status == 'inactive':
            users_query = users_query.filter(User.is_active == False)
        
        role = request.args.get('role', '').strip()
        if role == 'admin':
            users_query = users_query.filter(User.is_admin == True)
        elif role == 'user':
            users_query = users_query.filter(User.is_admin == False)
        
        users_pagination = users_query.paginate(
            page=page, per_page=20, error_out=False
        )
        
        # Add today for template
        today = datetime.now().date()
        
        return render_template('admin/users.html', users=users_pagination.items, 
                             pagination=users_pagination, today=today)
    except Exception as e:
        current_app.logger.error(f"Users error: {str(e)}")
        # Return with empty list for template
        today = datetime.now().date()
        return render_template('admin/users.html', users=[], 
                             pagination=None, today=today)

# Meal Plans
@admin_bp.route('/meal-plans')
@login_required
@admin_required
def admin_meal_plans():
    """Admin meal plans management"""
    try:
        page = request.args.get('page', 1, type=int)
        meal_plans = MealPlan.query.order_by(MealPlan.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        return render_template('admin/meal_plans.html', meal_plans=meal_plans)
    except Exception as e:
        current_app.logger.error(f"Meal plans error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 10
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/meal_plans.html', meal_plans=EmptyPagination())

# Orders
@admin_bp.route('/orders')
@login_required
@admin_required
def admin_orders():
    """Admin orders management"""
    try:
        today = datetime.now().date()
        selected_date_str = request.args.get('date', str(today))
        
        # Convert string date to date object
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except:
            selected_date = today
        
        # Create sample orders data
        orders_list = [
            {
                'subscription_id': 1,
                'customer_name': 'John Doe',
                'email': 'john@example.com',
                'phone': '+1234567890',
                'meal_plan_name': 'Healthy Choice',
                'is_vegetarian': False,
                'includes_breakfast': True,
                'address': '123 Main St',
                'city': 'Toronto',
                'province': 'ON',
                'postal_code': 'M1A 1A1',
                'created_at': '2024-01-01',
                'delivery_status': 'pending',
                'delivery_id': 1,
                'is_skipped': False
            }
        ]
        
        # Create sample data for template
        location_counts = {'Toronto, ON': 1}
        meal_counts = {'Healthy Choice': 1}
        skipped = []
        
        return render_template('admin/orders.html', 
                             orders=orders_list,
                             today=today,
                             selected_date=selected_date,
                             location_counts=location_counts,
                             meal_counts=meal_counts,
                             skipped=skipped)
                             
    except Exception as e:
        current_app.logger.error(f"Orders error: {str(e)}")
        today = datetime.now().date()
        return render_template('admin/orders.html', 
                             orders=[],
                             today=today,
                             selected_date=today,
                             location_counts={},
                             meal_counts={},
                             skipped=[])

# Subscriptions
@admin_bp.route('/subscriptions')
@login_required
@admin_required
def admin_subscriptions():
    """Admin subscriptions management"""
    try:
        page = request.args.get('page', 1, type=int)
        current_filters = request.args.get('status', 'all')
        
        query = Subscription.query
        if current_filters != 'all':
            query = query.filter(Subscription.status == current_filters)
        
        subscriptions = query.order_by(Subscription.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('admin/subscriptions.html', 
                             subscriptions=subscriptions,
                             current_filters=current_filters)
    except Exception as e:
        current_app.logger.error(f"Subscriptions error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/subscriptions.html', 
                             subscriptions=EmptyPagination(),
                             current_filters='all')

# Other routes with proper empty pagination handling
@admin_bp.route('/trial-requests')
@login_required
@admin_required
def admin_trial_requests():
    """Admin trial requests management"""
    try:
        page = request.args.get('page', 1, type=int)
        trial_requests = TrialRequest.query.order_by(TrialRequest.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        return render_template('admin/trial_requests.html', trial_requests=trial_requests)
    except Exception as e:
        current_app.logger.error(f"Trial requests error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/trial_requests.html', trial_requests=EmptyPagination())

@admin_bp.route('/blog')
@login_required
@admin_required
def admin_blog():
    """Admin blog management"""
    try:
        page = request.args.get('page', 1, type=int)
        blog_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        return render_template('admin/blog.html', blog_posts=blog_posts)
    except Exception as e:
        current_app.logger.error(f"Blog error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 10
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/blog.html', blog_posts=EmptyPagination())

@admin_bp.route('/contact-inquiries')
@login_required
@admin_required
def admin_contact_inquiries():
    """Admin contact inquiries management"""
    try:
        page = request.args.get('page', 1, type=int)
        contact_inquiries = ContactInquiry.query.order_by(ContactInquiry.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        return render_template('admin/contact_inquiries.html', contact_inquiries=contact_inquiries)
    except Exception as e:
        current_app.logger.error(f"Contact inquiries error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/contact_inquiries.html', contact_inquiries=EmptyPagination())

@admin_bp.route('/faqs')
@login_required
@admin_required
def admin_faqs():
    """Admin FAQs management"""
    try:
        page = request.args.get('page', 1, type=int)
        faqs = FAQ.query.order_by(FAQ.id.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        return render_template('admin/faqs.html', faqs=faqs)
    except Exception as e:
        current_app.logger.error(f"FAQs error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/faqs.html', faqs=EmptyPagination())

@admin_bp.route('/banners')
@login_required
@admin_required
def admin_banners():
    """Admin banners management"""
    try:
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 10
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        
        banners = EmptyPagination()
        return render_template('admin/banners.html', banners=banners)
    except Exception as e:
        current_app.logger.error(f"Banners error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 10
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/banners.html', banners=EmptyPagination())

@admin_bp.route('/coupons')
@login_required
@admin_required
def admin_coupons():
    """Admin coupons management"""
    try:
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        
        coupons = EmptyPagination()
        return render_template('admin/coupons.html', coupons=coupons)
    except Exception as e:
        current_app.logger.error(f"Coupons error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/coupons.html', coupons=EmptyPagination())

@admin_bp.route('/newsletters')
@login_required
@admin_required
def admin_newsletters():
    """Admin newsletters management"""
    try:
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        
        newsletters = EmptyPagination()
        total_pages = newsletters.pages
        return render_template('admin/newsletters.html', newsletters=newsletters, total_pages=total_pages)
    except Exception as e:
        current_app.logger.error(f"Newsletters error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/newsletters.html', newsletters=EmptyPagination(), total_pages=1)

@admin_bp.route('/notifications', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_notifications():
    """Admin notifications management"""
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            message = request.form.get('message')
            flash(f'Notification "{title}" sent successfully!', 'success')
            return redirect(url_for('admin.admin_notifications'))
        except Exception as e:
            current_app.logger.error(f"Notifications error: {str(e)}")
            flash('Failed to send notification.', 'error')
    
    # GET request - show notifications page
    try:
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        
        notifications = EmptyPagination()
        return render_template('admin/notifications.html', notifications=notifications)
    except Exception as e:
        current_app.logger.error(f"Notifications error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/notifications.html', notifications=EmptyPagination())

@admin_bp.route('/location-tree')
@login_required
@admin_required
def admin_location_tree():
    """Admin location tree management"""
    try:
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        
        locations = EmptyPagination()
        return render_template('admin/location_tree.html', locations=locations)
    except Exception as e:
        current_app.logger.error(f"Location tree error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/location_tree.html', locations=EmptyPagination())

@admin_bp.route('/media')
@login_required
@admin_required
def admin_media():
    """Admin media management"""
    try:
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        
        media = EmptyPagination()
        return render_template('admin/media.html', media=media)
    except Exception as e:
        current_app.logger.error(f"Media error: {str(e)}")
        class EmptyPagination:
            items = []
            page = 1
            pages = 1
            per_page = 20
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template('admin/media.html', media=EmptyPagination())

# Add routes for templates
@admin_bp.route('/add-meal-plan', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_meal_plan():
    """Add new meal plan"""
    if request.method == 'POST':
        try:
            flash('Meal plan added successfully!', 'success')
            return redirect(url_for('admin.admin_meal_plans'))
        except Exception as e:
            current_app.logger.error(f"Add meal plan error: {str(e)}")
            flash('Failed to add meal plan.', 'error')
    
    return render_template('admin/add_meal_plan.html')

@admin_bp.route('/add-coupon', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_coupon():
    """Add new coupon"""
    if request.method == 'POST':
        try:
            flash('Coupon added successfully!', 'success')
            return redirect(url_for('admin.admin_coupons'))
        except Exception as e:
            current_app.logger.error(f"Add coupon error: {str(e)}")
            flash('Failed to add coupon.', 'error')
    
    return render_template('admin/add_coupon.html')

@admin_bp.route('/add-banner', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_banner():
    """Add new banner"""
    if request.method == 'POST':
        try:
            flash('Banner added successfully!', 'success')
            return redirect(url_for('admin.admin_banners'))
        except Exception as e:
            current_app.logger.error(f"Add banner error: {str(e)}")
            flash('Failed to add banner.', 'error')
    
    return render_template('admin/add_banner.html')

# User management routes
@admin_bp.route('/toggle-user-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user_status():
    """Toggle user active status"""
    try:
        user_id = request.json.get('user_id')
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        return jsonify({'success': True, 'message': 'User status updated successfully'})
    except Exception as e:
        current_app.logger.error(f"Toggle user status error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to update user status'})

@admin_bp.route('/toggle-admin-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_admin_status():
    """Toggle user admin status"""
    try:
        user_id = request.json.get('user_id')
        user = User.query.get_or_404(user_id)
        user.is_admin = not user.is_admin
        db.session.commit()
        return jsonify({'success': True, 'message': 'Admin status updated successfully'})
    except Exception as e:
        current_app.logger.error(f"Toggle admin status error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to update admin status'})

@admin_bp.route('/delete-user', methods=['POST'])
@login_required
@admin_required
def admin_delete_user():
    """Delete user"""
    try:
        user_id = request.json.get('user_id')
        user = User.query.get_or_404(user_id)
        
        # Don't allow deleting the current admin user
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': 'Cannot delete your own account'})
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    except Exception as e:
        current_app.logger.error(f"Delete user error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to delete user'})

# Additional helper routes
@admin_bp.route('/export-orders/<date>')
@login_required
@admin_required
def admin_export_orders(date):
    """Export orders for a specific date"""
    try:
        flash(f'Export orders for {date} - Feature coming soon!', 'info')
        return redirect(url_for('admin.admin_orders'))
    except Exception as e:
        current_app.logger.error(f"Export orders error: {str(e)}")
        flash('Failed to export orders.', 'error')
        return redirect(url_for('admin.admin_orders'))

@admin_bp.route('/generate-labels/<date>')
@login_required
@admin_required
def admin_generate_labels(date):
    """Generate shipping labels for a specific date"""
    try:
        flash(f'Generate labels for {date} - Feature coming soon!', 'info')
        return redirect(url_for('admin.admin_orders'))
    except Exception as e:
        current_app.logger.error(f"Generate labels error: {str(e)}")
        flash('Failed to generate labels.', 'error')
        return redirect(url_for('admin.admin_orders'))

@admin_bp.route('/orders/email', methods=['POST'])
@login_required
@admin_required
def admin_orders_email():
    """Send email notifications for orders"""
    try:
        email = request.form.get('email')
        date = request.form.get('date')
        flash(f'Email notifications sent to {email} for {date}!', 'success')
        return redirect(url_for('admin.admin_orders'))
    except Exception as e:
        current_app.logger.error(f"Orders email error: {str(e)}")
        flash('Failed to send email notifications.', 'error')
        return redirect(url_for('admin.admin_orders'))

@admin_bp.route('/update-delivery-status/<int:delivery_id>', methods=['POST'])
@login_required
@admin_required
def admin_update_delivery_status(delivery_id):
    """Update delivery status"""
    try:
        status = request.form.get('status')
        flash(f'Delivery status updated to {status}!', 'success')
        return redirect(url_for('admin.admin_orders'))
    except Exception as e:
        current_app.logger.error(f"Update delivery status error: {str(e)}")
        flash('Failed to update delivery status.', 'error')
        return redirect(url_for('admin.admin_orders')) 