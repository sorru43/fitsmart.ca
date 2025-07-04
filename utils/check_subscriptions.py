from app import create_app
from models import Subscription, SubscriptionStatus, User, MealPlan
from datetime import datetime, date

def check_all_subscriptions():
    """Print all subscriptions in the database with all relevant fields."""
    app = create_app()
    with app.app_context():
        try:
            all_subs = Subscription.query.all()
            print(f"\nTotal subscriptions in database: {len(all_subs)}\n")
            for sub in all_subs:
                user = User.query.get(sub.user_id)
                meal_plan = MealPlan.query.get(sub.meal_plan_id)
                print(f"{'='*50}")
                print(f"Subscription #{sub.id}")
                print(f"User: {user.name if user else 'N/A'} ({user.email if user else 'N/A'})")
                print(f"Meal Plan: {meal_plan.name if meal_plan else 'N/A'}")
                print(f"Status: {sub.status}")
                print(f"Start Date: {sub.start_date}")
                print(f"End Date: {sub.end_date}")
                print(f"Delivery Days: {sub.delivery_days}")
                print(f"Address: {getattr(sub, 'delivery_address', None)}")
                print(f"City: {getattr(sub, 'delivery_city', None)}")
                print(f"Province: {getattr(sub, 'delivery_province', None)}")
                print(f"Postal Code: {getattr(sub, 'delivery_postal_code', None)}")
                print(f"Created At: {sub.created_at}")
                print(f"{'='*50}\n")
        except Exception as e:
            print(f"Error checking subscriptions: {str(e)}")

if __name__ == "__main__":
    check_all_subscriptions() 