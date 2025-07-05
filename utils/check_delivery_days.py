from app import create_app
from models import Subscription, SubscriptionStatus
from datetime import datetime

def check_delivery_days():
    app = create_app()
    with app.app_context():
        today = datetime.now().date()
        active_subs = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).all()
        
        print(f"\nChecking delivery days for {today.strftime('%A, %B %d, %Y')}\n")
        
        for sub in active_subs:
            is_delivery_day = sub.is_delivery_day(today)
            delivery_days = sub.get_delivery_days_list()
            days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            delivery_days_names = [days_names[day] for day in delivery_days]
            
            print(f"Subscription #{sub.id}")
            print(f"User: {sub.user.name} ({sub.user.email})")
            print(f"Meal Plan: {sub.meal_plan.name}")
            print(f"Delivery Days: {', '.join(delivery_days_names)}")
            print(f"Is Today a Delivery Day: {'Yes' if is_delivery_day else 'No'}")
            print(f"Address: {sub.delivery_address}")
            print(f"City: {sub.delivery_city}")
            print(f"Province: {sub.delivery_province}")
            print(f"Postal Code: {sub.delivery_postal_code}")
            print("="*50 + "\n")

if __name__ == "__main__":
    check_delivery_days() 