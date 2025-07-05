þ#!/usr/bin/env python3
"""
HealthyRizz Local Development Server
Run this script to start the application locally
"""

from main import app
import os

if __name__ == "__main__":
    print(" Starting HealthyRizz Local Development Server...")
    print("=" * 60)
    print(" Application: HealthyRizz Meal Delivery Platform")
    print(" URL: http://127.0.0.1:5001")
    print(" Admin Panel: http://127.0.0.1:5001/admin/dashboard")
    print(" Admin Login: admin@healthyrizz.in / admin123")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the Flask application
        app.run(
            host="127.0.0.1",
            port=5001,
            debug=True,
            use_reloader=False  # Disable reloader to avoid issues
        )
    except KeyboardInterrupt:
        print("\n Server stopped by user")
    except Exception as e:
        print(f" Server error: {e}")
        print(" Try running on a different port if needed")

