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

# 1. Dashboard
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

# 2. Users
@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    """Admin users management"""
    try:
        page = request.args.get('page', 1, type=int)
        users = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('admin/users.html', users=users)
    except Exception as e:
        current_app.logger.error(f"Users error: {str(e)}")
        # Create empty pagination for template
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
        
        return render_template('admin/users.html', users=EmptyPagination())

# 3. Meal Plans
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

# 4. Trial Requests
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

@admin_bp.route('/orders')
@login_required
@admin_required
def admin_orders():
    """Admin orders management"""
    try:
        page = request.args.get('page', 1, type=int)
        today = datetime.now().date()
        selected_date = request.args.get('date', str(today))
        
        # Create empty pagination for orders
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
        
        orders = EmptyPagination()
        return render_template('admin/orders.html', 
                             orders=orders, 
                             today=today,
                             selected_date=selected_date)
    except Exception as e:
        current_app.logger.error(f"Orders error: {str(e)}")
        return render_template('admin/orders.html', 
                             orders=EmptyPagination(),
                             today=datetime.now().date(),
                             selected_date=str(datetime.now().date()))

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
        # Create empty pagination for banners
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
        return render_template('admin/banners.html', banners=EmptyPagination())

@admin_bp.route('/coupons')
@login_required
@admin_required
def admin_coupons():
    """Admin coupons management"""
    try:
        # Create empty pagination for coupons
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
        return render_template('admin/coupons.html', coupons=EmptyPagination())

@admin_bp.route('/newsletters')
@login_required
@admin_required
def admin_newsletters():
    """Admin newsletters management"""
    try:
        # Create empty pagination for newsletters
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
        return render_template('admin/newsletters.html', newsletters=newsletters)
    except Exception as e:
        current_app.logger.error(f"Newsletters error: {str(e)}")
        return render_template('admin/newsletters.html', newsletters=EmptyPagination())
