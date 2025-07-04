# HealthyRizz Admin Notification System Guide

This guide explains how to use the HealthyRizz admin notification system to send push notifications to your customers.

## Accessing the Notification System

1. Log in to your HealthyRizz admin account
2. Navigate to Admin > Notifications
3. You'll see the notification management interface

## Sending Notifications

### Basic Steps

1. **Compose your notification**:
   - Enter a title (appears in bold at the top of the notification)
   - Enter a message (the main content of the notification)
   - Add a URL (optional - where users will go when they click the notification)

2. **Choose recipients**:
   - All subscribed users (anyone who has enabled notifications)
   - Active subscribers only (users with an active meal plan subscription)
   - Specific user (send to just one user by selecting them from the dropdown)

3. **Select notification type**:
   - General Announcement
   - Promotion/Special Offer
   - Order Update
   - Delivery Information
   - Account Update

4. **Click "Send Notification"**

### Using Templates

To save time, you can use the quick templates in the right sidebar:

1. Click on any template (e.g., "New Menu Item", "Special Offer")
2. The form will be automatically filled with template content
3. Edit the content as needed
4. Complete sending as normal

## Notification Statistics

The statistics card shows:

- Total number of users subscribed to notifications
- Number of notifications sent today
- Success rate (percentage of notifications successfully delivered)

## Notification History

To view your notification history:

1. Look at the "Recent Notifications" table at the bottom of the page
2. For more detailed history, click "View All" or navigate to Admin > Notification History
3. In the history view, you can:
   - See all past notifications
   - Filter by date
   - Resend previous notifications
   - View delivery statistics

## Best Practices

For effective notifications:

- **Keep titles short** (40-50 characters max)
- **Keep messages concise** (100-120 characters recommended)
- **Limit frequency** to 2-3 notifications per week to avoid user fatigue
- **Send at appropriate times** (10am-6pm is generally best)
- **Include a clear call to action** in your message
- **Use notification types consistently** to help users recognize the importance

## Troubleshooting

If notifications aren't being received:

1. **Check the success rate** in the statistics card
2. **View detailed logs** in Admin > Notification History
3. **Verify VAPID keys** are properly configured
4. **Ensure users have granted permission** (they must explicitly allow notifications)

## Technical Requirements

The notification system requires:

1. VAPID keys to be generated (these secure the push notification system)
2. HTTPS connection (push notifications only work over secure connections)
3. Modern browsers that support the Web Push API (Chrome, Firefox, Edge, Opera)

To generate new VAPID keys (if needed), use the CloudPanel deployment script or run:
```bash
python generate_vapid_keys.py --email admin@healthyrizz.ca
```
