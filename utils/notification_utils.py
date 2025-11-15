from datetime import datetime, time
from flask import current_app as app
from database.models import WaterIntakeReminder, User
from utils.email_utils import send_email
import pytz

def send_water_reminder(reminder):
    """
    Send a water intake reminder to a user
    
    Args:
        reminder (WaterIntakeReminder): The reminder object
    """
    try:
        user = reminder.user
        if not user or not user.email:
            app.logger.error(f"Cannot send water reminder: Invalid user or email for reminder {reminder.id}")
            return False
            
        # Calculate progress towards daily goal
        current_time = datetime.now(pytz.UTC)
        local_time = current_time.astimezone(pytz.timezone('Asia/Kolkata'))
        
        # Create email content
        subject = "Time to Hydrate! 💧"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4CAF50;">Stay Hydrated!</h2>
            <p>Hi {user.name},</p>
            <p>It's time to drink some water! 💧</p>
            <p>Remember:</p>
            <ul>
                <li>Your daily target: {reminder.daily_target_ml}ml</li>
                <li>Try to drink a glass of water (250ml) now</li>
                <li>Stay consistent throughout the day</li>
            </ul>
            <p>Benefits of staying hydrated:</p>
            <ul>
                <li>Improved energy levels</li>
                <li>Better digestion</li>
                <li>Enhanced workout performance</li>
                <li>Clearer skin</li>
            </ul>
            <p style="color: #666;">This is an automated reminder from HealthyRizz. You can adjust your reminder settings in your account.</p>
        </body>
        </html>
        """
        
        # Send email
        success = send_email(
            to_email=user.email,
            from_email="healthyrizz.in@gmail.com",
            subject=subject,
            html_content=html_content
        )
        
        if success:
            app.logger.info(f"Water reminder sent successfully to user {user.id}")
        else:
            app.logger.error(f"Failed to send water reminder to user {user.id}")
            
        return success
        
    except Exception as e:
        app.logger.error(f"Error sending water reminder: {str(e)}")
        return False

def check_and_send_water_reminders():
    """
    Check and send water reminders to users based on their preferences
    """
    try:
        current_time = datetime.now(pytz.UTC)
        local_time = current_time.astimezone(pytz.timezone('Asia/Kolkata'))
        current_time_of_day = local_time.time()
        
        # Get all active reminders
        active_reminders = WaterIntakeReminder.query.filter_by(is_active=True).all()
        
        for reminder in active_reminders:
            # Check if current time is within reminder window
            if reminder.start_time <= current_time_of_day <= reminder.end_time:
                # Calculate if it's time to send a reminder based on interval
                minutes_since_midnight = current_time_of_day.hour * 60 + current_time_of_day.minute
                if minutes_since_midnight % reminder.interval_minutes == 0:
                    send_water_reminder(reminder)
                    
    except Exception as e:
        app.logger.error(f"Error checking water reminders: {str(e)}") 