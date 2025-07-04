#!/usr/bin/env python3
"""
Script to recreate the Order table with correct structure
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db

def recreate_order_table():
    """Recreate the Order table with correct structure"""
    with app.app_context():
        try:
            print("🔧 Recreating Order table with correct structure...")
            
            with db.engine.connect() as conn:
                # Drop the old order table
                print("Dropping old order table...")
                conn.execute(db.text('DROP TABLE IF EXISTS "order"'))
                
                # Create new order table with correct structure
                print("Creating new order table...")
                conn.execute(db.text('''
                    CREATE TABLE "order" (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        meal_plan_id INTEGER NOT NULL,
                        amount FLOAT NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        payment_status VARCHAR(20) DEFAULT 'pending',
                        payment_id VARCHAR(100),
                        order_id VARCHAR(100),
                        delivery_address TEXT,
                        delivery_instructions TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user (id),
                        FOREIGN KEY (meal_plan_id) REFERENCES meal_plan (id)
                    )
                '''))
                
                conn.commit()
            
            print("✅ Order table recreated successfully!")
            
            # Verify the changes
            inspector = db.inspect(db.engine)
            order_columns = inspector.get_columns('order')
            print("\n📦 New Order Table Columns:")
            for col in order_columns:
                print(f"   - {col['name']}: {col['type']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error recreating order table: {str(e)}")
            return False

if __name__ == '__main__':
    recreate_order_table() 