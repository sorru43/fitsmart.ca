#!/usr/bin/env python3
import sqlite3
import os

def fix_database():
    db_path = 'instance/healthyrizz.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add name column if it doesn't exist
        if 'name' not in columns:
            print("Adding name column...")
            cursor.execute("ALTER TABLE user ADD COLUMN name VARCHAR(100)")
            
            # Copy username to name for existing users
            cursor.execute("UPDATE user SET name = username WHERE name IS NULL")
            
            conn.commit()
            print("✅ Name column added successfully!")
        else:
            print("✅ Name column already exists!")
        
        # Verify
        cursor.execute("SELECT id, username, name, email FROM user LIMIT 3")
        users = cursor.fetchall()
        print("\nSample users:")
        for user in users:
            print(f"  - {user[1]} -> Name: {user[2]}")
        
        conn.close()
        print("\n🎉 Database fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_database()
