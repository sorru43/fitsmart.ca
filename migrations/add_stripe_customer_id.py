#!/usr/bin/env python3
"""
Migration script to add stripe_customer_id column to User model
Run this script to add the stripe_customer_id column to the user table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.models import db, User
from sqlalchemy import text

def migrate():
    """Add stripe_customer_id column to user table"""
    app = create_app()
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            print(f"Current user table columns: {columns}")
            
            if 'stripe_customer_id' not in columns:
                print("Adding stripe_customer_id column to user table...")
                # Add stripe_customer_id column
                with db.engine.connect() as conn:
                    # SQLite doesn't support adding UNIQUE constraint in ALTER TABLE
                    # We'll add the column first, then create index
                    conn.execute(text('ALTER TABLE user ADD COLUMN stripe_customer_id VARCHAR(100)'))
                    conn.commit()
                    
                    # Create index for better performance
                    try:
                        conn.execute(text('CREATE INDEX IF NOT EXISTS ix_user_stripe_customer_id ON user(stripe_customer_id)'))
                        conn.commit()
                    except Exception as e:
                        print(f"Note: Could not create index (may already exist): {e}")
                
                print("[SUCCESS] Added stripe_customer_id column to user table")
            else:
                print("[INFO] stripe_customer_id column already exists")
            
            # Verify the column was added
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            if 'stripe_customer_id' in columns:
                print("[SUCCESS] Verification successful: stripe_customer_id column exists")
            else:
                print("[ERROR] Error: Column was not added successfully")
                return False
                
            return True
            
        except Exception as e:
            print(f"[ERROR] Error adding stripe_customer_id column: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("Adding stripe_customer_id column to user table")
    print("=" * 60)
    
    success = migrate()
    
    if success:
        print("\n[SUCCESS] Migration completed successfully!")
        print("You can now restart your server.")
    else:
        print("\n[ERROR] Migration failed. Please check the error messages above.")
        sys.exit(1)

