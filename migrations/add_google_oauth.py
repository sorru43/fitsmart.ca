#!/usr/bin/env python3
"""
Migration script to add Google OAuth support to User model
Run this script to add the google_id column to the user table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database.models import db, User
from sqlalchemy import text

def migrate():
    """Add google_id column to user table"""
    app = create_app()
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'google_id' not in columns:
                # Add google_id column
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE user ADD COLUMN google_id VARCHAR(100)'))
                    conn.execute(text('CREATE INDEX IF NOT EXISTS ix_user_google_id ON user(google_id)'))
                    conn.commit()
                print("Added google_id column to user table")
            else:
                print("google_id column already exists")
            
            # Make username nullable if not already (SQLite doesn't support ALTER COLUMN, skip for SQLite)
            if 'sqlite' not in str(db.engine.url).lower():
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text('ALTER TABLE user ALTER COLUMN username DROP NOT NULL'))
                        conn.commit()
                    print("Made username column nullable")
                except Exception as e:
                    if 'NOT NULL' in str(e) or 'cannot' in str(e).lower():
                        print("Username column is already nullable or cannot be changed")
                    else:
                        raise
            
            # Make password_hash nullable if not already (SQLite doesn't support ALTER COLUMN, skip for SQLite)
            if 'sqlite' not in str(db.engine.url).lower():
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text('ALTER TABLE user ALTER COLUMN password_hash DROP NOT NULL'))
                        conn.commit()
                    print("Made password_hash column nullable")
                except Exception as e:
                    if 'NOT NULL' in str(e) or 'cannot' in str(e).lower():
                        print("password_hash column is already nullable or cannot be changed")
                    else:
                        raise
            
            print("Migration completed successfully")
            
        except Exception as e:
            print(f"Migration error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrate()

