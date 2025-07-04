import subprocess
import json
import re

# List of packages to check
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

# Get the latest version for each package
latest_versions = {}
for package in packages:
    try:
        # Run pip index to get package info
        result = subprocess.run(
            ["pip", "index", "versions", package],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract the latest version
        output = result.stdout
        version_match = re.search(r"Available versions: ([\d\.]+)", output)
        if version_match:
            latest_version = version_match.group(1)
            latest_versions[package] = latest_version
        else:
            latest_versions[package] = "Version not found"
    except subprocess.CalledProcessError:
        latest_versions[package] = "Error checking version"

print(json.dumps(latest_versions, indent=2))