from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class VideoUploadForm(FlaskForm):
    """Form for uploading videos or adding YouTube videos"""
    video_type = SelectField('Video Type', choices=[
        ('youtube', 'YouTube Video'),
        ('upload', 'Uploaded Video')
    ], validators=[DataRequired()])
    
    title = StringField('Video Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=200, message='Title must be between 3 and 200 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000, message='Description must be less than 1000 characters')
    ])
    
    youtube_url = StringField('YouTube URL', validators=[Optional()])
    
    video_file = FileField('Video File', validators=[
        Optional(),
        FileAllowed(['mp4', 'webm', 'avi', 'mov'], 'Only video files are allowed')
    ])
    
    thumbnail_file = FileField('Thumbnail Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed')
    ])
    
    order = IntegerField('Display Order', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Order must be between 0 and 100')
    ], default=0)
    
    is_active = BooleanField('Active', default=True)

class VideoEditForm(FlaskForm):
    """Form for editing video details"""
    title = StringField('Video Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=200, message='Title must be between 3 and 200 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000, message='Description must be less than 1000 characters')
    ])
    
    video_type = SelectField('Video Type', choices=[
        ('youtube', 'YouTube Video'),
        ('upload', 'Uploaded Video')
    ], validators=[DataRequired()])
    
    youtube_url = StringField('YouTube URL', validators=[Optional()])
    
    video_file = FileField('Video File', validators=[
        Optional(),
        FileAllowed(['mp4', 'webm', 'avi', 'mov'], 'Only video files are allowed')
    ])
    
    thumbnail_file = FileField('Thumbnail Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed')
    ])
    
    order = IntegerField('Display Order', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Order must be between 0 and 100')
    ], default=0)
    
    is_active = BooleanField('Active', default=True) 