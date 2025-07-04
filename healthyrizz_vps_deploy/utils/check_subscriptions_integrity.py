from app import create_app, db
from models import Subscription, User, MealPlan

app = create_app()

def check_subscriptions_integrity():
    with app.app_context():
        print("\n=== Checking Subscriptions Integrity ===")
        subscriptions = Subscription.query.all()
        print(f"Total subscriptions: {len(subscriptions)}")
        for s in subscriptions:
            user = User.query.get(s.user_id)
            plan = MealPlan.query.get(s.meal_plan_id)
            user_email = user.email if user else 'MISSING'
            plan_name = plan.name if plan else 'MISSING'
            print(f"ID: {s.id}, User: {user_email}, Plan: {plan_name}, Status: {s.status}")
            if not user or not plan:
                print(f"  -> WARNING: Subscription {s.id} has missing references!")

if __name__ == '__main__':
    check_subscriptions_integrity() 