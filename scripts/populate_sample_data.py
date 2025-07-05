from datetime import datetime, timedelta
from database.models import (
    User, DeliveryLocation, MealPlan, Subscription, 
    SubscriptionStatus, SubscriptionFrequency, Delivery,
    DeliveryStatus
)
from extensions import db
from werkzeug.security import generate_password_hash
import random

def clear_sample_data():
    """Clear existing sample data"""
    try:
        # Delete in reverse order of dependencies
        Delivery.query.delete()
        Subscription.query.delete()
        User.query.filter(User.email.like('sample_%')).delete()
        MealPlan.query.delete()
        DeliveryLocation.query.delete()
        db.session.commit()
        print("Existing sample data cleared successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing sample data: {str(e)}")
        raise e

def create_sample_data():
    """Create sample data for testing"""
    try:
        # Clear existing sample data first
        clear_sample_data()
        
        # Create sample meal plans
        meal_plans = [
            MealPlan(
                name="Weight Loss Plan",
                description="Low calorie meals for weight loss",
                calories="1200-1500",
                protein="80g",
                fat="40g",
                carbs="120g",
                price_weekly=99.99,
                price_monthly=349.99,
                price_trial=14.99,
                is_active=True,
                available_for_trial=True,
                tag="weight_loss",
                is_vegetarian=False,
                is_vegan=False,
                is_keto=False
            ),
            MealPlan(
                name="Muscle Gain Plan",
                description="High protein meals for muscle building",
                calories="2500-3000",
                protein="180g",
                fat="80g",
                carbs="250g",
                price_weekly=119.99,
                price_monthly=399.99,
                price_trial=14.99,
                is_active=True,
                available_for_trial=True,
                tag="muscle_gain",
                is_vegetarian=False,
                is_vegan=False,
                is_keto=False
            ),
            MealPlan(
                name="Vegetarian Plan",
                description="Plant-based meals",
                calories="1800-2200",
                protein="90g",
                fat="60g",
                carbs="200g",
                price_weekly=109.99,
                price_monthly=379.99,
                price_trial=14.99,
                is_active=True,
                available_for_trial=True,
                tag="vegetarian",
                is_vegetarian=True,
                is_vegan=False,
                is_keto=False
            )
        ]
        
        for plan in meal_plans:
            db.session.add(plan)
        db.session.commit()
        
        # Create sample delivery locations
        locations = [
            DeliveryLocation(province="ON", city="Toronto", is_active=True),
            DeliveryLocation(province="ON", city="Ottawa", is_active=True),
            DeliveryLocation(province="ON", city="Hamilton", is_active=True),
            DeliveryLocation(province="BC", city="Vancouver", is_active=True),
            DeliveryLocation(province="BC", city="Victoria", is_active=True),
            DeliveryLocation(province="AB", city="Calgary", is_active=True),
            DeliveryLocation(province="AB", city="Edmonton", is_active=True)
        ]
        
        for location in locations:
            db.session.add(location)
        db.session.commit()
        
        # Create sample users with subscriptions
        users = [
            {
                "username": "sample_john",
                "email": "sample_john@example.com",
                "password": "password123",
                "address": "123 Main St",
                "city": "Toronto",
                "province": "ON",
                "postal_code": "M5V 2H1"
            },
            {
                "username": "sample_jane",
                "email": "sample_jane@example.com",
                "password": "password123",
                "address": "456 Oak Ave",
                "city": "Vancouver",
                "province": "BC",
                "postal_code": "V6B 1A1"
            },
            {
                "username": "sample_bob",
                "email": "sample_bob@example.com",
                "password": "password123",
                "address": "789 Pine Rd",
                "city": "Calgary",
                "province": "AB",
                "postal_code": "T2P 1J9"
            }
        ]
        
        created_users = []
        for user_data in users:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=generate_password_hash(user_data["password"]),
                address=user_data["address"],
                city=user_data["city"],
                province=user_data["province"],
                postal_code=user_data["postal_code"],
                is_active=True
            )
            db.session.add(user)
            created_users.append(user)
        db.session.commit()
        
        # Create subscriptions for users
        today = datetime.now().date()
        for user in created_users:
            # Create active subscription
            subscription = Subscription(
                user_id=user.id,
                meal_plan_id=random.choice(meal_plans).id,
                status=SubscriptionStatus.ACTIVE,
                frequency=random.choice([SubscriptionFrequency.WEEKLY, SubscriptionFrequency.MONTHLY]),
                start_date=today - timedelta(days=random.randint(1, 30)),
                price=random.choice([99.99, 119.99, 109.99]),
                delivery_days="0,1,2,3,4",  # Monday to Friday
                delivery_address=user.address,
                delivery_city=user.city,
                delivery_province=user.province,
                delivery_postal_code=user.postal_code
            )
            db.session.add(subscription)
            db.session.commit()  # Commit subscription before creating deliveries
            
            # Create some deliveries
            for i in range(5):  # Create 5 deliveries for each user
                delivery_date = today - timedelta(days=i)
                status = random.choice(list(DeliveryStatus))
                
                delivery = Delivery(
                    subscription_id=subscription.id,
                    user_id=user.id,
                    delivery_date=delivery_date,
                    status=status,
                    tracking_number=f"TRK{random.randint(100000, 999999)}" if status == DeliveryStatus.DELIVERED else None
                )
                db.session.add(delivery)
            db.session.commit()  # Commit deliveries
        
        # Create some cancelled deliveries
        for user in created_users:
            subscription = Subscription(
                user_id=user.id,
                meal_plan_id=random.choice(meal_plans).id,
                status=SubscriptionStatus.ACTIVE,
                frequency=SubscriptionFrequency.WEEKLY,
                start_date=today - timedelta(days=15),
                price=99.99,
                delivery_days="0,1,2,3,4",  # Monday to Friday
                delivery_address=user.address,
                delivery_city=user.city,
                delivery_province=user.province,
                delivery_postal_code=user.postal_code
            )
            db.session.add(subscription)
            db.session.commit()  # Commit subscription before creating deliveries
            
            # Create cancelled deliveries
            for i in range(3):
                delivery_date = today - timedelta(days=i+1)
                delivery = Delivery(
                    subscription_id=subscription.id,
                    user_id=user.id,
                    delivery_date=delivery_date,
                    status=DeliveryStatus.CANCELLED,
                    notes="Delivery skipped by customer"
                )
                db.session.add(delivery)
            db.session.commit()  # Commit deliveries
        
        print("Sample data created successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample data: {str(e)}")
        raise e

if __name__ == "__main__":
    create_sample_data() 