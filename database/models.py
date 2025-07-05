from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import enum
import os
import json
from sqlalchemy import Enum, Text, String
from flask_login import UserMixin
import random

# Import SQLAlchemy instance from extensions.py
from extensions import db

# Models for Push Notifications
class PushSubscription(db.Model):
    """Push subscription for web push notifications"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    endpoint = db.Column(db.String(500), nullable=False)
    p256dh = db.Column(db.String(255), nullable=False)
    auth = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('push_subscriptions', lazy=True))
    
    def __repr__(self):
        return f"<PushSubscription {self.id}>"
    
    def to_json(self):
        return json.dumps({
            'endpoint': self.endpoint,
            'keys': {
                'p256dh': self.p256dh,
                'auth': self.auth
            }
        })

class Notification(db.Model):
    """Notification history and tracking"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(255), nullable=True)
    sent_count = db.Column(db.Integer, default=0)
    recipient_count = db.Column(db.Integer, default=0)
    notification_type = db.Column(db.String(50), default='general')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"

# Database compatibility layer
# Define database type for environment-specific configurations
DB_TYPE = "mysql" if os.environ.get('MYSQL_DATABASE') else "postgresql"

# MySQL has different string length limits and defaults than PostgreSQL
# PostgreSQL doesn't have a specific length limit for TEXT, but MySQL does
def get_text_type():
    """Return the appropriate text type based on the database"""
    if DB_TYPE == "mysql":
        # MySQL has TEXT with specific size limits
        return Text().with_variant(String(16777215), "mysql")  # MEDIUMTEXT - up to 16MB
    else:
        # PostgreSQL text doesn't need size limits
        return Text()

# SQLAlchemy will automatically handle most type mapping, but for specific cases
# like binary data, JSON, etc., custom mapping would be added here

class FAQ(db.Model):
    """Frequently Asked Questions model for the website"""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True, default='General')  # Category for organizing FAQs
    order = db.Column(db.Integer, default=0)  # For custom ordering of FAQs
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return self.question

class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Add these properties for backward compatibility with existing code
    @property
    def subscribed_at(self):
        return self.created_at
        
    @property
    def is_active(self):
        return True
    
    def __repr__(self):
        return f'<Newsletter {self.email}>'

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELED = "canceled"
    EXPIRED = "expired"
    
class SubscriptionFrequency(enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    
class DeliveryStatus(enum.Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    PACKED = "packed"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    CANCELLED = "cancelled"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)  # Add proper name field
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Address fields
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    province = db.Column(db.String(50), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Update property accessors for backward compatibility
    @property
    def display_name(self):
        """Return name if available, otherwise username"""
        return self.name if self.name else self.username
        
    @display_name.setter
    def display_name(self, value):
        self.name = value
    
    def set_password(self, password):
        """Set password hash using pbkdf2:sha256"""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256:50000',
            salt_length=16
        )
        
    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        try:
            return check_password_hash(self.password_hash, password)
        except Exception as e:
            current_app.logger.error(f"Error checking password: {str(e)}")
            return False
        
    @staticmethod
    def create_user(email, username=None, password=None, **kwargs):
        """Create a new user with proper validation"""
        if not username:
            username = email.split('@')[0]  # Use email prefix as username if not provided
            
        # Check if username is already taken
        if User.query.filter_by(username=username).first():
            # Append a random number to make it unique
            username = f"{username}{random.randint(1000, 9999)}"
            
        user = User(
            username=username,
            email=email,
            **kwargs
        )
        
        if password:
            user.set_password(password)
            
        return user

class DeliveryLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(2), nullable=False)
    postal_code_prefix = db.Column(db.String(3), nullable=True)  # Made nullable
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"{self.city}, {self.province}"
        
    @classmethod
    def check_delivery_available(cls, postal_code, city, province):
        """Check if delivery is available in the location"""
        if not postal_code or len(postal_code) < 3:
            return False
            
        # Use case-insensitive search for city
        from sqlalchemy import func
        
        # Check if the location is in our delivery area
        # We use functional.lower() for case-insensitive matching on city
        # The province should already be standardized
        location = cls.query.filter(
            func.lower(cls.city) == func.lower(city),
            cls.province == province.upper(),
            cls.is_active == True
        ).first()
        
        return location is not None

class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    calories = db.Column(db.String(20), nullable=False)
    protein = db.Column(db.String(20), nullable=False)
    fat = db.Column(db.String(20), nullable=True)
    carbs = db.Column(db.String(20), nullable=True)
    
    # Pricing fields
    price_weekly = db.Column(db.Numeric(10, 2), nullable=False)
    price_monthly = db.Column(db.Numeric(10, 2), nullable=False)
    price_trial = db.Column(db.Numeric(10, 2), default=14.99)
    
    for_gender = db.Column(db.String(10), default='both')  # 'male', 'female', or 'both'
    tag = db.Column(db.String(20))  # e.g., 'High Protein', 'Balanced', 'Performance'
    is_active = db.Column(db.Boolean, default=True)
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    is_gluten_free = db.Column(db.Boolean, default=False)
    is_dairy_free = db.Column(db.Boolean, default=False)
    is_keto = db.Column(db.Boolean, default=False)
    is_paleo = db.Column(db.Boolean, default=False)
    is_low_carb = db.Column(db.Boolean, default=False)
    is_high_protein = db.Column(db.Boolean, default=False)
    available_for_trial = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(255))
    is_popular = db.Column(db.Boolean, default=False)
    includes_breakfast = db.Column(db.Boolean, default=True)
    
    def get_price_weekly(self):
        """Get weekly price"""
        return float(self.price_weekly)
    
    def get_price_monthly(self):
        """Get monthly price"""
        return float(self.price_monthly)
    
    def get_price_trial(self):
        """Get trial price"""
        return float(self.price_trial) if self.price_trial else 14.99
    
    def __repr__(self):
        return self.name
        
    @property
    def dietary_tags(self):
        """Return a list of dietary tags for this meal plan"""
        tags = []
        if self.is_vegetarian:
            tags.append('Vegetarian')
        if self.is_vegan:
            tags.append('Vegan')
        if self.is_gluten_free:
            tags.append('Gluten Free')
        if self.is_dairy_free:
            tags.append('Dairy Free')
        if self.is_keto:
            tags.append('Keto')
        if self.is_paleo:
            tags.append('Paleo')
        if self.is_low_carb:
            tags.append('Low Carb')
        if self.is_high_protein:
            tags.append('High Protein')
        return tags

class CouponCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    discount_type = db.Column(db.String(20), nullable=False)  # 'percent', 'fixed', or 'shipping'
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)  # Amount or percentage
    min_order_value = db.Column(db.Numeric(10, 2), default=0)  # Minimum order value to apply coupon
    valid_from = db.Column(db.DateTime, nullable=False, default=datetime.now)
    valid_to = db.Column(db.DateTime, nullable=False)
    is_single_use = db.Column(db.Boolean, default=False)  # If true, can only be used once per user
    max_uses = db.Column(db.Integer, default=None)  # Maximum number of times this coupon can be used
    current_uses = db.Column(db.Integer, default=0)  # How many times the coupon has been used
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return self.code
        
    def is_valid(self):
        """Check if coupon is still valid"""
        now = datetime.now()
        
        # Check if coupon is active
        if not self.is_active:
            return False
            
        # Check if coupon is within valid date range
        if now < self.valid_from or now > self.valid_to:
            return False
            
        # Check if max uses is reached
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
            
        return True
        
    def calculate_discount(self, order_amount):
        """Calculate discount amount based on coupon type and order amount"""
        if not self.is_valid():
            return 0
            
        # Check minimum order value
        if order_amount < float(self.min_order_value):
            return 0
            
        # Calculate discount based on type
        if self.discount_type == 'percent':
            return round(order_amount * float(self.discount_value) / 100, 2)
        elif self.discount_type == 'fixed':
            return min(float(self.discount_value), order_amount)  # Don't discount more than order amount
        elif self.discount_type == 'shipping':
            return float(self.discount_value)  # Shipping discount value
            
        return 0
    
class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    link_text = db.Column(db.String(50), nullable=True)
    link_url = db.Column(db.String(255), nullable=True)
    background_color = db.Column(db.String(20), default="#4CAF50")  # Default to brand primary color
    text_color = db.Column(db.String(20), default="#FFFFFF")  # Default to white
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime, nullable=True)  # Null means no end date
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    @property
    def is_expired(self):
        """Check if the banner has expired"""
        if not self.end_date:
            return False
        return datetime.now() > self.end_date
    
    @classmethod
    def get_active_banner(cls):
        """Get the currently active banner to display"""
        try:
            now = datetime.now()
            
            # Use the actual Flask-SQLAlchemy session directly
            banner = db.session.query(cls).filter(
                cls.is_active == True,
                cls.start_date <= now,
                (cls.end_date == None) | (cls.end_date >= now)
            ).order_by(cls.id.desc()).first()
            
            return banner
        except Exception as e:
            # If any error occurs, return None
            import logging
            logging.error(f"Error in get_active_banner: {str(e)}")
            return None
        
    def __repr__(self):
        return self.message
        
class BlogPost(db.Model):
    """Blog post model"""
    __tablename__ = 'blog_post'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    meta_description = db.Column(db.String(300), nullable=True)  # Added meta_description field
    featured_image = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    published_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))  # Store as comma-separated values
    views = db.Column(db.Integer, default=0)  # Added views field
    
    def __repr__(self):
        return self.title

class ServiceRequest(db.Model):
    """Model for customers requesting service in a new area"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(2), nullable=False)
    postal_code = db.Column(db.String(7), nullable=False)
    message = db.Column(db.Text, nullable=True)
    is_contacted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"ServiceRequest #{self.id} - {self.city}, {self.province} ({self.postal_code})"
        
class TrialRequest(db.Model):
    """Model for customers requesting a 1-day trial meal plan"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(2), nullable=False)
    postal_code = db.Column(db.String(7), nullable=False)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plan.id'), nullable=False)
    meal_plan = db.relationship('MealPlan', backref=db.backref('trial_requests', lazy=True))
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    preferred_date = db.Column(db.Date, nullable=True)
    is_processed = db.Column(db.Boolean, default=False)
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"TrialRequest #{self.id} - {self.name} - {self.meal_plan.name} - {self.status}"

class Delivery(db.Model):
    """Model for tracking meal deliveries"""
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    subscription = db.relationship('Subscription', backref=db.backref('deliveries', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Add user_id field
    user = db.relationship('User', backref=db.backref('deliveries', lazy=True))  # Add user relationship
    delivery_date = db.Column(db.Date, nullable=False)
    status = db.Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    tracking_number = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)  # Admin notes about the delivery
    status_updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"Delivery #{self.id} - {self.subscription.user.name} - {self.delivery_date} - {self.status.value}"
    
    def update_status(self, new_status, notes=None):
        """Update the delivery status and optionally add notes"""
        if isinstance(new_status, str):
            new_status = DeliveryStatus(new_status)
        
        self.status = new_status
        self.status_updated_at = datetime.now()
        if notes:
            self.notes = notes if self.notes is None else f"{self.notes}\n{notes} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        return True
    
    @classmethod
    def get_deliveries_by_date(cls, date):
        """Get all deliveries for a specific date"""
        return cls.query.filter_by(delivery_date=date).all()
    
    @classmethod
    def get_user_upcoming_deliveries(cls, user_id, limit=5):
        """Get upcoming deliveries for a user"""
        today = datetime.now().date()
        return cls.query.join(Subscription).filter(
            Subscription.user_id == user_id,
            cls.delivery_date >= today
        ).order_by(cls.delivery_date).limit(limit).all()
    
    @classmethod
    def get_deliveries_by_status(cls, status, limit=100):
        """Get deliveries with a specific status"""
        if isinstance(status, str):
            status = DeliveryStatus(status)
            
        return cls.query.filter_by(status=status).order_by(cls.delivery_date).limit(limit).all()

class DeliveryMessage(db.Model):
    """Model for delivery status messages sent to users"""
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=False)
    delivery = db.relationship('Delivery', backref=db.backref('messages', lazy=True))
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.now)
    channel = db.Column(db.String(20), default="sms")  # sms, email, etc.
    status = db.Column(db.String(20), default="sent")  # sent, delivered, failed
    
    def __repr__(self):
        return f"DeliveryMessage #{self.id} - Delivery #{self.delivery_id} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"

class SkippedDelivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"SkippedDelivery #{self.id} - Subscription #{self.subscription_id} - {self.delivery_date}"
    
    @classmethod
    def is_delivery_skipped(cls, subscription_id, delivery_date):
        """Check if a delivery is skipped for a specific date"""
        return cls.query.filter_by(
            subscription_id=subscription_id,
            delivery_date=delivery_date
        ).first() is not None
    
    @classmethod
    def get_upcoming_skipped_deliveries(cls, subscription_id, from_date=None):
        """Get all upcoming skipped deliveries for a subscription"""
        if from_date is None:
            from_date = datetime.now().date()
            
        return cls.query.filter(
            cls.subscription_id == subscription_id,
            cls.delivery_date >= from_date
        ).order_by(cls.delivery_date).all()


class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('subscriptions', lazy='joined'))
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plan.id'), nullable=False)
    meal_plan = db.relationship('MealPlan', backref=db.backref('subscriptions', lazy=True))
    status = db.Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    frequency = db.Column(Enum(SubscriptionFrequency), nullable=False)
    stripe_subscription_id = db.Column(db.String(100), unique=True)
    stripe_customer_id = db.Column(db.String(100))
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime, nullable=True)  # Added end_date field
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    pause_collection = db.Column(db.Boolean, default=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Price at the time of subscription
    delivery_days = db.Column(db.String(20), default="0,1,2,3,4")  # Days of the week for delivery (0=Monday, 6=Sunday)
    vegetarian_days = db.Column(db.String(20), default="")  # Days of the week for vegetarian meals
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # Added delivery address fields
    delivery_address = db.Column(db.String(255))
    delivery_city = db.Column(db.String(100))
    delivery_province = db.Column(db.String(100))
    delivery_postal_code = db.Column(db.String(20))
    
    def __repr__(self):
        return f"Subscription #{self.id} - {self.user.name} - {self.meal_plan.name}"
        
    def pause(self):
        """Pause the subscription"""
        if self.status == SubscriptionStatus.ACTIVE:
            self.status = SubscriptionStatus.PAUSED
            self.pause_collection = True
            return True
        return False
        
    def resume(self):
        """Resume the subscription if it was paused"""
        if self.status == SubscriptionStatus.PAUSED:
            self.status = SubscriptionStatus.ACTIVE
            self.pause_collection = False
            return True
        return False
        
    def cancel(self):
        """Cancel the subscription"""
        if self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.PAUSED]:
            self.status = SubscriptionStatus.CANCELED
            self.cancel_at_period_end = True
            return True
        return False
        
    def get_delivery_days_list(self):
        """Get delivery days as a list of integers"""
        if not self.delivery_days:
            return [0, 1, 2, 3, 4]  # Default to weekdays (Monday-Friday)
        return [int(day) for day in self.delivery_days.split(',')]
    
    def set_delivery_days_list(self, days_list):
        """Set delivery days from a list of integers"""
        self.delivery_days = ','.join(str(day) for day in days_list)
        
    def is_delivery_day(self, date):
        """Check if the given date is a delivery day"""
        return date.weekday() in self.get_delivery_days_list()
    
    def get_upcoming_deliveries(self, days=14):
        """Get upcoming delivery dates for the next N days"""
        upcoming = []
        current_date = datetime.now().date()
        
        # Skip today if it's past cutoff time (5 hours before standard delivery time which is 6 PM)
        cutoff_hour = 11  # 11 AM (5 hours before 4 PM delivery start)
        if datetime.now().hour >= cutoff_hour:
            current_date += timedelta(days=1)
            
        # Get delivery days
        delivery_days = self.get_delivery_days_list()
        
        # Loop through the next N days
        end_date = current_date + timedelta(days=days)
        while current_date < end_date:
            # Check if this is a delivery day
            if current_date.weekday() in delivery_days:
                # Check if this delivery hasn't been skipped
                is_skipped = SkippedDelivery.is_delivery_skipped(self.id, current_date)
                
                # Check if we're past the cutoff time for today
                is_today = current_date == datetime.now().date()
                cutoff_passed = is_today and datetime.now().hour >= cutoff_hour
                
                # Can only skip if not already skipped and not past cutoff
                can_skip = not is_skipped and not cutoff_passed
                
                upcoming.append({
                    'date': current_date,
                    'formatted_date': current_date.strftime('%A, %B %d'),
                    'is_skipped': is_skipped,
                    'can_skip': can_skip,
                    'cutoff_passed': cutoff_passed
                })
            
            current_date += timedelta(days=1)
            
        return upcoming
    
    def skip_delivery(self, delivery_date):
        """Skip a delivery for a specific date"""
        # Convert string date to date object if needed
        if isinstance(delivery_date, str):
            delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
            
        # Check if delivery is in the future and after cutoff
        current_date = datetime.now().date()
        cutoff_hour = 11  # 11 AM (5 hours before 4 PM delivery start)
        
        if delivery_date == current_date and datetime.now().hour >= cutoff_hour:
            return False, "Cannot skip a delivery after the cutoff time (11 AM on delivery day)"
            
        # Create a new skipped delivery record
        skipped = SkippedDelivery(
            subscription_id=self.id,
            delivery_date=delivery_date
        )
        
        db.session.add(skipped)
        db.session.commit()
        
        return True, "Delivery skipped successfully"
    
    def unskip_delivery(self, delivery_date):
        """Cancel a previously skipped delivery"""
        # Convert string date to date object if needed
        if isinstance(delivery_date, str):
            delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
            
        # Check if delivery is in the future and after cutoff
        current_date = datetime.now().date()
        cutoff_hour = 11  # 11 AM (5 hours before 4 PM delivery start)
        
        if delivery_date == current_date and datetime.now().hour >= cutoff_hour:
            return False, "Cannot change a delivery after the cutoff time (11 AM on delivery day)"
            
        # Find and delete the skipped delivery record
        skipped = SkippedDelivery.query.filter_by(
            subscription_id=self.id,
            delivery_date=delivery_date
        ).first()
        
        if skipped:
            db.session.delete(skipped)
            db.session.commit()
            return True, "Delivery restored successfully"
        
        return False, "This delivery was not skipped"
    
    def schedule_delivery(self, delivery_date):
        """Schedule a delivery for the subscription"""
        # Convert string date to date object if needed
        if isinstance(delivery_date, str):
            delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
        
        # Check if this date is already scheduled
        existing = Delivery.query.filter_by(
            subscription_id=self.id,
            delivery_date=delivery_date
        ).first()
        
        if existing:
            return existing
        
        # Check if this date is skipped
        if SkippedDelivery.is_delivery_skipped(self.id, delivery_date):
            return None
        
        # Create a new delivery
        delivery = Delivery(
            subscription_id=self.id,
            delivery_date=delivery_date,
            status=DeliveryStatus.PENDING
        )
        
        db.session.add(delivery)
        db.session.commit()
        return delivery
    
    def get_upcoming_delivery_status(self):
        """Get status of upcoming deliveries for customer display"""
        today = datetime.now().date()
        upcoming_deliveries = Delivery.query.filter(
            Delivery.subscription_id == self.id,
            Delivery.delivery_date >= today
        ).order_by(Delivery.delivery_date).limit(5).all()
        
        return upcoming_deliveries

class SubscriptionVegDay(db.Model):
    """Model for tracking vegetarian days in a subscription"""
    __tablename__ = 'subscription_veg_days'
    
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 for Monday-Sunday
    
    subscription = db.relationship('Subscription', backref=db.backref('veg_days', lazy=True))
    
    def __repr__(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return f'<SubscriptionVegDay {days[self.day_of_week]}>'

class WaterIntakeReminder(db.Model):
    """Model for water intake reminders"""
    __tablename__ = 'water_intake_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    start_time = db.Column(db.Time, nullable=False)  # When to start sending reminders
    end_time = db.Column(db.Time, nullable=False)    # When to stop sending reminders
    interval_minutes = db.Column(db.Integer, default=60)  # How often to remind
    daily_target_ml = db.Column(db.Integer, nullable=True)  # Daily water intake target in ml (optional)
    wake_up_time = db.Column(db.Time, nullable=True)  # User's wake up time
    sleep_time = db.Column(db.Time, nullable=True)    # User's sleep time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('water_reminders', lazy=True))
    
    def __repr__(self):
        return f'<WaterIntakeReminder {self.id} for user {self.user_id}>'
        
    @property
    def is_awake(self):
        """Check if user is likely awake based on their schedule"""
        if not self.wake_up_time or not self.sleep_time:
            return True
            
        current_time = datetime.now().time()
        
        # If sleep time is before wake up time (e.g., 10 PM to 6 AM)
        if self.sleep_time < self.wake_up_time:
            return self.wake_up_time <= current_time <= self.sleep_time
        # If sleep time is after wake up time (e.g., 2 AM to 10 AM)
        else:
            return current_time >= self.wake_up_time or current_time <= self.sleep_time

class DietType(db.Model):
    """Diet type model for categorizing meals"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    meals = db.relationship('Meal', backref='diet_type', lazy=True)

class Meal(db.Model):
    """Meal model for food items"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Integer)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)
    image_url = db.Column(db.String(200))
    diet_type_id = db.Column(db.Integer, db.ForeignKey('diet_type.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='meal', lazy=True)

class Customer(db.Model):
    """Customer model for order management"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='customer', lazy=True)

class Order(db.Model):
    """Order model for tracking customer orders"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    delivery_address = db.Column(db.Text)
    delivery_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    """Order item model for tracking individual items in orders"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CouponUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon_code.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    coupon = db.relationship('CouponCode', backref=db.backref('usages', lazy=True))
    user = db.relationship('User', backref=db.backref('coupon_usages', lazy=True))
    order = db.relationship('Order', backref=db.backref('coupon_usage', lazy=True))
    
    def __repr__(self):
        return f'CouponUsage(coupon_id={self.coupon_id}, user_id={self.user_id})'

class State(db.Model):
    __tablename__ = 'state'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    cities = db.relationship('City', backref='state', cascade='all, delete-orphan')

    def __repr__(self):
        return f"State({self.name})"

class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    areas = db.relationship('Area', backref='city', cascade='all, delete-orphan')

    def __repr__(self):
        return f"City({self.name}, State={self.state_id})"

class Area(db.Model):
    __tablename__ = 'area'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)

    def __repr__(self):
        return f'<Area {self.name}>'

# New models for homepage content management
class HeroSlide(db.Model):
    """Model for hero section slides"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(300), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    button_text = db.Column(db.String(50), nullable=True)
    button_url = db.Column(db.String(200), nullable=True)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<HeroSlide {self.title}>'

class Video(db.Model):
    """Model for video content"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    youtube_url = db.Column(db.String(500), nullable=True)  # Made nullable for local videos
    thumbnail_url = db.Column(db.String(500), nullable=True)
    video_file = db.Column(db.String(500), nullable=True)  # New field for local video uploads
    video_type = db.Column(db.String(20), default='youtube')  # 'youtube' or 'upload'
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<Video {self.title}>'
    
    @property
    def youtube_id(self):
        """Extract YouTube video ID from URL"""
        if not self.youtube_url:
            return None
        import re
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
            r'youtube\.com\/shorts\/([^&\n?#]+)'  # Added support for YouTube Shorts
        ]
        for pattern in patterns:
            match = re.search(pattern, self.youtube_url)
            if match:
                return match.group(1)
        return None
    
    @property
    def video_url(self):
        """Get the appropriate video URL based on type"""
        if self.video_type == 'upload' and self.video_file:
            return f'/static/videos/{self.video_file}'
        elif self.video_type == 'youtube' and self.youtube_url:
            return self.youtube_url
        return None
    
    @property
    def thumbnail_image(self):
        """Get thumbnail URL with fallback"""
        if self.thumbnail_url:
            return self.thumbnail_url
        elif self.video_type == 'youtube' and self.youtube_id:
            return f"https://img.youtube.com/vi/{self.youtube_id}/maxresdefault.jpg"
        else:
            return '/static/images/default-video-thumbnail.jpg'

class TeamMember(db.Model):
    """Model for team members"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)
    twitter_url = db.Column(db.String(200), nullable=True)
    instagram_url = db.Column(db.String(200), nullable=True)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<TeamMember {self.name}>'

class SiteSetting(db.Model):
    """Model for site-wide settings"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<SiteSetting {self.key}>'
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key"""
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @classmethod
    def set_setting(cls, key, value, description=None):
        """Set a site setting"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
            setting.updated_at = datetime.now()
        else:
            setting = cls(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting

class ContactInquiry(db.Model):
    """Model for contact form inquiries"""
    __tablename__ = 'contact_inquiries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    inquiry_type = db.Column(db.String(50), nullable=False)  # location_request, franchise, general_query, expert_consultation
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Additional fields for specific inquiry types
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    
    # Franchise specific fields
    investment_range = db.Column(db.String(50), nullable=True)  # 5-10L, 10-20L, 20-50L, 50L+
    business_experience = db.Column(db.String(200), nullable=True)
    preferred_location = db.Column(db.String(200), nullable=True)
    
    # Expert consultation fields
    consultation_type = db.Column(db.String(100), nullable=True)  # nutrition, fitness, meal_planning, weight_loss
    preferred_time = db.Column(db.String(100), nullable=True)  # morning, afternoon, evening
    preferred_date = db.Column(db.Date, nullable=True)
    
    # Status tracking
    status = db.Column(db.String(20), default='new')  # new, in_progress, contacted, resolved, closed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    assigned_to = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contacted_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # User relationship (if logged in)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('contact_inquiries', lazy=True))
    
    def __repr__(self):
        return f'<ContactInquiry {self.id} - {self.name} ({self.inquiry_type})>'
    
    @property
    def is_urgent(self):
        return self.priority == 'urgent'
    
    @property
    def is_new(self):
        return self.status == 'new'
    
    @property
    def days_since_created(self):
        return (datetime.utcnow() - self.created_at).days

class WhyChooseSection(db.Model):
    """Model for the 'Why Choose HealthyRizz' section (single, admin-editable)"""
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    button_text = db.Column(db.String(100), nullable=True)
    button_url = db.Column(db.String(500), nullable=True)
    image_link_url = db.Column(db.String(500), nullable=True)
    show_button = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<WhyChooseSection {self.id}>'

class FullWidthSection(db.Model):
    """Model for a new full-width image section (comes after Why Choose section)"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=True)  # Optional title for the section
    image_url = db.Column(db.String(500), nullable=False)
    button_text = db.Column(db.String(100), nullable=True)
    button_url = db.Column(db.String(500), nullable=True)
    image_link_url = db.Column(db.String(500), nullable=True)
    show_button = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)  # For ordering multiple sections if needed
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<FullWidthSection {self.id} - {self.title}>'