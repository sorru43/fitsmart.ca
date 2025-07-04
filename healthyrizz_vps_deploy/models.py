from datetime import datetime
from extensions import db

class TrialRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)  # Indian phone number format
    preferred_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)  # Changed from province to state
    pincode = db.Column(db.String(6), nullable=False)  # Changed from postal_code to pincode
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plan.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    meal_plan = db.relationship('MealPlan', backref=db.backref('trial_requests', lazy=True))
    user = db.relationship('User', backref=db.backref('trial_requests', lazy=True))
    
    def __repr__(self):
        return f'<TrialRequest {self.id} - {self.name}>' 

class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    calories = db.Column(db.String(50), nullable=False)  # Changed to string to support ranges
    protein = db.Column(db.String(50), nullable=False)  # Changed to string to support ranges
    carbs = db.Column(db.String(50), nullable=False)  # Changed to string to support ranges
    fat = db.Column(db.String(50), nullable=False)  # Changed to string to support ranges
    price_weekly = db.Column(db.Float, nullable=False)  # Price in INR
    price_monthly = db.Column(db.Float, nullable=False)  # Price in INR
    price_trial = db.Column(db.Float, nullable=False, default=999.00)  # Changed default trial price to INR
    is_vegetarian = db.Column(db.Boolean, default=False)
    includes_breakfast = db.Column(db.Boolean, default=True)
    available_for_trial = db.Column(db.Boolean, default=True)
    tag = db.Column(db.String(50))
    is_popular = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # New per-meal pricing columns
    price_per_meal_veg = db.Column(db.Float)  # Price per vegetarian meal
    price_per_meal_nonveg = db.Column(db.Float)  # Price per non-vegetarian meal
    price_per_meal_breakfast = db.Column(db.Float, default=199.00)  # Price per breakfast meal

    def get_price_weekly(self, with_breakfast=True):
        if with_breakfast:
            return self.price_weekly
        return self.price_weekly - 199.00  # Changed breakfast cost to INR

    def get_price_monthly(self, with_breakfast=True):
        if with_breakfast:
            return self.price_monthly
        return self.price_monthly - 796.00  # Changed breakfast cost to INR

    def get_price_trial(self, with_breakfast=True):
        if with_breakfast:
            return self.price_trial
        return self.price_trial - 199.00  # Changed breakfast cost to INR 

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('meal_plan.id'), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # weekly or monthly
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, delivered, cancelled
    
    # Customer details
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(15), nullable=False)
    customer_address = db.Column(db.String(255), nullable=False)
    customer_city = db.Column(db.String(100), nullable=False)
    customer_state = db.Column(db.String(50), nullable=False)
    customer_pincode = db.Column(db.String(10), nullable=False)
    delivery_instructions = db.Column(db.Text)
    
    # Plan details
    vegetarian_days = db.Column(db.String(20))  # Comma-separated list of days (0-6)
    includes_breakfast = db.Column(db.Boolean, default=False)
    
    # Payment details
    payment_id = db.Column(db.String(100))  # Razorpay payment ID
    payment_status = db.Column(db.String(20))  # pending, captured, failed
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='INR')
    
    # Discount details
    coupon_code = db.Column(db.String(20))
    discount_amount = db.Column(db.Float, default=0)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    plan = db.relationship('MealPlan', backref=db.backref('orders', lazy=True))
    
    @property
    def total_amount(self):
        return self.amount - self.discount_amount
    
    def __repr__(self):
        return f'<Order {self.id}>' 

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Set password hash"""
        from werkzeug.security import generate_password_hash
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)
    
    # Flask-Login required methods
    def get_id(self):
        """Return the user ID as a string (required by Flask-Login)"""
        return str(self.id)
    
    def is_authenticated(self):
        """Return True if the user is authenticated (required by Flask-Login)"""
        return True
    
    def is_anonymous(self):
        """Return False for regular users (required by Flask-Login)"""
        return False
    
    @staticmethod
    def create_user(email, username=None, password=None, **kwargs):
        """Create a new user with proper validation"""
        if not username:
            username = email.split('@')[0]  # Use email prefix as username if not provided
            
        # Check if username is already taken
        if User.query.filter_by(name=username).first():
            # Append a random number to make it unique
            import random
            username = f"{username}{random.randint(1000, 9999)}"
            
        user = User(
            name=username,
            email=email,
            **kwargs
        )
        
        if password:
            user.set_password(password)
            
        return user

    def __repr__(self):
        return f'<User {self.email}>' 

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plan.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, paused, cancelled
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # New columns for smart meal planning
    veg_days_json = db.Column(db.Text)  # JSON string of veg days (0-6)
    meals_per_week = db.Column(db.Integer, default=5)  # 5, 6, or 7 days
    with_breakfast = db.Column(db.Boolean, default=True)  # Include breakfast
    
    # Relationships
    user = db.relationship('User', backref=db.backref('subscriptions', lazy=True))
    meal_plan = db.relationship('MealPlan', backref=db.backref('subscriptions', lazy=True))
    
    def __repr__(self):
        return f'<Subscription {self.id} - {self.user.email}>' 

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
        return f"Area({self.name}, City={self.city_id})"

class BlogPost(db.Model):
    """Blog post model"""
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    featured_image = db.Column(db.String(500))
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    published_date = db.Column(db.DateTime)
    
    # Relationships
    author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))
    
    def __init__(self, **kwargs):
        super(BlogPost, self).__init__(**kwargs)
        if 'content' in kwargs and not self.summary:
            self.summary = kwargs['content'][:200] + '...' if len(kwargs['content']) > 200 else kwargs['content']
        if not self.created_at:
            self.created_at = datetime.now()
        if self.is_published and not self.published_date:
            self.published_date = datetime.now()
    
    def __repr__(self):
        return f'<BlogPost {self.title}>' 

class HeroSlide(db.Model):
    """Model for hero section slides"""
    __tablename__ = 'hero_slides'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(300))
    image_url = db.Column(db.String(500), nullable=False)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<HeroSlide {self.title}>'

class Video(db.Model):
    """Model for homepage videos"""
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_type = db.Column(db.String(50), default='youtube')  # youtube, mp4, etc.
    video_url = db.Column(db.String(500))  # YouTube ID or video URL
    thumbnail_url = db.Column(db.String(500))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Video {self.title}>'

class TeamMember(db.Model):
    """Model for team members"""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500))
    bio = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TeamMember {self.name}>'

class SiteSetting(db.Model):
    """Model for site settings"""
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(300))
    setting_type = db.Column(db.String(50), default='text')  # text, image, url, json
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SiteSetting {self.key}>'

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('contact_inquiries', lazy=True))
    
    def __repr__(self):
        return f'<ContactInquiry {self.name} - {self.inquiry_type}>'
    
    @property
    def is_urgent(self):
        return self.priority == 'urgent'
    
    @property
    def is_new(self):
        return self.status == 'new'
    
    @property
    def days_since_created(self):
        return (datetime.utcnow() - self.created_at).days

class FAQ(db.Model):
    """Frequently Asked Questions model for the website"""
    __tablename__ = 'faq'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True, default='General')  # Category for organizing FAQs
    order = db.Column(db.Integer, default=0)  # For custom ordering of FAQs
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FAQ {self.question}>' 