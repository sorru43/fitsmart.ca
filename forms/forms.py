"""
General form definitions
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional

class ContactForm(FlaskForm):
    """Contact form for general inquiries"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=2, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Send Message')

class CorporateInquiryForm(FlaskForm):
    """Form for corporate/business inquiries"""
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    contact_person = StringField('Contact Person', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    company_size = SelectField('Company Size', validators=[DataRequired()], choices=[
        ('', 'Select Company Size'),
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees')
    ])
    inquiry_type = SelectField('Inquiry Type', validators=[DataRequired()], choices=[
        ('', 'Select Inquiry Type'),
        ('corporate_catering', 'Corporate Catering'),
        ('employee_wellness', 'Employee Wellness Program'),
        ('bulk_orders', 'Bulk Orders'),
        ('partnership', 'Partnership Opportunity'),
        ('franchise', 'Franchise Inquiry'),
        ('other', 'Other')
    ])
    budget_range = SelectField('Budget Range', validators=[Optional()], choices=[
        ('', 'Select Budget Range'),
        ('under_10k', 'Under ₹10,000'),
        ('10k_50k', '₹10,000 - ₹50,000'),
        ('50k_1l', '₹50,000 - ₹1,00,000'),
        ('1l_5l', '₹1,00,000 - ₹5,00,000'),
        ('above_5l', 'Above ₹5,00,000')
    ])
    preferred_start_date = DateField('Preferred Start Date', validators=[Optional()])
    message = TextAreaField('Additional Details', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Submit Inquiry') 