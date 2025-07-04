"""
Routes for Progressive Web App (PWA) functionality
"""
from flask import Blueprint, send_from_directory, current_app

# Create PWA blueprint
pwa_bp = Blueprint('pwa', __name__)

# Serve the service worker from the root directory
@pwa_bp.route('/service-worker.js')
def service_worker():
    """Serve the service worker file from the static folder"""
    return send_from_directory('static/js', 'service-worker.js')

# Serve the manifest file
@pwa_bp.route('/manifest.json')
def manifest():
    """Serve the manifest file from the static folder"""
    return send_from_directory('static', 'manifest.json')

# Serve the offline page
@pwa_bp.route('/offline')
def offline():
    """Display the offline fallback page"""
    return current_app.send_static_file('offline.html') 