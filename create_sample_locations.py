
# Sample Delivery Locations for Testing
# Run this in your Flask shell or create a script

from app import create_app, db
from database.models import DeliveryLocation

app = create_app()

with app.app_context():
    # Clear existing locations
    DeliveryLocation.query.delete()
    
    # Create sample locations
    locations = [
        {'city': 'Mumbai', 'province': 'MH', 'is_active': True},
        {'city': 'Delhi', 'province': 'DL', 'is_active': True},
        {'city': 'Bangalore', 'province': 'KA', 'is_active': True},
        {'city': 'Hyderabad', 'province': 'TS', 'is_active': True},
        {'city': 'Chennai', 'province': 'TN', 'is_active': True},
        {'city': 'Kolkata', 'province': 'WB', 'is_active': True},
        {'city': 'Pune', 'province': 'MH', 'is_active': True},
        {'city': 'Ahmedabad', 'province': 'GJ', 'is_active': True},
        {'city': 'Jaipur', 'province': 'RJ', 'is_active': True},
        {'city': 'Lucknow', 'province': 'UP', 'is_active': True}
    ]
    
    for loc_data in locations:
        location = DeliveryLocation(**loc_data)
        db.session.add(location)
    
    db.session.commit()
    print("✅ Sample delivery locations created!")
