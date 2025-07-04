from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional

class TrialRequestForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Address', validators=[DataRequired(), Length(min=5, max=200)])
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
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    preferred_date = DateField('Preferred Date', validators=[Optional()])
    meal_plan_id = HiddenField('Meal Plan ID', validators=[DataRequired()]) 