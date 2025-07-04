from app import create_app

app = create_app()
with app.app_context():
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        if str(rule).startswith('/admin'):
            print(f"{rule} -> {rule.endpoint}") 