from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, BooleanField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Optional, Length, EqualTo

class CheckoutForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    province = StringField('Province', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])

class TrialRequestForm(FlaskForm):
    meal_plan_id = HiddenField('Meal Plan ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    province = SelectField('State', validators=[DataRequired()], choices=[
        ('', 'Select State'),
        ('PB', 'Punjab'),
        ('HR', 'Haryana'),
        ('DL', 'Delhi'),
        ('MH', 'Maharashtra'),
        ('KA', 'Karnataka'),
        ('TN', 'Tamil Nadu'),
        ('TS', 'Telangana'),
        ('WB', 'West Bengal'),
        ('GJ', 'Gujarat'),
        ('RJ', 'Rajasthan'),
        ('UP', 'Uttar Pradesh'),
        ('BR', 'Bihar'),
        ('JH', 'Jharkhand'),
        ('OD', 'Odisha'),
        ('CG', 'Chhattisgarh'),
        ('MP', 'Madhya Pradesh'),
        ('HP', 'Himachal Pradesh'),
        ('UK', 'Uttarakhand'),
        ('JK', 'Jammu & Kashmir'),
        ('OT', 'Other')
    ])
    postal_code = StringField('PIN Code', validators=[DataRequired(), Length(min=6, max=6)])
    notes = TextAreaField('Notes', validators=[Optional()])
    preferred_date = DateField('Preferred Date', validators=[Optional()])

class MultiPurposeContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(min=10, max=15)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    
    # Inquiry type and related fields
    inquiry_type = SelectField('Inquiry Type', choices=[
        ('general', 'General Inquiry'),
        ('location_request', 'Location Request'),
        ('franchise', 'Franchise Opportunity'),
        ('consultation', 'Expert Consultation'),
        ('support', 'Customer Support'),
        ('feedback', 'Feedback/Suggestion')
    ], validators=[DataRequired()])
    
    # Location fields (for location requests)
    city = StringField('City', validators=[Optional(), Length(max=50)])
    state = SelectField('State', choices=[
        ('', 'Select State'),
        ('punjab', 'Punjab'),
        ('haryana', 'Haryana'),
        ('delhi', 'Delhi'),
        ('mumbai', 'Maharashtra'),
        ('bangalore', 'Karnataka'),
        ('chennai', 'Tamil Nadu'),
        ('hyderabad', 'Telangana'),
        ('kolkata', 'West Bengal'),
        ('other', 'Other')
    ], validators=[Optional()])
    pincode = StringField('PIN Code', validators=[Optional(), Length(min=6, max=6)])
    
    # Franchise fields
    investment_range = SelectField('Investment Range', choices=[
        ('', 'Select Investment Range'),
        ('5-10_lakhs', '₹5-10 Lakhs'),
        ('10-25_lakhs', '₹10-25 Lakhs'),
        ('25-50_lakhs', '₹25-50 Lakhs'),
        ('50_lakhs_plus', '₹50 Lakhs+')
    ], validators=[Optional()])
    business_experience = SelectField('Business Experience', choices=[
        ('', 'Select Experience Level'),
        ('none', 'No Experience'),
        ('1-3_years', '1-3 Years'),
        ('3-5_years', '3-5 Years'),
        ('5_plus_years', '5+ Years')
    ], validators=[Optional()])
    preferred_location = StringField('Preferred Location', validators=[Optional(), Length(max=100)])
    
    # Consultation fields
    consultation_type = SelectField('Consultation Type', choices=[
        ('', 'Select Consultation Type'),
        ('nutrition', 'Nutrition Consultation'),
        ('fitness', 'Fitness Consultation'),
        ('weight_loss', 'Weight Loss Consultation'),
        ('meal_planning', 'Meal Planning'),
        ('health_coaching', 'Health Coaching')
    ], validators=[Optional()])
    preferred_time = SelectField('Preferred Time', choices=[
        ('', 'Select Preferred Time'),
        ('morning', 'Morning (9 AM - 12 PM)'),
        ('afternoon', 'Afternoon (12 PM - 3 PM)'),
        ('evening', 'Evening (3 PM - 6 PM)'),
        ('night', 'Night (6 PM - 9 PM)')
    ], validators=[Optional()])
    preferred_date = DateField('Preferred Date', validators=[Optional()])
    
    # Contact preferences
    contact_preference = SelectField('Preferred Contact Method', choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('whatsapp', 'WhatsApp'),
        ('any', 'Any Method')
    ], validators=[DataRequired()])
    
    urgency = SelectField('Urgency Level', choices=[
        ('low', 'Low - No Rush'),
        ('normal', 'Normal'),
        ('high', 'High - Within 24 hours'),
        ('urgent', 'Urgent - Same day')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Send Message')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Update Profile')

class MealCalculatorForm(FlaskForm):
    age = StringField('Age', validators=[DataRequired()])
    weight = StringField('Weight (kg)', validators=[DataRequired()])
    height = StringField('Height (cm)', validators=[DataRequired()])
    activity_level = SelectField('Activity Level', choices=[
        ('sedentary', 'Sedentary'),
        ('lightly_active', 'Lightly Active'),
        ('moderately_active', 'Moderately Active'),
        ('very_active', 'Very Active'),
        ('extremely_active', 'Extremely Active')
    ], validators=[DataRequired()])
    goal = SelectField('Goal', choices=[
        ('lose_weight', 'Lose Weight'),
        ('maintain_weight', 'Maintain Weight'),
        ('gain_weight', 'Gain Weight')
    ], validators=[DataRequired()])
    submit = SubmitField('Calculate')

class NewsletterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe') 