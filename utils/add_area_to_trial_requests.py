#!/usr/bin/env python3
"""
Migration script to add area field to TrialRequest table and update province field
"""

import sys
import os
from sqlalchemy import text

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app, db
    from database.models import TrialRequest
    from flask import current_app

    def migrate_trial_requests():
        """Add area field to TrialRequest table and update province field"""
        with app.app_context():
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('trial_request')]
            print(f"Existing columns: {columns}")
            # Add area column if not exists
            if 'area' not in columns:
                try:
                    db.session.execute(text("ALTER TABLE trial_request ADD COLUMN area VARCHAR(100) NOT NULL DEFAULT 'Unknown'"))
                    db.session.commit()
                    print("✅ Added area column to trial_request table")
                except Exception as e:
                    print(f"❌ Failed to add area column: {e}")
            else:
                print("ℹ️  area column already exists")
            # Try to alter province column size if needed
            province_col = next((col for col in inspector.get_columns('trial_request') if col['name'] == 'province'), None)
            if province_col and str(province_col['type']) == 'VARCHAR(2)':
                try:
                    # SQLite does not support ALTER COLUMN, so we need to recreate the table if using SQLite
                    if db.engine.url.get_backend_name() == 'sqlite':
                        print("⚠️  SQLite detected: cannot alter column type directly. Manual migration needed if you want to change province column size.")
                    else:
                        db.session.execute(text("ALTER TABLE trial_request ALTER COLUMN province TYPE VARCHAR(100)"))
                        db.session.commit()
                        print("✅ Altered province column to VARCHAR(100)")
                except Exception as e:
                    print(f"❌ Failed to alter province column: {e}")
            else:
                print("ℹ️  province column is already correct or not found")

    if __name__ == "__main__":
        migrate_trial_requests()
except Exception as e:
    print(f"❌ Import error: {e}") 