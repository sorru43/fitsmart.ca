#!/usr/bin/env python3
"""
Test script for holiday management system
"""
from app import create_app
from database.models import Holiday
from datetime import datetime, timedelta

def test_holiday_system():
    """Test the holiday management system"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Testing Holiday Management System...")
        
        # Test 1: Check current holiday
        current_holiday = Holiday.get_current_holiday()
        if current_holiday:
            print(f"✅ Current holiday: {current_holiday.name}")
            print(f"   Description: {current_holiday.description}")
            print(f"   Duration: {current_holiday.start_date} to {current_holiday.end_date}")
            print(f"   Days remaining: {current_holiday.days_remaining}")
            print(f"   Protect meals: {current_holiday.protect_meals}")
            print(f"   Show popup: {current_holiday.show_popup}")
            print(f"   Popup options: {current_holiday.get_popup_options()}")
        else:
            print("ℹ️ No current holiday active")
        
        # Test 2: List all holidays
        all_holidays = Holiday.query.all()
        print(f"\n📅 Total holidays: {len(all_holidays)}")
        
        for holiday in all_holidays:
            status = "Active" if holiday.is_current else "Inactive"
            print(f"   - {holiday.name} ({status})")
        
        # Test 3: Check upcoming holidays
        upcoming = Holiday.get_upcoming_holidays()
        print(f"\n🔮 Upcoming holidays: {len(upcoming)}")
        
        for holiday in upcoming:
            days_until = (holiday.start_date - datetime.now().date()).days
            print(f"   - {holiday.name} (in {days_until} days)")
        
        print("\n✅ Holiday system test completed!")

if __name__ == "__main__":
    test_holiday_system()
