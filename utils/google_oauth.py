"""
Google OAuth utility functions for FitSmart
"""
from authlib.integrations.flask_client import OAuth

def init_oauth(app):
    """Initialize OAuth with Google"""
    if not app.config.get('GOOGLE_CLIENT_ID') or not app.config.get('GOOGLE_CLIENT_SECRET'):
        return None, None
    
    oauth = OAuth(app)
    
    google = oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url=app.config.get('GOOGLE_DISCOVERY_URL'),
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    return oauth, google

