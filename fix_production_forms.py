#!/usr/bin/env python3
"""
Production Forms Import Fix Script
This script fixes the forms import issue on the production server
"""

import os
import sys

def fix_production_forms():
    """Fix the forms import structure on production server"""
    
    print("🔧 Fixing production forms import structure...")
    
    # Check if we're on the production server
    if not os.path.exists('/home/healthyrizz/htdocs/healthyrizz.in'):
        print("❌ This script should be run on the production server")
        return False
    
    base_path = '/home/healthyrizz/htdocs/healthyrizz.in'
    
    # Fix 1: Update forms/__init__.py on production
    forms_init_path = os.path.join(base_path, 'forms', '__init__.py')
    forms_init_content = '''"""
Forms package initialization
"""
from .auth_forms import LoginForm, RegisterForm, ProfileForm, MealCalculatorForm, ContactForm, NewsletterForm
from .checkout_forms import CheckoutForm
from .trial_forms import TrialRequestForm
from .forms import ContactForm as GeneralContactForm, CorporateInquiryForm

__all__ = ['LoginForm', 'RegisterForm', 'ProfileForm', 'MealCalculatorForm', 'ContactForm', 'NewsletterForm', 'CheckoutForm', 'TrialRequestForm', 'GeneralContactForm', 'CorporateInquiryForm']
'''
    
    try:
        with open(forms_init_path, 'w', encoding='utf-8') as f:
            f.write(forms_init_content)
        print(f"✅ Updated {forms_init_path}")
    except Exception as e:
        print(f"❌ Error updating forms/__init__.py: {e}")
        return False
    
    # Fix 2: Update routes/main_routes.py on production
    main_routes_path = os.path.join(base_path, 'routes', 'main_routes.py')
    
    try:
        # Read the current file
        with open(main_routes_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the old import
        old_import = "from forms.forms import ContactForm, CorporateInquiryForm"
        new_import = "from forms import GeneralContactForm, CorporateInquiryForm"
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            
            # Write the updated content
            with open(main_routes_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated {main_routes_path}")
        else:
            print(f"⚠️  Import statement already updated in {main_routes_path}")
    
    except Exception as e:
        print(f"❌ Error updating routes/main_routes.py: {e}")
        return False
    
    # Fix 3: Ensure forms.py exists with the correct content
    forms_py_path = os.path.join(base_path, 'forms', 'forms.py')
    forms_py_content = '''"""
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
'''
    
    try:
        with open(forms_py_path, 'w', encoding='utf-8') as f:
            f.write(forms_py_content)
        print(f"✅ Created/Updated {forms_py_path}")
    except Exception as e:
        print(f"❌ Error creating forms.py: {e}")
        return False
    
    print("🎉 Production forms import structure fixed successfully!")
    print("\n📋 Next steps:")
    print("1. Restart gunicorn: sudo supervisorctl restart healthyrizz")
    print("2. Check logs: sudo tail -f /var/log/healthyrizz.err.log")
    
    return True

if __name__ == "__main__":
    success = fix_production_forms()
    sys.exit(0 if success else 1) 