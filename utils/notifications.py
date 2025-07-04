import logging

def send_push_notification_to_user(user_id, title, message, data=None):
    logging.info(f"Push notification to user {user_id}: {title} - {message}")
    return True

def send_push_notification_to_all_users(title, message, data=None):
    logging.info(f"Broadcast notification: {title} - {message}")
    return {"success": True, "sent_count": 100} 