# Firebase Setup Guide for FitSmart

This guide explains how Firebase is integrated into the FitSmart application.

## Overview

Firebase has been integrated for:
- **Firebase Analytics** - Track user behavior and app performance
- **Future integrations** - Authentication, Cloud Messaging, Firestore, etc.

## Configuration

### Frontend Configuration

Firebase is initialized in `templates/base.html` with the following configuration:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyAT2e7cQ8CV6DI_ekF6CQwxeEa2FBGuRrs",
  authDomain: "fitsmart-web.firebaseapp.com",
  projectId: "fitsmart-web",
  storageBucket: "fitsmart-web.firebasestorage.app",
  messagingSenderId: "233893386700",
  appId: "1:233893386700:web:b65857d303458570996569",
  measurementId: "G-KL81PX3VRR"
};
```

### Backend Configuration

Firebase Admin SDK is installed and can be initialized in `app.py` or utility files.

## Files

### Frontend Files

1. **`templates/base.html`**
   - Contains Firebase initialization script
   - Loads Firebase SDK from CDN
   - Initializes Analytics

2. **`static/js/firebase-config.js`**
   - Standalone Firebase configuration file (alternative approach)
   - Can be used if you prefer separate config file

3. **`static/js/firebase-utils.js`**
   - Utility functions for Firebase Analytics
   - Helper functions for tracking events
   - Functions: `trackPageView()`, `trackUserAction()`, `trackPurchase()`, etc.

### Backend Files

1. **`requirements.txt`**
   - Includes `firebase-admin==6.5.0` for backend Firebase operations

## Usage

### Frontend - Track Events

```javascript
// Track page view
if (window.firebaseUtils) {
    window.firebaseUtils.trackPageView('/meal-plans', 'Meal Plans');
}

// Track user action
window.firebaseUtils.trackUserAction('button_click', 'navigation', 'subscribe');

// Track purchase
window.firebaseUtils.trackPurchase(99.99, 'CAD', [
    { name: 'Weekly Plan', price: 99.99 }
]);

// Track subscription
window.firebaseUtils.trackSubscription('Weekly Plan', 99.99, 'CAD');
```

### Backend - Initialize Firebase Admin

```python
import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase Admin (one time)
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Send push notification
message = messaging.Message(
    notification=messaging.Notification(
        title='New Meal Plan Available',
        body='Check out our new weekly plan!'
    ),
    token='device-token'
)
messaging.send(message)
```

## Content Security Policy

The CSP has been updated in `app.py` to allow:
- Firebase scripts from `https://www.gstatic.com`
- Firebase API connections to `https://www.googleapis.com` and Firebase domains

## Next Steps

### Potential Integrations

1. **Firebase Authentication**
   - Can replace or complement Google OAuth
   - Supports multiple providers (Email, Phone, etc.)

2. **Firebase Cloud Messaging (FCM)**
   - Replace current VAPID push notifications
   - More reliable and feature-rich

3. **Firestore Database**
   - Real-time database for live updates
   - Can sync with SQLAlchemy models

4. **Firebase Storage**
   - Store user-uploaded images
   - CDN-backed file storage

5. **Firebase Hosting**
   - Deploy static assets
   - CDN for better performance

## Environment Variables

For backend Firebase Admin, add to `.env`:

```env
# Firebase Admin (optional - for backend operations)
FIREBASE_CREDENTIALS_PATH=path/to/serviceAccountKey.json
# OR
FIREBASE_PROJECT_ID=fitsmart-web
```

## Security Notes

- Firebase API keys are safe to expose in frontend code
- They are restricted by domain in Firebase Console
- Never expose service account keys (backend only)
- Keep Firebase Admin credentials secure

## Troubleshooting

### Firebase not initializing
- Check browser console for errors
- Verify CSP allows Firebase domains
- Check network tab for blocked requests

### Analytics not tracking
- Verify `measurementId` is correct
- Check Firebase Console for data
- Ensure Analytics is enabled in Firebase Console

### CORS errors
- Add Firebase domains to CSP `connect-src`
- Check Firebase Console for allowed domains

## Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firebase Analytics](https://firebase.google.com/docs/analytics)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)

