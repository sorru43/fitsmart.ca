#!/usr/bin/env python3
"""
Simple test script to check payment-subscription flow
"""
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.models import db, Order, Subscription, User, MealPlan

def check_payment_subscription_flow():
    """Check the current state of payment-subscription flow"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking Payment-Subscription Flow...")
        
        # Check for orders without subscriptions
        orders_without_subscriptions = db.session.query(Order).filter(
            Order.status == 'confirmed',
            Order.payment_status == 'captured'
        ).outerjoin(Subscription, Order.id == Subscription.order_id).filter(
            Subscription.id.is_(None)
        ).all()
        
        print(f"Orders with successful payments but no subscriptions: {len(orders_without_subscriptions)}")
        
        if orders_without_subscriptions:
            print("\nProblematic orders:")
            for order in orders_without_subscriptions:
                print(f"  Order ID: {order.id}")
                print(f"    User ID: {order.user_id}")
                print(f"    Amount: {order.amount}")
                print(f"    Created: {order.created_at}")
                print(f"    Payment ID: {order.payment_id}")
                print()
        
        # Check for recent orders
        recent_orders = db.session.query(Order).filter(
            Order.created_at >= datetime.now() - timedelta(hours=24)
        ).all()
        
        print(f"Recent orders (last 24 hours): {len(recent_orders)}")
        
        for order in recent_orders:
            subscription = Subscription.query.filter_by(order_id=order.id).first()
            status = "✅ Has subscription" if subscription else "❌ No subscription"
            print(f"  Order {order.id}: {status}")
        
        return len(orders_without_subscriptions) == 0

if __name__ == "__main__":
    from datetime import timedelta
    check_payment_subscription_flow()
