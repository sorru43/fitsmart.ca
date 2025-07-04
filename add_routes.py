#!/usr/bin/env python3
"""Script to add missing routes to admin_routes.py"""

missing_routes = """

# ===== MISSING ROUTES FOR TEMPLATES =====

# Add Meal Plan Route
@admin_bp.route('/add-meal-plan', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_meal_plan():
    \"\"\"Add new meal plan\"\"\"
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
    \"\"\"Add new coupon\"\"\"
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
    \"\"\"Add new banner\"\"\"
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
    \"\"\"Toggle user active status\"\"\"
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
    \"\"\"Toggle user admin status\"\"\"
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
    \"\"\"Delete user\"\"\"
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
"""

# Add routes to admin_routes.py
with open('routes/admin_routes.py', 'a', encoding='utf-8') as f:
    f.write(missing_routes)

print("✅ Missing routes added successfully to admin_routes.py") 