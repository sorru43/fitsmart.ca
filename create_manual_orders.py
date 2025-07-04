#!/usr/bin/env python3
"""
Manual order creation using SQL to bypass model issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database.models import User, MealPlan
from sqlalchemy import text
from datetime import datetime, timedelta

def create_manual_orders():
    """Create orders manually using SQL"""
    print("🛠️ Creating orders manually using SQL...")
    
    with app.app_context():
        try:
            # Get admin user and meal plans
            admin_user = User.query.filter_by(email='admin@healthyrizz.in').first()
            if not admin_user:
                print("❌ Admin user not found")
                return False
            
            meal_plans = MealPlan.query.all()
            if not meal_plans:
                print("❌ No meal plans found")
                return False
            
            print(f"✅ Found admin user: {admin_user.email} (ID: {admin_user.id})")
            print(f"✅ Found {len(meal_plans)} meal plans")
            
            # Create orders using direct SQL
            orders_created = 0
            for i in range(5):
                meal_plan = meal_plans[i % len(meal_plans)]
                days_ago = (i + 1) * 7
                amount = float(meal_plan.price_weekly) + (i * 100)
                created_date = datetime.now() - timedelta(days=days_ago)
                
                # Insert order using SQL
                sql = text("""
                    INSERT INTO `order` (
                        user_id, meal_plan_id, amount, status, payment_status, 
                        payment_id, order_id, delivery_address, created_at, updated_at
                    ) VALUES (
                        :user_id, :meal_plan_id, :amount, :status, :payment_status,
                        :payment_id, :order_id, :delivery_address, :created_at, :updated_at
                    )
                """)
                
                db.session.execute(sql, {
                    'user_id': admin_user.id,
                    'meal_plan_id': meal_plan.id,
                    'amount': amount,
                    'status': 'confirmed',
                    'payment_status': 'completed',
                    'payment_id': f'pay_manual_{i+1:03d}',
                    'order_id': f'order_manual_{i+1:03d}',
                    'delivery_address': f'{admin_user.address}, {admin_user.city}',
                    'created_at': created_date,
                    'updated_at': created_date
                })
                
                orders_created += 1
                print(f"   - Created order #{i+1}: ₹{amount} ({meal_plan.name})")
            
            # Commit all changes
            db.session.commit()
            print(f"✅ Successfully created {orders_created} orders using SQL")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating orders: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return False

def verify_orders():
    """Verify the created orders"""
    print("\n🔍 Verifying created orders...")
    
    with app.app_context():
        try:
            # Count orders for admin user
            sql = text("SELECT COUNT(*) FROM `order` WHERE user_id = :user_id")
            result = db.session.execute(sql, {'user_id': 1})
            order_count = result.scalar()
            
            print(f"📊 Total orders for admin user: {order_count}")
            
            # Get total amount
            sql = text("SELECT SUM(amount) FROM `order` WHERE user_id = :user_id AND payment_status = 'completed'")
            result = db.session.execute(sql, {'user_id': 1})
            total_amount = result.scalar() or 0
            
            print(f"💰 Total spent: ₹{total_amount}")
            
            # Get recent orders
            sql = text("""
                SELECT o.id, o.amount, o.payment_status, o.created_at, m.name as meal_plan_name
                FROM `order` o 
                JOIN meal_plan m ON o.meal_plan_id = m.id 
                WHERE o.user_id = :user_id 
                ORDER BY o.created_at DESC 
                LIMIT 3
            """)
            result = db.session.execute(sql, {'user_id': 1})
            recent_orders = result.fetchall()
            
            if recent_orders:
                print(f"\n📋 Recent orders:")
                for order in recent_orders:
                    print(f"   - Order #{order.id}: ₹{order.amount} ({order.payment_status}) - {order.meal_plan_name}")
            
            return order_count > 0
            
        except Exception as e:
            print(f"❌ Error verifying orders: {str(e)}")
            return False

if __name__ == "__main__":
    print("🚀 Manual Order Creator")
    print("=" * 50)
    
    if create_manual_orders():
        if verify_orders():
            print("\n✅ Manual order creation successful!")
            print("Now check the profile page to see the orders.")
        else:
            print("\n⚠️ Orders created but verification failed")
    else:
        print("\n❌ Failed to create orders") 