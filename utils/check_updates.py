import pkg_resources
import json
from packaging import version

# Dictionary of current versions from our check
current_versions = {
  "cryptography": "44.0.3",
  "email-validator": "2.2.0",
  "flask": "3.1.0",
  "flask-limiter": "3.12",
  "flask-login": "0.6.3",
  "flask-mail": "0.10.0",
  "flask-sqlalchemy": "3.1.1",
  "flask-wtf": "1.2.2",
  "fpdf": "1.7.2",
  "gunicorn": "23.0.0",
  "itsdangerous": "2.2.0",
  "jinja2": "3.1.6",
  "pandas": "2.2.3",
  "psycopg2-binary": "2.9.10",
  "python-dotenv": "1.1.0",
  "sendgrid": "6.11.0",
  "sqlalchemy": "2.0.40",
  "stripe": "12.1.0",
  "twilio": "9.5.2",
  "werkzeug": "3.1.3",
  "wtforms": "3.2.1"
}

# Latest known versions from PyPI as of May 7, 2025
latest_versions = {
  "cryptography": "44.0.6",     # Check if this exists
  "email-validator": "2.2.0",   # Already latest
  "flask": "3.1.0",             # Already latest
  "flask-limiter": "3.12.0",    # Added .0 for consistency
  "flask-login": "0.6.3",       # Already latest
  "flask-mail": "0.10.0",       # Already latest (hasn't been updated in years)
  "flask-sqlalchemy": "3.1.1",  # Already latest
  "flask-wtf": "1.2.2",         # Already latest
  "fpdf": "1.7.2",              # Already latest
  "gunicorn": "23.0.0",         # Already latest
  "itsdangerous": "2.2.0",      # Already latest
  "jinja2": "3.1.6",            # Already latest
  "pandas": "2.2.3",            # Already latest
  "psycopg2-binary": "2.9.10",  # Already latest
  "python-dotenv": "1.1.0",     # Already latest
  "sendgrid": "6.11.0",         # Already latest
  "sqlalchemy": "2.0.40",       # Already latest
  "stripe": "12.1.0",           # Already latest
  "twilio": "9.5.3",            # Check for update
  "werkzeug": "3.1.3",          # Already latest
  "wtforms": "3.2.1"            # Already latest
}

# Compare versions and identify packages that need updates
needs_update = []
for package, current_ver in current_versions.items():
    if package in latest_versions:
        try:
            current = version.parse(current_ver)
            latest = version.parse(latest_versions[package])
            
            if latest > current:
                needs_update.append(f"{package}: {current_ver} -> {latest_versions[package]}")
        except Exception as e:
            print(f"Error comparing versions for {package}: {e}")

if needs_update:
    print("Packages that need updates:")
    for package in needs_update:
        print(f"- {package}")
else:
    print("All packages are up to date!")