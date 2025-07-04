"""
Database check and repair script for HealthyRizz application.
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

def main():
    """Check database connection and tables."""
    print("Checking database connection and tables...")
    
    # Get database URL from environment or use default for CloudPanel
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Try to construct from components
        db_user = os.environ.get('PGUSER', 'cp_healthyrizz_user')
        db_password = os.environ.get('PGPASSWORD', '')
        db_host = os.environ.get('PGHOST', 'localhost')
        db_port = os.environ.get('PGPORT', '5432')
        db_name = os.environ.get('PGDATABASE', 'cp_healthyrizz_db')
        
        if not db_password:
            print("Database password not found in environment variables.")
            db_password = input("Please enter the database password: ")
        
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        # Create engine without pooling for diagnostics
        engine = create_engine(
            database_url,
            isolation_level="AUTOCOMMIT",  # Prevent transaction issues
            pool_pre_ping=True,
            echo=False
        )
        
        # Test connection
        with engine.connect() as conn:
            print("✅ Successfully connected to the database.")
            
            # Check tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"Found {len(tables)} tables: {', '.join(tables)}")
            
            # Check if meal_plan table exists
            if 'meal_plan' in tables:
                print("✅ meal_plan table exists.")
                
                # Check if we can query meal_plan table
                try:
                    result = conn.execute(text("SELECT COUNT(*) FROM meal_plan"))
                    count = result.scalar()
                    print(f"✅ Successfully queried meal_plan table. Found {count} records.")
                except SQLAlchemyError as e:
                    print(f"❌ Error querying meal_plan table: {e}")
                    
                    # Try to fix the table if needed
                    print("Attempting to verify meal_plan table structure...")
                    try:
                        # Show table structure
                        table_info = conn.execute(text(
                            "SELECT column_name, data_type FROM information_schema.columns "
                            "WHERE table_name = 'meal_plan'"
                        )).fetchall()
                        print("meal_plan table structure:")
                        for column, dtype in table_info:
                            print(f"  - {column} ({dtype})")
                    except SQLAlchemyError as e:
                        print(f"Error getting table structure: {e}")
            else:
                print("❌ meal_plan table does not exist!")
                
            # Check for any active transactions that might be causing problems
            try:
                active_txns = conn.execute(text(
                    "SELECT pid, usename, application_name, state, backend_xmin, backend_xid "
                    "FROM pg_stat_activity WHERE state = 'idle in transaction'"
                )).fetchall()
                
                if active_txns:
                    print(f"Found {len(active_txns)} idle transactions that might be causing problems:")
                    for txn in active_txns:
                        print(f"  - Process ID: {txn[0]}, User: {txn[1]}, App: {txn[2]}, State: {txn[3]}")
                    
                    choice = input("Would you like to terminate these transactions? (y/n): ")
                    if choice.lower() == 'y':
                        for txn in active_txns:
                            conn.execute(text(f"SELECT pg_terminate_backend({txn[0]})"))
                        print("Terminated idle transactions.")
                else:
                    print("✅ No idle transactions found.")
            except SQLAlchemyError as e:
                print(f"Error checking transactions: {e}")
    
    except SQLAlchemyError as e:
        print(f"❌ Database connection error: {e}")
        return 1
    
    print("\n✅ Database check completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
