þ#!/usr/bin/env python3

print(" Starting HealthyRizz Application...")
print("=" * 50)

try:
    # Import and test the app
    from main import app
    print(" App imported successfully")
    
    # Check admin user exists
    from models import User, db
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        admin = User.query.filter_by(email="admin@healthyrizz.in").first()
        if not admin:
            print(" Creating admin user...")
            admin = User(
                name="Admin User",
                email="admin@healthyrizz.in",
                phone="+919876543210",
                password=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print(" Admin user created")
        else:
            print(" Admin user exists")
    
    print("=" * 50)
    print(" Starting server on http://127.0.0.1:5001")
    print(" Admin panel: http://127.0.0.1:5001/admin/dashboard")
    print(" Login: admin@healthyrizz.in / admin123")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the application
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True,
        use_reloader=False
    )

except KeyboardInterrupt:
    print("\n Server stopped by user")
except Exception as e:
    print(f" Error starting application: {e}")
    import traceback
    traceback.print_exc()
    print("\n Try running \"python main.py\" instead")

