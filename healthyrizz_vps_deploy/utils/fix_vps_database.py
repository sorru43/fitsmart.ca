import os
import sys
import argparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def main():
    """Add missing columns to the database schema on VPS."""
    print("Starting database schema fix...")
    
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Fix database schema for HealthyRizz VPS deployment')
    parser.add_argument('--host', default=os.environ.get('PGHOST', 'localhost'), help='Database host')
    parser.add_argument('--port', default=os.environ.get('PGPORT', '5432'), help='Database port')
    parser.add_argument('--dbname', default=os.environ.get('PGDATABASE'), help='Database name')
    parser.add_argument('--user', default=os.environ.get('PGUSER'), help='Database user')
    parser.add_argument('--password', default=os.environ.get('PGPASSWORD'), help='Database password')
    
    args = parser.parse_args()
    
    # Get database connection details from arguments or environment variables
    db_host = args.host
    db_name = args.dbname
    db_user = args.user
    db_password = args.password
    db_port = args.port
    
    # Verify we have the required parameters
    if not all([db_name, db_user, db_password]):
        print("Error: Database name, user, and password are required.")
        print("Please provide them as command line arguments:")
        print("python fix_vps_database.py --dbname=yourdbname --user=youruser --password=yourpassword")
        sys.exit(1)
    
    # Connect to the database
    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print(f"Connected to database: {db_name}")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
    
    # Check if the user table exists
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user')")
    user_table_exists = cursor.fetchone()[0]
    
    if not user_table_exists:
        print("Error: User table doesn't exist. Database might not be initialized.")
        sys.exit(1)
    
    # Check if username column exists and add it if missing
    try:
        cursor.execute("SELECT username FROM \"user\" LIMIT 1")
        print("Username column already exists.")
    except psycopg2.errors.UndefinedColumn:
        print("Adding username column to user table...")
        try:
            # Add username column and populate it from email field
            cursor.execute('ALTER TABLE "user" ADD COLUMN username VARCHAR(64)')
            cursor.execute('UPDATE "user" SET username = email')
            cursor.execute('ALTER TABLE "user" ALTER COLUMN username SET NOT NULL')
            print("Username column added successfully.")
        except Exception as e:
            print(f"Error adding username column: {e}")
            sys.exit(1)
    
    # Check if created_at column exists and add it if missing
    try:
        cursor.execute("SELECT created_at FROM \"user\" LIMIT 1")
        print("created_at column already exists.")
    except psycopg2.errors.UndefinedColumn:
        print("Adding created_at column to user table...")
        try:
            # Add created_at column with current timestamp
            cursor.execute('ALTER TABLE "user" ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP')
            print("created_at column added successfully.")
        except Exception as e:
            print(f"Error adding created_at column: {e}")
    
    # Close connection
    cursor.close()
    conn.close()
    
    print("Database schema fix completed successfully!")

if __name__ == "__main__":
    main()
