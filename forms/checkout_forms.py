"""
Checkout form definitions
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional

class CheckoutForm(FlaskForm):
    """Form for handling checkout process"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Delivery Address', validators=[DataRequired(), Length(min=5, max=200)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=50)])
    province = SelectField('Province', validators=[DataRequired()], choices=[
        ('ON', 'Ontario'),
        ('BC', 'British Columbia'),
        ('AB', 'Alberta'),
        ('QC', 'Quebec'),
        ('NS', 'Nova Scotia'),
        ('NB', 'New Brunswick'),
        ('MB', 'Manitoba'),
        ('PE', 'Prince Edward Island'),
        ('SK', 'Saskatchewan'),
        ('NL', 'Newfoundland and Labrador'),
        ('NT', 'Northwest Territories'),
        ('NU', 'Nunavut'),
        ('YT', 'Yukon')
    ])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(min=6, max=7)])
    delivery_instructions = TextAreaField('Delivery Instructions', validators=[Optional(), Length(max=500)])
    save_address = BooleanField('Save this address for future orders') 