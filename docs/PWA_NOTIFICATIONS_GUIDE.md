# HealthyRizz PWA Push Notification System

This guide explains how the push notification system works in the HealthyRizz Progressive Web App (PWA).

## Overview

The push notification system allows HealthyRizz to send notifications to users even when they're not actively using the website. This is useful for:

- Sending delivery updates
- Notifying about meal plan changes
- Sending subscription reminders
- Alerting users about special promotions

## Components

The notification system consists of several components:

1. **Service Worker** - Handles notification display and click events
2. **Push API** - Allows sending notifications to users' devices
3. **Subscription Database** - Stores users' notification subscriptions
4. **API Endpoints** - For managing subscriptions and sending notifications
5. **VAPID Authentication** - Secures the push notification system

## Setup Instructions

### 1. Generate VAPID Keys

VAPID (Voluntary Application Server Identification) keys are required for sending push notifications. To generate them:

```bash
python generate_vapid_keys.py --email admin@healthyrizz.ca
```

This will create a public/private key pair in your `.env` file.

### 2. Enable Push Notifications in Client

Add the notification button to any page where you want users to enable notifications:

```html
{% include 'static/templates/notification-button.html' %}
```

### 3. Send Notifications

Notifications can be sent using the API endpoint:

```bash
curl -X POST http://your-domain.com/api/send-notification \
  -H "Content-Type: application/json" \
  -d '{"title":"New Meal Available", "message":"Try our new keto-friendly chicken bowl!", "url":"/meals"}'
```

Or use the test page: `/notification-test`

## Implementation Details

### Client-Side Components

1. **push-notifications.js**: Handles subscribing to push notifications and sending the subscription to the server.
2. **service-worker.js**: Contains event handlers for push notifications and notification clicks.
3. **notification-button.html**: Provides a UI component for users to enable notifications.

### Server-Side Components

1. **routes_notifications.py**: Contains API endpoints for managing push notification subscriptions.
2. **routes_api.py**: Contains endpoints for generating VAPID keys and checking their status.
3. **generate_vapid_keys.py**: Script to generate and store VAPID keys.

## Database Schema

The push notification system uses a `PushSubscription` model with the following structure:

```
- id: Primary key
- user_id: Foreign key to User (nullable)
- endpoint: The subscription endpoint URL
- p256dh: Public key for the subscription
- auth: Authentication token for the subscription
- created_at: Timestamp when the subscription was created
```

## Adding to CloudPanel Deployment

The PWA notification system is integrated with the main HealthyRizz deployment. When you run the deployment script, it will:

1. Set up all necessary files for the PWA
2. Install required Python packages
3. Configure the database schema for push subscriptions
4. Import the notification routes

## Testing Push Notifications

Visit the `/notification-test` page to:

1. Generate VAPID keys if they don't exist
2. Test sending notifications
3. Verify subscription functionality

## Troubleshooting

If push notifications aren't working:

1. **Check browser support**: Chrome, Edge, Firefox and Opera support push notifications
2. **Verify HTTPS**: Push notifications only work over secure connections
3. **Check VAPID keys**: Make sure keys are properly generated and stored in .env
4. **Check Console Logs**: Look for errors in browser developer tools
5. **Verify Service Worker**: Check if service worker is registered in browser's Application tab
6. **Database Issues**: Ensure the push_subscriptions table exists in the database

## Additional Resources

- [Web Push API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [Service Worker API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [VAPID Protocol Information](https://datatracker.ietf.org/doc/html/draft-thomson-webpush-vapid)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
