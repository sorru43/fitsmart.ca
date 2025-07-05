from app import app, db
from database.models import FullWidthSection

with app.app_context():
    db.create_all()
    print("✅ FullWidthSection table created!") 