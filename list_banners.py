#!/usr/bin/env python3
"""
Script to list all banners in the database
"""
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database.models import Banner
from extensions import db

def list_banners():
    app = create_app()
    
    with app.app_context():
        try:
            banners = Banner.query.order_by(Banner.created_at.desc()).all()
            
            print(f"📋 Found {len(banners)} banners in database:")
            print("=" * 60)
            
            for i, banner in enumerate(banners, 1):
                print(f"\n{i}. Banner ID: {banner.id}")
                print(f"   Message: {banner.message}")
                print(f"   Link Text: {banner.link_text or 'None'}")
                print(f"   Link URL: {banner.link_url or 'None'}")
                print(f"   Background Color: {banner.background_color}")
                print(f"   Text Color: {banner.text_color}")
                print(f"   Active: {'✅ Yes' if banner.is_active else '❌ No'}")
                print(f"   Start Date: {banner.start_date.strftime('%Y-%m-%d %H:%M')}")
                print(f"   End Date: {banner.end_date.strftime('%Y-%m-%d %H:%M') if banner.end_date else 'No end date'}")
                print(f"   Is Expired: {'✅ Yes' if banner.is_expired else '❌ No'}")
                print(f"   Created: {banner.created_at.strftime('%Y-%m-%d %H:%M')}")
                print("-" * 40)
            
            # Check which banner is currently active
            active_banner = Banner.get_active_banner()
            if active_banner:
                print(f"\n🎯 CURRENTLY ACTIVE BANNER:")
                print(f"   ID: {active_banner.id}")
                print(f"   Message: {active_banner.message}")
                print(f"   This banner should be displayed on the website!")
            else:
                print(f"\n❌ NO ACTIVE BANNER FOUND")
                print(f"   Check if banners are active and within date range")
            
            print(f"\n🌐 To view banners on website:")
            print("1. Go to: http://localhost:5000")
            print("2. Look for banner at the top of the page")
            print("3. If no banner shows, check the criteria above")
            
        except Exception as e:
            print(f"❌ Error listing banners: {e}")

if __name__ == "__main__":
    list_banners() 