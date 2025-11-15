from app import create_app, db
from database.models import User, MealPlan, Subscription, SubscriptionStatus, SubscriptionFrequency
from datetime import datetime, timedelta

def create_test_subscription():
    app = create_app()
    with app.app_context():
        # Check for existing user by email or username
        test_user = User.query.filter((User.email=='test@example.com') | (User.username=='testuser')).first()
        if not test_user:
            test_user = User(
                username='testuser',
                name='Test User',
                email='test@example.com',
                phone='1234567890',
                is_active=True
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()

        # Create a test meal plan if it doesn't exist
        test_plan = MealPlan.query.filter_by(name='Test Plan').first()
        if not test_plan:
            test_plan = MealPlan(
                name='Test Plan',
                description='Test meal plan',
                price=99.99,
                is_active=True
            )
            db.session.add(test_plan)
            db.session.commit()

        # Check for existing subscription
        test_subscription = Subscription.query.filter_by(user_id=test_user.id, meal_plan_id=test_plan.id).first()
        if not test_subscription:
            test_subscription = Subscription(
                user_id=test_user.id,
                meal_plan_id=test_plan.id,
                status=SubscriptionStatus.ACTIVE,
                frequency=SubscriptionFrequency.WEEKLY,
                price=99.99,
                start_date=datetime.now(),
                current_period_start=datetime.now(),
                current_period_end=datetime.now() + timedelta(days=30)
            )
            try:
                db.session.add(test_subscription)
                db.session.commit()
                print("Test subscription created successfully!")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating test subscription: {str(e)}")
        else:
            print("Test subscription already exists.")

if __name__ == '__main__':
    create_test_subscription() 