"""
API routes for the HealthyRizz application
"""
import os
import json
import logging
import subprocess
from flask import request, jsonify
from main import app
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

@app.route('/api/generate-vapid-keys', methods=['POST'])
def generate_vapid_keys_api():
    """Generate VAPID keys for push notifications and save to .env file"""
    try:
        data = request.json
        if not data or 'email' not in data:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        email = data['email']
        
        # Run the generate_vapid_keys.py script
        result = subprocess.run(
            ['python', 'generate_vapid_keys.py', '--email', email],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error generating VAPID keys: {result.stderr}")
            return jsonify({'success': False, 'error': result.stderr}), 500
        
        logger.info("VAPID keys generated successfully")
        
        # Load the newly generated keys to make them available immediately
        load_dotenv(override=True)
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Error generating VAPID keys: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/check-vapid-keys', methods=['GET'])
def check_vapid_keys():
    """Check if VAPID keys are configured"""
    vapid_public_key = os.environ.get('VAPID_PUBLIC_KEY')
    vapid_private_key = os.environ.get('VAPID_PRIVATE_KEY')
    
    return jsonify({
        'configured': bool(vapid_public_key and vapid_private_key),
        'public_key_available': bool(vapid_public_key)
    })
