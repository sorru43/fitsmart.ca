#!/usr/bin/env python3
"""
Database initialization script for HealthyRizz
This script creates all necessary tables and updates the schema
"""

from app import create_app
from extensions import db
from database.models import User, MealPlan, FAQ, HeroSlide, SiteSetting
import sqlite3
import os

def init_database():
    """Initialize the database with all required tables"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Initializing HealthyRizz database...")
        
        # Drop all tables and recreate them
        print("📊 Creating all database tables...")
        db.create_all()
        
        # Check if we need to update existing tables
        update_meal_plan_table()
        
        print("✅ Database initialization completed!")
        print("\n📋 Available tables:")
        
        # List all tables
        conn = sqlite3.connect('healthyrizz.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        conn.close()

def update_meal_plan_table():
    """Update meal_plan table with missing columns"""
    print("🔄 Updating meal_plan table schema...")
    
    conn = sqlite3.connect('healthyrizz.db')
    cursor = conn.cursor()
    
    # Check if includes_breakfast column exists
    cursor.execute("PRAGMA table_info(meal_plan)")
    columns = [col[1] for col in cursor.fetchall()]
    
    missing_columns = []
    
    # Add missing columns
    if 'includes_breakfast' not in columns:
        missing_columns.append(('includes_breakfast', 'BOOLEAN DEFAULT 1'))
    
    if 'available_for_trial' not in columns:
        missing_columns.append(('available_for_trial', 'BOOLEAN DEFAULT 1'))
    
    if 'price_per_meal_veg' not in columns:
        missing_columns.append(('price_per_meal_veg', 'FLOAT'))
    
    if 'price_per_meal_nonveg' not in columns:
        missing_columns.append(('price_per_meal_nonveg', 'FLOAT'))
    
    if 'price_per_meal_breakfast' not in columns:
        missing_columns.append(('price_per_meal_breakfast', 'FLOAT DEFAULT 199.0'))
    
    if 'is_featured' not in columns:
        missing_columns.append(('is_featured', 'BOOLEAN DEFAULT 0'))
    
    if 'created_at' not in columns:
        missing_columns.append(('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'))
    
    if 'updated_at' not in columns:
        missing_columns.append(('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'))
    
    # Add missing columns
    for col_name, col_def in missing_columns:
        try:
            cursor.execute(f"ALTER TABLE meal_plan ADD COLUMN {col_name} {col_def}")
            print(f"  ✅ Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                print(f"  ❌ Error adding column {col_name}: {e}")
    
    conn.commit()
    conn.close()

def create_sample_data():
    """Create some sample data for testing"""
    app = create_app()
    
    with app.app_context():
        from database.models import User, MealPlan, FAQ, HeroSlide, SiteSetting
        
        print("🎯 Creating sample data...")
        
        # Create admin user
        admin = User.query.filter_by(email='admin@healthyrizz.in').first()
        if not admin:
            admin = User(
                name='Admin',
                email='admin@healthyrizz.in',
                phone='9999999999',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("  ✅ Created admin user (admin@healthyrizz.in / admin123)")
        
        # Create sample meal plan
        meal_plan = MealPlan.query.first()
        if not meal_plan:
            meal_plan = MealPlan(
                name='Healthy Weight Loss Plan',
                description='A balanced meal plan designed for healthy weight loss with nutritious ingredients.',
                calories='1200-1500',
                protein='80-100g',
                carbs='120-150g',
                fat='40-50g',
                price_weekly=2499.0,
                price_monthly=9999.0,
                price_trial=999.0,
                is_vegetarian=True,
                includes_breakfast=True,
                available_for_trial=True,
                tag='weight-loss',
                is_popular=True,
                is_active=True
            )
            db.session.add(meal_plan)
            print("  ✅ Created sample meal plan")
        
        # Create sample FAQ
        faq = FAQ.query.first()
        if not faq:
            faq = FAQ(
                question='How does HealthyRizz meal delivery work?',
                answer='Simply choose your meal plan, customize your preferences, and we deliver fresh, chef-prepared meals to your doorstep. Our nutrition experts ensure each meal meets your dietary goals.',
                category='General',
                order=1,
                is_active=True
            )
            db.session.add(faq)
            print("  ✅ Created sample FAQ")
        
        # Create sample hero slide
        hero = HeroSlide.query.first()
        if not hero:
            hero = HeroSlide(
                title="It's Not An Ordinary Meal Box, It's a Nutrition Box",
                subtitle='Personalized nutrition delivered to your doorstep',
                image_url='/static/images/healthy-meal-bowl.jpg',
                order=1,
                is_active=True
            )
            db.session.add(hero)
            print("  ✅ Created sample hero slide")
        
        # Create sample site settings
        settings = [
            ('company_name', 'HealthyRizz'),
            ('company_tagline', 'Healthy Meal Delivery'),
            ('site_logo', '/static/images/logo white.png'),
            ('hero_subtitle', 'In Supervision Of Nutrition Experts')
        ]
        
        for key, value in settings:
            setting = SiteSetting.query.filter_by(key=key).first()
            if not setting:
                setting = SiteSetting(key=key, value=value)
                db.session.add(setting)
                print(f"  ✅ Created site setting: {key}")
        
        db.session.commit()
        print("✅ Sample data created successfully!")

if __name__ == '__main__':
    init_database()
    create_sample_data()
    print("\n🚀 Database ready! You can now run your Flask application.") 