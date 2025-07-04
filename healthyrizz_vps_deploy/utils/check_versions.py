import pkg_resources
import json

# List of packages we're interested in
packages = [
    "cryptography",
    "email-validator",
    "flask",
    "flask-limiter",
    "flask-login",
    "flask-mail",
    "flask-sqlalchemy",
    "flask-wtf",
    "fpdf",
    "gunicorn",
    "itsdangerous",
    "jinja2",
    "pandas",
    "psycopg2-binary",
    "python-dotenv",
    "sendgrid",
    "sqlalchemy",
    "stripe",
    "twilio",
    "werkzeug",
    "wtforms"
]

# Get version information for each package
installed_packages = {}
for package_name in packages:
    try:
        version = pkg_resources.get_distribution(package_name).version
        installed_packages[package_name] = version
    except pkg_resources.DistributionNotFound:
        installed_packages[package_name] = "Not installed"

# Display results
print(json.dumps(installed_packages, indent=2))