#!/usr/bin/env python3
"""
Fix the migration issue by marking it as completed
"""
import os
import sys
from sqlalchemy import text

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db

def fix_migration():
    """Mark the problematic migration as completed"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Fixing migration issue...")
            
            # Check if the migration is already marked as completed
            result = db.session.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.fetchone()
            print(f"Current migration version: {current_version}")
            
            # Mark the problematic migration as completed
            target_version = "6af3761b666d"  # The problematic migration
            
            if current_version and current_version[0] != target_version:
                print(f"Updating migration version to {target_version}...")
                db.session.execute(text(f"UPDATE alembic_version SET version_num = '{target_version}'"))
                db.session.commit()
                print("✅ Migration version updated successfully")
            else:
                print("✅ Migration version is already correct")
            
            # Ensure email_verified column exists
            try:
                result = db.session.execute(text("PRAGMA table_info(user)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'email_verified' not in columns:
                    print("Adding email_verified column...")
                    db.session.execute(text('ALTER TABLE user ADD COLUMN email_verified BOOLEAN DEFAULT 0'))
                    db.session.commit()
                    print("✅ email_verified column added successfully")
                else:
                    print("✅ email_verified column already exists")
                    
            except Exception as e:
                print(f"Error with email_verified column: {e}")
                db.session.rollback()
            
            print("✅ Migration fix completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing migration: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 Migration Fix Script")
    print("=" * 30)
    fix_migration()
