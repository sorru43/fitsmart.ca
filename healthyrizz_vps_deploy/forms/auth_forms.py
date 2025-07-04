"""
Authentication form definitions
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    """Form for user registration"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_email(self, email):
        """Validate that email is not already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or login.')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Address', validators=[DataRequired(), Length(min=5, max=200)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=50)])
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=50)])
    pincode = StringField('Pincode', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Update Profile')

class MealCalculatorForm(FlaskForm):
    weight = StringField('Weight (kg)', validators=[DataRequired()])
    height = StringField('Height (cm)', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    activity_level = SelectField('Activity Level', validators=[DataRequired()], choices=[
        ('sedentary', 'Sedentary'),
        ('light', 'Lightly Active'),
        ('moderate', 'Moderately Active'),
        ('active', 'Very Active'),
        ('very_active', 'Extra Active')
    ])
    goal = SelectField('Goal', validators=[DataRequired()], choices=[
        ('lose', 'Lose Weight'),
        ('maintain', 'Maintain Weight'),
        ('gain', 'Gain Weight')
    ])
    submit = SubmitField('Calculate')

class ContactForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=2, max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Send Message')

class NewsletterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe') 