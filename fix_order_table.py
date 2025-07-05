#!/usr/bin/env python3
"""
Script to fix the Order table structure
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, db

def fix_order_table():
    """Fix the Order table structure"""
    with app.app_context():
        try:
            print("🔧 Fixing Order table structure...")
            
            with db.engine.connect() as conn:
                # Rename total_amount to amount
                print("Renaming total_amount to amount...")
                conn.execute(db.text('ALTER TABLE "order" RENAME COLUMN total_amount TO amount'))
                
                # Remove old customer_id column if it exists
                print("Removing old customer_id column...")
                try:
                    conn.execute(db.text('ALTER TABLE "order" DROP COLUMN customer_id'))
                except:
                    print("customer_id column doesn't exist or can't be dropped")
                
                conn.commit()
            
            print("✅ Order table structure fixed!")
            
            # Verify the changes
            inspector = db.inspect(db.engine)
            order_columns = inspector.get_columns('order')
            print("\n📦 Updated Order Table Columns:")
            for col in order_columns:
                print(f"   - {col['name']}: {col['type']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing order table: {str(e)}")
            return False

if __name__ == '__main__':
    fix_order_table() 