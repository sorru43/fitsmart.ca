"""
User routes for the application
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from extensions import db
from database.models import User, Subscription

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return render_template('user/dashboard.html')

@user_bp.route('/subscriptions')
@login_required
def subscriptions():
    """User subscriptions"""
    user_subscriptions = Subscription.query.filter_by(user_id=current_user.id).all()
    return render_template('user/subscriptions.html', subscriptions=user_subscriptions)

@user_bp.route('/orders')
@login_required
def orders():
    """User orders"""
    return render_template('user/orders.html')

@user_bp.route('/settings')
@login_required
def settings():
    """User settings"""
    return render_template('user/settings.html') 