"""
Multi-purpose contact form for various inquiry types
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional

class MultiPurposeContactForm(FlaskForm):
    """Multi-purpose contact form supporting various inquiry types"""
    
    # Basic Information
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=2, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
    
    # Inquiry Type
    inquiry_type = SelectField('Inquiry Type', validators=[DataRequired()], choices=[
        ('', 'Select Inquiry Type'),
        ('location_request', 'Location Request'),
        ('franchise', 'Franchise Inquiry'),
        ('general_query', 'General Query'),
        ('expert_consultation', 'Expert Consultation'),
        ('corporate_catering', 'Corporate Catering'),
        ('bulk_orders', 'Bulk Orders'),
        ('other', 'Other')
    ])
    
    # Location Information
    city = StringField('City', validators=[Optional(), Length(max=100)])
    state = StringField('State/Province', validators=[Optional(), Length(max=50)])
    pincode = StringField('Postal Code', validators=[Optional(), Length(max=10)])
    
    # Franchise Specific Fields
    investment_range = SelectField('Investment Range', validators=[Optional()], choices=[
        ('', 'Select Investment Range'),
        ('5-10L', '5-10 Lakhs'),
        ('10-20L', '10-20 Lakhs'),
        ('20-50L', '20-50 Lakhs'),
        ('50L+', '50 Lakhs+')
    ])
    business_experience = TextAreaField('Business Experience', validators=[Optional(), Length(max=500)])
    preferred_location = StringField('Preferred Location', validators=[Optional(), Length(max=200)])
    
    # Expert Consultation Fields
    consultation_type = SelectField('Consultation Type', validators=[Optional()], choices=[
        ('', 'Select Consultation Type'),
        ('nutrition', 'Nutrition'),
        ('fitness', 'Fitness'),
        ('meal_planning', 'Meal Planning'),
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('general_health', 'General Health')
    ])
    preferred_time = SelectField('Preferred Time', validators=[Optional()], choices=[
        ('', 'Select Preferred Time'),
        ('morning', 'Morning (9 AM - 12 PM)'),
        ('afternoon', 'Afternoon (12 PM - 4 PM)'),
        ('evening', 'Evening (4 PM - 8 PM)')
    ])
    preferred_date = DateField('Preferred Date', validators=[Optional()])
    
    # Urgency
    urgency = SelectField('Urgency', validators=[Optional()], choices=[
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
        ('low', 'Low')
    ], default='normal')
    
    submit = SubmitField('Send Message')

