from app import create_app, db
from models import Subscription

app = create_app()

def check_subscription_statuses():
    with app.app_context():
        print("\n=== Checking Subscription Statuses ===")
        subscriptions = Subscription.query.all()
        print(f"Total subscriptions: {len(subscriptions)}")
        for s in subscriptions:
            print(f"ID: {s.id}, Status: {s.status}")

if __name__ == '__main__':
    check_subscription_statuses() 