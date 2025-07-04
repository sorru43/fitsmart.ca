#!/usr/bin/env python3
"""
Set favicon in database
"""
from app import app
from database.models import SiteSetting
from extensions import db
import os

def set_favicon():
    """Set favicon in database"""
    
    with app.app_context():
        print("🔧 Setting favicon in database...")
        
        # Check existing favicon files
        images_dir = os.path.join(app.root_path, 'static', 'images')
        favicon_files = [f for f in os.listdir(images_dir) if 'favicon' in f.lower()]
        print(f"📁 Available favicon files: {favicon_files}")
        
        if favicon_files:
            # Use the most recent favicon file
            favicon_file = favicon_files[-1]  # Get the last one (most recent)
            favicon_path = f'/static/images/{favicon_file}'
            
            print(f"🎯 Setting favicon to: {favicon_path}")
            
            # Check if setting already exists
            existing = SiteSetting.query.filter_by(key='site_favicon').first()
            if existing:
                existing.value = favicon_path
                print("✅ Updated existing favicon setting")
            else:
                new_setting = SiteSetting(key='site_favicon', value=favicon_path, description='Site favicon')
                db.session.add(new_setting)
                print("✅ Created new favicon setting")
            
            db.session.commit()
            print("💾 Database updated successfully!")
            
            # Verify the setting
            setting = SiteSetting.query.filter_by(key='site_favicon').first()
            if setting:
                print(f"✅ Verified: site_favicon = {setting.value}")
            else:
                print("❌ Setting not found after creation")
        else:
            print("❌ No favicon files found in static/images")

if __name__ == "__main__":
    set_favicon() 