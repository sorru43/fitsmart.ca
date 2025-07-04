#!/usr/bin/env python3
"""
Script to debug banner activation logic
"""
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database.models import Banner
from extensions import db

def debug_banner():
    app = create_app()
    
    with app.app_context():
        try:
            # Get all banners
            banners = Banner.query.all()
            print(f"Found {len(banners)} banners")
            
            for banner in banners:
                print(f"\n🔍 Debugging Banner ID: {banner.id}")
                print(f"   Message: {banner.message}")
                print(f"   Is Active: {banner.is_active}")
                print(f"   Start Date: {banner.start_date}")
                print(f"   End Date: {banner.end_date}")
                print(f"   Current Time: {datetime.now()}")
                print(f"   Start Date <= Now: {banner.start_date <= datetime.now()}")
                print(f"   End Date >= Now: {banner.end_date >= datetime.now() if banner.end_date else 'No end date'}")
                print(f"   Is Expired: {banner.is_expired}")
                
                # Test the query manually
                now = datetime.now()
                query = db.session.query(Banner).filter(
                    Banner.is_active == True,
                    Banner.start_date <= now,
                    (Banner.end_date == None) | (Banner.end_date >= now)
                ).order_by(Banner.id.desc())
                
                print(f"   SQL Query: {query}")
                result = query.first()
                print(f"   Query Result: {result.message if result else 'None'}")
                
            # Test the get_active_banner method
            print(f"\n🎯 Testing get_active_banner() method:")
            active_banner = Banner.get_active_banner()
            if active_banner:
                print(f"   ✅ Active banner found: {active_banner.message}")
            else:
                print(f"   ❌ No active banner found")
                
        except Exception as e:
            print(f"❌ Error debugging banner: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_banner() 