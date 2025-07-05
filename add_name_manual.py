#!/usr/bin/env python3
import sqlite3
import os

def add_name_column():
    db_path = 'instance/healthyrizz.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if name column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current user table columns: {columns}")
        
        if 'name' in columns:
            print("✅ Name column already exists!")
        else:
            print("�� Adding name column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN name VARCHAR(100)")
            
            print("🔄 Updating existing users...")
            cursor.execute("UPDATE user SET name = username WHERE name IS NULL")
            updated_count = cursor.rowcount
            print(f"✅ Updated {updated_count} users!")
            
            conn.commit()
            print("✅ Migration completed successfully!")
        
        # Verify the changes
        print("\n�� Sample users after update:")
        cursor.execute("SELECT id, username, name, email FROM user LIMIT 5")
        users = cursor.fetchall()
        for user in users:
            print(f"  - ID: {user[0]}, Username: '{user[1]}', Name: '{user[2]}', Email: '{user[3]}'")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_name_column()
