from app import create_app, db
from sqlalchemy import text

def check_table_structure():
    app = create_app()
    with app.app_context():
        try:
            # Get all table names
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = result.fetchall()
            
            print("\nDatabase tables:")
            for table in tables:
                table_name = table[0]
                print(f"\nTable: {table_name}")
                
                # Get columns for this table
                result = db.session.execute(text(f"PRAGMA table_info({table_name});"))
                columns = result.fetchall()
                
                for column in columns:
                    print(f"  - {column[1]}: {column[2]}")
                
        except Exception as e:
            print(f"Error checking table structure: {str(e)}")

if __name__ == "__main__":
    check_table_structure() 