from app import create_app, db
from database.models import Subscription, User, MealPlan

app = create_app()

with app.app_context():
    subs = Subscription.query.all()
    print(f'Total subscriptions: {len(subs)}')
    for s in subs:
        user = User.query.get(s.user_id)
        plan = MealPlan.query.get(s.meal_plan_id)
        print(f'ID: {s.id}, User: {user.email if user else None}, Plan: {plan.name if plan else None}, Status: {s.status}, Start: {s.start_date}, Period Start: {s.current_period_start}, Period End: {s.current_period_end}') 