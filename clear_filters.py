from flask import url_for
from app import create_app

app = create_app()

def clear_filters():
    with app.app_context():
        # Generate the URL for admin_subscriptions with no filters
        url = url_for('admin_subscriptions', _external=True)
        print("\n=== Clear Filters and Reload ===")
        print(f"Visit this URL to clear all filters and reload the subscriptions page:")
        print(url)

if __name__ == '__main__':
    clear_filters() 