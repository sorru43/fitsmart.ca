#!/usr/bin/env python3
"""
Add Sample Delivery Locations
Run this script to add sample delivery locations to your database
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from database.models import DeliveryLocation

def add_sample_locations():
    """Add sample delivery locations"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if locations already exist
            existing_count = DeliveryLocation.query.count()
            if existing_count > 0:
                print(f"⚠️ Found {existing_count} existing locations")
                response = input("Do you want to clear existing locations and add new ones? (y/N): ")
                if response.lower() != 'y':
                    print("✅ Keeping existing locations")
                    return
            
            # Clear existing locations if requested
            if existing_count > 0:
                DeliveryLocation.query.delete()
                db.session.commit()
                print("✅ Cleared existing locations")
            
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
                {'city': 'Lucknow', 'province': 'UP', 'is_active': True},
                {'city': 'Ludhiana', 'province': 'PB', 'is_active': True},
                {'city': 'Chandigarh', 'province': 'CH', 'is_active': True},
                {'city': 'Amritsar', 'province': 'PB', 'is_active': True},
                {'city': 'Jalandhar', 'province': 'PB', 'is_active': True},
                {'city': 'Patiala', 'province': 'PB', 'is_active': True}
            ]
            
            for loc_data in locations:
                location = DeliveryLocation(**loc_data)
                db.session.add(location)
            
            db.session.commit()
            print(f"✅ Added {len(locations)} sample delivery locations!")
            
            # Show the locations
            print("\n📋 Available delivery locations:")
            for location in DeliveryLocation.query.filter_by(is_active=True).order_by(DeliveryLocation.city).all():
                print(f"  • {location.city}, {location.province}")
                
        except Exception as e:
            print(f"❌ Error adding locations: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    add_sample_locations()
