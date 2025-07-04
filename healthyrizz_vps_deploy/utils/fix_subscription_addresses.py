from app import create_app
from models import Subscription, SubscriptionStatus, db

def fix_addresses():
    app = create_app()
    with app.app_context():
        updated = 0
        active_subs = Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).all()
        for sub in active_subs:
            sub.delivery_address = '123 Test Street'
            sub.delivery_city = 'Test City'
            sub.delivery_province = 'Test Province'
            sub.delivery_postal_code = '12345'
            updated += 1
        db.session.commit()
        print(f"Updated {updated} active subscriptions with test address data.")

if __name__ == "__main__":
    fix_addresses() 