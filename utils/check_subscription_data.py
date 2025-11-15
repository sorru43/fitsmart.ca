from app import create_app, db
from database.models import Subscription, User, MealPlan

app = create_app()

def check_subscription_data():
    with app.app_context():
        print("\n=== Full Subscription Data ===")
        subscriptions = Subscription.query.all()
        print(f"Total subscriptions: {len(subscriptions)}")
        for s in subscriptions:
            user = User.query.get(s.user_id)
            plan = MealPlan.query.get(s.meal_plan_id)
            print(f"ID: {s.id}")
            print(f"  User: {user.email if user else 'MISSING'}")
            print(f"  Plan: {plan.name if plan else 'MISSING'}")
            print(f"  Status: {s.status}")
            print(f"  Frequency: {s.frequency}")
            print(f"  Price: ${s.price}")
            print(f"  Current Period End: {s.current_period_end}")
            print(f"  Cancel At Period End: {s.cancel_at_period_end}")
            print(f"  Stripe Subscription ID: {s.stripe_subscription_id or 'None'}")
            print("---")

if __name__ == '__main__':
    check_subscription_data() 