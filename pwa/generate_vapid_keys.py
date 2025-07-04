#!/usr/bin/env python3
"""
Generate VAPID keys for Web Push Notifications

This script generates a pair of VAPID keys (Voluntary Application Server Identification)
that are required for sending web push notifications from a server to a client.

The keys are saved in a .env file and printed to the console.
"""

import os
import base64
from dotenv import load_dotenv

def generate_vapid_keys():
    """Generate VAPID keys for web push notifications"""
    try:
        # Try to import the pywebpush library
        from pywebpush import webpush, WebPushException
        from py_vapid import Vapid
    except ImportError:
        print("Required libraries not found. Installing them now...")
        os.system("pip install pywebpush py-vapid")
        # Now import after installation
        from pywebpush import webpush, WebPushException
        from py_vapid import Vapid
    
    # Generate VAPID keys
    vapid = Vapid()
    vapid.generate_keys()
    
    # Get keys in the correct format
    vapid_private_key = vapid.private_key.decode('utf-8')
    vapid_public_key = base64.urlsafe_b64encode(vapid.public_key).decode('utf-8')
    
    return {
        'VAPID_PRIVATE_KEY': vapid_private_key,
        'VAPID_PUBLIC_KEY': vapid_public_key
    }

def main():
    """Main function to generate and save VAPID keys"""
    import argparse
    parser = argparse.ArgumentParser(description='Generate VAPID keys for Web Push Notifications')
    parser.add_argument('--email', help='Contact email for VAPID claims')
    parser.add_argument('--force', action='store_true', help='Force overwrite existing keys')
    args = parser.parse_args()
    
    print("Generating VAPID keys for Web Push Notifications...")
    
    # Load existing .env file if it exists
    env_file = '.env'
    load_dotenv(env_file)
    
    # Check if keys already exist
    if os.environ.get('VAPID_PRIVATE_KEY') and os.environ.get('VAPID_PUBLIC_KEY') and not args.force:
        if os.isatty(0):  # Only ask if running in a terminal
            print("VAPID keys already exist in your .env file.")
            replace = input("Do you want to replace them? (y/n): ").lower()
            if replace != 'y':
                print("Keeping existing VAPID keys.")
                return
        else:
            print("VAPID keys already exist. Use --force to overwrite.")
            return
    
    # Generate new keys
    keys = generate_vapid_keys()
    
    # Ask for contact email if not already set or provided via args
    if args.email:
        keys['VAPID_CONTACT_EMAIL'] = args.email
    elif not os.environ.get('VAPID_CONTACT_EMAIL'):
        if os.isatty(0):  # Only ask if running in a terminal
            email = input("Enter a contact email for VAPID (required for push notifications): ")
            keys['VAPID_CONTACT_EMAIL'] = email
        else:
            print("Error: Contact email is required. Use --email option.")
            return
    else:
        keys['VAPID_CONTACT_EMAIL'] = os.environ.get('VAPID_CONTACT_EMAIL')
    
    # Read existing .env file
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # Update with new keys
    env_vars.update(keys)
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print("\nVAPID keys generated successfully and saved to .env file!")
    print("\nPublic Key (for client-side code):")
    print(keys['VAPID_PUBLIC_KEY'])
    print("\nPrivate Key (keep this secret):")
    print(keys['VAPID_PRIVATE_KEY'])
    print("\nContact Email:")
    print(keys['VAPID_CONTACT_EMAIL'])
    
    print("\nTo use these keys for push notifications:")
    print("1. Replace YOUR_PUBLIC_VAPID_KEY in push-notifications.js with the public key")
    print("2. Make sure to keep the .env file secure and never expose the private key")
    print("3. Install the pywebpush library: pip install pywebpush")

if __name__ == '__main__':
    main()