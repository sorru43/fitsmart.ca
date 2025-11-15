from app import create_app, db
from sqlalchemy import text
from database.models import SubscriptionStatus

def fix_subscription_status():
    app = create_app()
    with app.app_context():
        try:
            # First, let's see what values we have
            result = db.session.execute(text("SELECT id, status FROM subscriptions"))
            subscriptions = result.fetchall()
            print("\nCurrent subscription statuses:")
            for sub in subscriptions:
                print(f"ID: {sub[0]}, Status: {sub[1]}")
            
            # Update any lowercase 'active' to uppercase 'ACTIVE'
            db.session.execute(
                text("UPDATE subscriptions SET status = 'ACTIVE' WHERE status = 'active'")
            )
            db.session.commit()
            
            # Verify the changes
            result = db.session.execute(text("SELECT id, status FROM subscriptions"))
            subscriptions = result.fetchall()
            print("\nUpdated subscription statuses:")
            for sub in subscriptions:
                print(f"ID: {sub[0]}, Status: {sub[1]}")
            
            print("\nSubscription status values have been updated successfully.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating subscription status: {str(e)}")

if __name__ == "__main__":
    fix_subscription_status() 