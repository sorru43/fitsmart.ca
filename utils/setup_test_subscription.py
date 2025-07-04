from app import create_app
from database.models import Subscription, SubscriptionStatus, User, MealPlan, db
from datetime import datetime, date, timedelta

def setup_test_subscription():
    """Set up a test subscription with all required fields"""
    app = create_app()
    with app.app_context():
        try:
            # Get or create a test user by username or email
            user = User.query.filter((User.email=='test@example.com') | (User.username=='testuser')).first()
            if not user:
                user = User(
                    username='testuser',
                    name='Test User',
                    email='test@example.com',
                    phone='1234567890',
                    is_active=True
                )
                db.session.add(user)
                db.session.commit()

            # Get or create a meal plan
            meal_plan = MealPlan.query.first()
            if not meal_plan:
                meal_plan = MealPlan(
                    name='Test Plan',
                    description='Test meal plan',
                    price=99.99
                )
                db.session.add(meal_plan)
                db.session.commit()

            # Check for existing subscription for this user and meal plan
            subscription = Subscription.query.filter_by(user_id=user.id, meal_plan_id=meal_plan.id).first()
            if not subscription:
                # Create a new subscription with all required fields
                subscription = Subscription(
                    user_id=user.id,
                    meal_plan_id=meal_plan.id,
                    status=SubscriptionStatus.ACTIVE,
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=30),
                    delivery_days=[0, 2, 4],  # Monday, Wednesday, Friday
                    delivery_address='123 Test Street',
                    delivery_city='Test City',
                    delivery_province='Test Province',
                    delivery_postal_code='12345'
                )
                db.session.add(subscription)
                db.session.commit()
                print(f"Created test subscription #{subscription.id}")
            else:
                print(f"Test subscription already exists: #{subscription.id}")

            print(f"User: {user.name} ({user.email})")
            print(f"Meal Plan: {meal_plan.name}")
            print(f"Delivery Days: {subscription.delivery_days}")
            print(f"Address: {subscription.delivery_address}")
            print(f"City: {subscription.delivery_city}")
            print(f"Province: {subscription.delivery_province}")
            print(f"Postal Code: {subscription.delivery_postal_code}")

        except Exception as e:
            print(f"Error setting up test subscription: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    setup_test_subscription() 