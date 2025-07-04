from app import db
from database.models import BlogPost

def upgrade():
    """Add is_featured column to blog_post table"""
    try:
        # Add is_featured column with default value False
        db.engine.execute('ALTER TABLE blog_post ADD COLUMN is_featured BOOLEAN DEFAULT FALSE')
        print("Successfully added is_featured column to blog_post table")
    except Exception as e:
        print(f"Error adding is_featured column: {str(e)}")

if __name__ == '__main__':
    upgrade() 