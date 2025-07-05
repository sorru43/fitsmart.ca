#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add Sample States, Cities, and Areas for Cascading Dropdown
This script creates sample location data for the checkout page cascading dropdowns.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from database.models import State, City, Area

def add_sample_locations():
    """Add sample states, cities, and areas for cascading dropdowns"""
    print("🔧 Adding Sample States, Cities, and Areas...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Clear existing data
            print("🗑️ Clearing existing location data...")
            Area.query.delete()
            City.query.delete()
            State.query.delete()
            db.session.commit()
            
            # Sample location data
            location_data = {
                'Punjab': {
                    'Ludhiana': ['Civil Lines', 'Model Town', 'Sarabha Nagar', 'BRS Nagar', 'Pakhowal Road'],
                    'Chandigarh': ['Sector 1', 'Sector 2', 'Sector 3', 'Sector 4', 'Sector 5'],
                    'Amritsar': ['Golden Temple Area', 'Lawrence Road', 'Mall Road', 'Ranjit Avenue'],
                    'Jalandhar': ['Model Town', 'Adarsh Nagar', 'Civil Lines', 'Nakodar Road'],
                    'Patiala': ['Leela Bhawan', 'Urban Estate', 'Civil Lines', 'Rajpura Road']
                },
                'Haryana': {
                    'Gurgaon': ['Cyber City', 'DLF Phase 1', 'DLF Phase 2', 'Sector 29', 'Sector 30'],
                    'Faridabad': ['Sector 15', 'Sector 16', 'Sector 17', 'NIT', 'Ballabhgarh'],
                    'Panipat': ['Model Town', 'Civil Lines', 'Industrial Area', 'Gohana Road']
                },
                'Delhi': {
                    'New Delhi': ['Connaught Place', 'Khan Market', 'Lajpat Nagar', 'Greater Kailash', 'Hauz Khas'],
                    'Delhi': ['Dwarka', 'Rohini', 'Pitampura', 'Janakpuri', 'Vikaspuri']
                },
                'Maharashtra': {
                    'Mumbai': ['Bandra West', 'Andheri West', 'Juhu', 'Worli', 'Colaba'],
                    'Pune': ['Koregaon Park', 'Kalyani Nagar', 'Viman Nagar', 'Baner', 'Aundh']
                },
                'Karnataka': {
                    'Bangalore': ['Indiranagar', 'Koramangala', 'Whitefield', 'Electronic City', 'Marathahalli'],
                    'Mysore': ['Vijayanagar', 'Hebbal', 'Kuvempunagar', 'Saraswathipuram']
                }
            }
            
            # Create states, cities, and areas
            for state_name, cities in location_data.items():
                print(f"📍 Creating state: {state_name}")
                state = State(name=state_name)
                db.session.add(state)
                db.session.flush()  # Get the state ID
                
                for city_name, areas in cities.items():
                    print(f"  🏙️ Creating city: {city_name}")
                    city = City(name=city_name, state_id=state.id)
                    db.session.add(city)
                    db.session.flush()  # Get the city ID
                    
                    for area_name in areas:
                        print(f"    🏘️ Creating area: {area_name}")
                        area = Area(name=area_name, city_id=city.id)
                        db.session.add(area)
            
            db.session.commit()
            print(f"✅ Successfully added location data!")
            
            # Show summary
            print("\n📋 Location Summary:")
            print(f"  • States: {State.query.count()}")
            print(f"  • Cities: {City.query.count()}")
            print(f"  • Areas: {Area.query.count()}")
            
            print("\n📍 Available States:")
            for state in State.query.order_by(State.name).all():
                print(f"  • {state.name}")
                for city in state.cities:
                    print(f"    - {city.name}")
                    for area in city.areas:
                        print(f"      * {area.name}")
            
        except Exception as e:
            print(f"❌ Error adding locations: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_sample_locations() 