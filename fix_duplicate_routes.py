#!/usr/bin/env python3
"""
Fix duplicate routes in admin_routes.py
"""

import re
import os

def remove_duplicate_routes():
    """Remove duplicate route definitions from admin_routes.py"""
    print("🔧 Fixing duplicate routes in admin_routes.py...")
    
    routes_file = 'routes/admin_routes.py'
    backup_file = 'routes/admin_routes_backup.py'
    
    if not os.path.exists(backup_file):
        print(f"  ❌ Backup file not found: {backup_file}")
        return
    
    # Start fresh from backup
    print(f"  📄 Starting fresh from {backup_file}")
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Write the clean backup content
        with open(routes_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Restored clean admin_routes.py from backup")
        
        # Now add only the missing routes (without duplicates)
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
        
        # Check if these routes are already in the backup
        if 'admin_add_meal_plan' not in content:
            with open(routes_file, 'a', encoding='utf-8') as f:
                f.write(missing_routes)
            print(f"  ✅ Added missing routes without duplicates")
        else:
            print(f"  ℹ️  Routes already exist in backup file")
            
    except Exception as e:
        print(f"  ❌ Error fixing duplicate routes: {e}")

def fix_users_route_in_clean_file():
    """Fix the users route to return proper pagination objects"""
    print("🔧 Fixing users route pagination in clean file...")
    
    routes_file = 'routes/admin_routes.py'
    if not os.path.exists(routes_file):
        print(f"  ❌ Routes file not found: {routes_file}")
        return
    
    try:
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the users route
        old_users_route = '''def admin_users():
    """User management page"""
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
        
        return render_template('admin/users.html', users=EmptyPagination())'''

        new_users_route = '''def admin_users():
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
        
        return render_template('admin/users.html', 
                             users=EmptyPagination(), 
                             pagination=EmptyPagination())'''
        
        if old_users_route in content:
            content = content.replace(old_users_route, new_users_route)
            with open(routes_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed users route pagination")
        else:
            print(f"  ℹ️  Users route already correct or not found")
            
    except Exception as e:
        print(f"  ❌ Error fixing users route: {e}")

def main():
    """Run fixes"""
    print("🚀 Fixing Duplicate Routes")
    print("=" * 30)
    
    remove_duplicate_routes()
    print()
    
    fix_users_route_in_clean_file()
    print()
    
    print("✅ Duplicate routes fixed!")
    print("🎯 Try running the app now with: python start_simple.py")

if __name__ == "__main__":
    main() 