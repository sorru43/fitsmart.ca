#!/usr/bin/env python3
"""
Utility script to identify and fix failed subscriptions
where payment was successful but subscription creation failed.
"""
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.models import db, Order, Subscription, User, MealPlan, SubscriptionStatus, SubscriptionFrequency
from sqlalchemy.exc import IntegrityError

def find_failed_subscriptions():
    """Find orders where payment was successful but no subscription exists"""
    app = create_app()
    
    with app.app_context():
        # Find orders that are confirmed but don't have associated subscriptions
        failed_orders = db.session.query(Order).filter(
            Order.status == 'confirmed',
            Order.payment_status == 'captured',
            ~Order.id.in_(
                db.session.query(Subscription.order_id).filter(Subscription.order_id.isnot(None))
            )
        ).all()
        
        print(f"Found {len(failed_orders)} orders with successful payments but no subscriptions:")
        
        for order in failed_orders:
            print(f"Order ID: {order.id}")
            print(f"  User ID: {order.user_id}")
            print(f"  Meal Plan ID: {order.meal_plan_id}")
            print(f"  Amount: {order.amount}")
            print(f"  Payment ID: {order.payment_id}")
            print(f"  Order ID: {order.order_id}")
            print(f"  Created: {order.created_at}")
            print("  ---")
        
        return failed_orders

def fix_failed_subscription(order):
    """Fix a failed subscription by creating it for the given order"""
    try:
        # Get user and meal plan
        user = User.query.get(order.user_id)
        meal_plan = MealPlan.query.get(order.meal_plan_id)
        
        if not user:
            print(f"  ❌ User not found for order {order.id}")
            return False
            
        if not meal_plan:
            print(f"  ❌ Meal plan not found for order {order.id}")
            return False
        
        # Check if subscription already exists
        existing_subscription = Subscription.query.filter_by(
            user_id=order.user_id,
            meal_plan_id=order.meal_plan_id,
            order_id=order.id
        ).first()
        
        if existing_subscription:
            print(f"  ✅ Subscription already exists: {existing_subscription.id}")
            return True
        
        # Determine frequency based on amount
        frequency = SubscriptionFrequency.WEEKLY
        if meal_plan.price_monthly and abs(order.amount - float(meal_plan.price_monthly)) < 1:
            frequency = SubscriptionFrequency.MONTHLY
        
        # Create subscription
        subscription = Subscription(
            user_id=order.user_id,
            meal_plan_id=order.meal_plan_id,
            frequency=frequency,
            status=SubscriptionStatus.ACTIVE,
            price=order.amount,
            order_id=order.id,
            start_date=order.created_at,
            current_period_start=order.created_at,
            current_period_end=(
                order.created_at + timedelta(days=7) if frequency == SubscriptionFrequency.WEEKLY 
                else order.created_at + timedelta(days=30)
            )
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        print(f"  ✅ Created subscription {subscription.id} for order {order.id}")
        return True
        
    except IntegrityError as e:
        print(f"  ❌ Database integrity error: {str(e)}")
        db.session.rollback()
        return False
    except Exception as e:
        print(f"  ❌ Error creating subscription: {str(e)}")
        db.session.rollback()
        return False

def fix_all_failed_subscriptions():
    """Fix all failed subscriptions"""
    app = create_app()
    
    with app.app_context():
        failed_orders = find_failed_subscriptions()
        
        if not failed_orders:
            print("No failed subscriptions found!")
            return
        
        print(f"\nAttempting to fix {len(failed_orders)} failed subscriptions...")
        
        success_count = 0
        for order in failed_orders:
            print(f"Fixing order {order.id}...")
            if fix_failed_subscription(order):
                success_count += 1
        
        print(f"\n✅ Successfully fixed {success_count}/{len(failed_orders)} subscriptions")

def check_subscription_integrity():
    """Check the integrity of subscriptions and orders"""
    app = create_app()
    
    with app.app_context():
        print("Checking subscription integrity...")
        
        # Check for subscriptions without orders
        orphaned_subscriptions = db.session.query(Subscription).filter(
            Subscription.order_id.isnot(None),
            ~Subscription.order_id.in_(db.session.query(Order.id))
        ).all()
        
        print(f"Found {len(orphaned_subscriptions)} orphaned subscriptions (subscription exists but order doesn't)")
        
        # Check for orders without subscriptions
        orders_without_subscriptions = db.session.query(Order).filter(
            Order.status == 'confirmed',
            Order.payment_status == 'captured',
            ~Order.id.in_(
                db.session.query(Subscription.order_id).filter(Subscription.order_id.isnot(None))
            )
        ).all()
        
        print(f"Found {len(orders_without_subscriptions)} orders without subscriptions")
        
        # Check for duplicate subscriptions
        duplicate_subscriptions = db.session.query(Subscription).filter(
            Subscription.order_id.isnot(None)
        ).group_by(Subscription.order_id).having(
            db.func.count(Subscription.id) > 1
        ).all()
        
        print(f"Found {len(duplicate_subscriptions)} potential duplicate subscriptions")
        
        return {
            'orphaned_subscriptions': orphaned_subscriptions,
            'orders_without_subscriptions': orders_without_subscriptions,
            'duplicate_subscriptions': duplicate_subscriptions
        }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix failed subscriptions")
    parser.add_argument("--check", action="store_true", help="Check subscription integrity")
    parser.add_argument("--fix", action="store_true", help="Fix failed subscriptions")
    parser.add_argument("--find", action="store_true", help="Find failed subscriptions")
    
    args = parser.parse_args()
    
    if args.check:
        check_subscription_integrity()
    elif args.fix:
        fix_all_failed_subscriptions()
    elif args.find:
        find_failed_subscriptions()
    else:
        print("Please specify an action: --check, --fix, or --find")
        print("Example: python fix_failed_subscriptions.py --check")
        print("Example: python fix_failed_subscriptions.py --fix")
