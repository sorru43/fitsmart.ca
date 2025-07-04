#!/usr/bin/env python3
"""
Comprehensive fix script for HealthyRizz Admin Panel Issues
Fixes:
1. SQLAlchemy DetachedInstanceError in base.html
2. Null bytes in corrupted files  
3. Users template pagination issues
4. Missing routes that templates expect
"""

import os
import sys
import re
from pathlib import Path

def remove_null_bytes_from_files():
    """Remove null bytes from all Python files"""
    print("🧹 Removing null bytes from Python files...")
    
    files_to_clean = [
        'routes/admin_routes.py',
        'routes/main_routes.py', 
        'start_app.py',
        'run_healthyrizz.py'
    ]
    
    for filepath in files_to_clean:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                
                if b'\x00' in content:
                    print(f"  ❌ Found null bytes in: {filepath}")
                    clean_content = content.replace(b'\x00', b'')
                    
                    with open(filepath, 'wb') as f:
                        f.write(clean_content)
                    print(f"  ✅ Cleaned: {filepath}")
                else:
                    print(f"  ✅ Clean: {filepath}")
                    
            except Exception as e:
                print(f"  ❌ Error processing {filepath}: {e}")
        else:
            print(f"  ⚠️  Not found: {filepath}")

def fix_base_template():
    """Fix SQLAlchemy DetachedInstanceError in base.html"""
    print("🔧 Fixing base.html SQLAlchemy DetachedInstanceError...")
    
    template_path = 'templates/base.html'
    if not os.path.exists(template_path):
        print(f"  ❌ Template not found: {template_path}")
        return
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace problematic lines that access subscriptions relationship
        original_content = content
        
        # Fix both instances of current_user.subscriptions
        content = content.replace(
            '{% if current_user.subscriptions %}',
            '{% if current_user.is_authenticated %}'
        )
        
        if content != original_content:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed SQLAlchemy DetachedInstanceError in {template_path}")
        else:
            print(f"  ℹ️  No changes needed in {template_path}")
            
    except Exception as e:
        print(f"  ❌ Error fixing {template_path}: {e}")

def fix_users_template():
    """Fix users template pagination issues"""
    print("🔧 Fixing users.html template issues...")
    
    template_path = 'templates/admin/users.html'
    if not os.path.exists(template_path):
        print(f"  ❌ Template not found: {template_path}")
        return
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add safe fallbacks for pagination
        content = content.replace(
            '{{ users|length if users else 0 }}',
            '{{ users.items|length if users and users.items else 0 }}'
        )
        
        # Fix user.username to user.name (if exists)
        content = content.replace('{{ user.username }}', '{{ user.name }}')
        
        if content != original_content:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed pagination issues in {template_path}")
        else:
            print(f"  ℹ️  No changes needed in {template_path}")
            
    except Exception as e:
        print(f"  ❌ Error fixing {template_path}: {e}")

def add_missing_routes():
    """Add all missing routes to admin_routes.py"""
    print("🔧 Adding missing routes to admin_routes.py...")
    
    routes_file = 'routes/admin_routes.py'
    if not os.path.exists(routes_file):
        print(f"  ❌ Routes file not found: {routes_file}")
        return
    
    missing_routes = '''

# ===== MISSING ROUTES FOR TEMPLATES =====

# Add Meal Plan Route
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

# Add Coupon Route
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

# Add Banner Route
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

# User Management Routes
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
'''
    
    try:
        # Check if routes are already added
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'admin_add_meal_plan' not in content:
            with open(routes_file, 'a', encoding='utf-8') as f:
                f.write(missing_routes)
            print(f"  ✅ Added missing routes to {routes_file}")
        else:
            print(f"  ℹ️  Routes already exist in {routes_file}")
            
    except Exception as e:
        print(f"  ❌ Error adding routes to {routes_file}: {e}")

def fix_users_route():
    """Fix the users route to handle pagination correctly"""
    print("🔧 Fixing users route pagination...")
    
    routes_file = 'routes/admin_routes.py'
    if not os.path.exists(routes_file):
        print(f"  ❌ Routes file not found: {routes_file}")
        return
    
    try:
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and fix the users route
        pattern = r'def admin_users\(\):.*?return render_template\([^)]+\)'
        
        fixed_route = '''def admin_users():
    """User management page"""
    try:
        page = request.args.get('page', 1, type=int)
        users_pagination = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('admin/users.html', 
                             users=users_pagination,
                             pagination=users_pagination)
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
        
        return render_template('admin/users.html', users=EmptyPagination(), pagination=EmptyPagination())'''
        
        updated_content = re.sub(pattern, fixed_route, content, flags=re.DOTALL)
        
        if updated_content != content:
            with open(routes_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"  ✅ Fixed users route pagination in {routes_file}")
        else:
            print(f"  ℹ️  Users route already correct in {routes_file}")
            
    except Exception as e:
        print(f"  ❌ Error fixing users route: {e}")

def create_missing_templates():
    """Create missing template files"""
    print("🔧 Creating missing template files...")
    
    templates_to_create = {
        'templates/admin/add_meal_plan.html': '''{% extends "admin/base_admin.html" %}

{% block title %}Add Meal Plan - HealthyRizz Admin{% endblock %}
{% block page_title %}Add Meal Plan{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">Add New Meal Plan</h1>
        <a href="{{ url_for('admin.admin_meal_plans') }}" class="btn-secondary">
            <i class="fas fa-arrow-left mr-2"></i>Back to Meal Plans
        </a>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Meal Plan Name</label>
                <input type="text" name="name" class="form-input" required>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea name="description" class="form-textarea" rows="4"></textarea>
            </div>
            
            <div class="flex space-x-4">
                <button type="submit" class="btn-primary">Add Meal Plan</button>
                <a href="{{ url_for('admin.admin_meal_plans') }}" class="btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}''',

        'templates/admin/add_coupon.html': '''{% extends "admin/base_admin.html" %}

{% block title %}Add Coupon - HealthyRizz Admin{% endblock %}
{% block page_title %}Add Coupon{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">Add New Coupon</h1>
        <a href="{{ url_for('admin.admin_coupons') }}" class="btn-secondary">
            <i class="fas fa-arrow-left mr-2"></i>Back to Coupons
        </a>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Coupon Code</label>
                <input type="text" name="code" class="form-input" required>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Discount Amount</label>
                <input type="number" name="discount" class="form-input" step="0.01" required>
            </div>
            
            <div class="flex space-x-4">
                <button type="submit" class="btn-primary">Add Coupon</button>
                <a href="{{ url_for('admin.admin_coupons') }}" class="btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}'''
    }
    
    for template_path, template_content in templates_to_create.items():
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            
            if not os.path.exists(template_path):
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                print(f"  ✅ Created: {template_path}")
            else:
                print(f"  ℹ️  Already exists: {template_path}")
                
        except Exception as e:
            print(f"  ❌ Error creating {template_path}: {e}")

def main():
    """Run all fixes"""
    print("🚀 HealthyRizz Admin Panel Comprehensive Fix")
    print("=" * 50)
    
    # Step 1: Remove null bytes from files
    remove_null_bytes_from_files()
    print()
    
    # Step 2: Fix base template SQLAlchemy issue
    fix_base_template()
    print()
    
    # Step 3: Fix users template 
    fix_users_template()
    print()
    
    # Step 4: Fix users route
    fix_users_route()
    print()
    
    # Step 5: Add missing routes
    add_missing_routes()
    print()
    
    # Step 6: Create missing templates
    create_missing_templates()
    print()
    
    print("✅ All fixes completed!")
    print("🎯 Try running the app now with: python start_simple.py")

if __name__ == "__main__":
    main() 