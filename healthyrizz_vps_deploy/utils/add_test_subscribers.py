from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Configure database - using the same configuration as your main app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthyrizz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define Newsletter model
class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

def add_test_subscribers():
    test_subscribers = [
        {
            'email': 'alex.morgan@example.com',
            'created_at': datetime(2024, 4, 1, 9, 30)
        },
        {
            'email': 'jessica.parker@example.com',
            'created_at': datetime(2024, 4, 2, 14, 15)
        },
        {
            'email': 'thomas.lee@example.com',
            'created_at': datetime(2024, 4, 3, 11, 45)
        },
        {
            'email': 'maria.garcia@example.com',
            'created_at': datetime(2024, 4, 4, 16, 20)
        },
        {
            'email': 'james.wilson@example.com',
            'created_at': datetime(2024, 4, 5, 10, 30)
        },
        {
            'email': 'sophia.kim@example.com',
            'created_at': datetime(2024, 4, 6, 13, 45)
        },
        {
            'email': 'daniel.patel@example.com',
            'created_at': datetime(2024, 4, 7, 15, 10)
        },
        {
            'email': 'olivia.martinez@example.com',
            'created_at': datetime(2024, 4, 8, 10, 0)
        }
    ]

    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Clear existing subscribers (optional - comment out if you want to keep existing ones)
        # Newsletter.query.delete()
        # db.session.commit()
        
        for subscriber_data in test_subscribers:
            try:
                # Check if subscriber already exists
                existing = Newsletter.query.filter_by(email=subscriber_data['email']).first()
                if not existing:
                    subscriber = Newsletter(
                        email=subscriber_data['email'],
                        created_at=subscriber_data['created_at']
                    )
                    db.session.add(subscriber)
                    print(f"Added subscriber: {subscriber_data['email']}")
                else:
                    print(f"Subscriber already exists: {subscriber_data['email']}")
            except Exception as e:
                print(f"Error adding subscriber {subscriber_data['email']}: {str(e)}")
                continue

        try:
            db.session.commit()
            print("\nSuccessfully added test subscribers!")
        except Exception as e:
            db.session.rollback()
            print(f"\nError committing changes: {str(e)}")

if __name__ == '__main__':
    add_test_subscribers() 
