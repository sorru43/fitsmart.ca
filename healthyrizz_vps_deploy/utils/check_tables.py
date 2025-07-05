from app import create_app, db
from models import Newsletter, Subscription, User, MealPlan
from datetime import datetime
from sqlalchemy import inspect

app = create_app()

def check_tables():
    with app.app_context():
        try:
            # Check if tables exist
            print("\n=== Checking Tables ===")
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print("Available tables:", tables)
            print("Newsletter table exists:", 'newsletter' in tables)
            print("Subscription table exists:", 'subscriptions' in tables)
            
            # Check Newsletter records
            print("\n=== Newsletter Records ===")
            newsletters = Newsletter.query.all()
            print(f"Total newsletter subscribers: {len(newsletters)}")
            for n in newsletters:
                print(f"ID: {n.id}, Email: {n.email}, Created: {n.created_at}")
            
            # Check Subscription records
            print("\n=== Subscription Records ===")
            subscriptions = Subscription.query.all()
            print(f"Total subscriptions: {len(subscriptions)}")
            for s in subscriptions:
                user = User.query.get(s.user_id)
                plan = MealPlan.query.get(s.meal_plan_id)
                print(f"ID: {s.id}, User: {user.email}, Plan: {plan.name}, Status: {s.status}")
                print(f"  Start: {s.start_date}, Period Start: {s.current_period_start}, Period End: {s.current_period_end}")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    check_tables() 