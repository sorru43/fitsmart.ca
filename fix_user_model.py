#!/usr/bin/env python3
"""
Script to fix the User model by adding required Flask-Login methods
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, '/home/healthyrizz/htdocs/healthyrizz.in')

# Read the models.py file
try:
    with open('models.py', 'r') as f:
        content = f.read()
    
    # Check if Flask-Login methods are already present
    if 'def get_id(self):' in content:
        print("✅ Flask-Login methods already present in User model")
        sys.exit(0)
    
    # Find the location to insert the Flask-Login methods
    # We'll insert after the check_password method
    insert_point = content.find('return check_password_hash(self.password, password)')
    
    if insert_point == -1:
        print("❌ Could not find insertion point in User model")
        sys.exit(1)
    
    # Find the end of the check_password method
    end_of_method = content.find('\n', insert_point)
    insert_point = end_of_method + 1
    
    # The methods to insert
    flask_login_methods = '''    
    # Flask-Login required methods
    def get_id(self):
        """Return the user ID as a string (required by Flask-Login)"""
        return str(self.id)
    
    def is_authenticated(self):
        """Return True if the user is authenticated (required by Flask-Login)"""
        return True
    
    def is_anonymous(self):
        """Return False for regular users (required by Flask-Login)"""
        return False
'''
    
    # Insert the methods
    new_content = content[:insert_point] + flask_login_methods + content[insert_point:]
    
    # Write the updated content back to the file
    with open('models.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Successfully added Flask-Login methods to User model")
    print("🔄 Please restart the service: systemctl restart healthyrizz")
    
except FileNotFoundError:
    print("❌ models.py file not found")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error updating models.py: {e}")
    sys.exit(1) 