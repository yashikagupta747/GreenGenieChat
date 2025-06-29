from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', 
                       validators=[
                           DataRequired(message='Email is required'),
                           Email(message='Invalid email address')
                       ],
                       render_kw={"placeholder": "Enter your email"})
    
    password = PasswordField('Password', 
                            validators=[
                                DataRequired(message='Password is required')
                            ],
                            render_kw={"placeholder": "Enter your password"})
    
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                          validators=[
                              DataRequired(message='Username is required'),
                              Length(min=4, max=20, message='Username must be between 4 and 20 characters')
                          ],
                          render_kw={"placeholder": "Choose a username"})
    
    email = StringField('Email',
                       validators=[
                           DataRequired(message='Email is required'),
                           Email(message='Invalid email address')
                       ],
                       render_kw={"placeholder": "Enter your email"})
    
    password = PasswordField('Password',
                            validators=[
                                DataRequired(message='Password is required'),
                                Length(min=8, message='Password must be at least 8 characters')
                            ],
                            render_kw={"placeholder": "Create a password"})
    
    password2 = PasswordField('Confirm Password',
                             validators=[
                                 DataRequired(message='Please confirm your password'),
                                 EqualTo('password', message='Passwords must match')
                             ],
                             render_kw={"placeholder": "Confirm your password"})
    
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Check if username contains only allowed characters
        if not username.data.isalnum():
            raise ValidationError('Username should contain only letters and numbers')
        
        # Check if username already exists
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        # Check if email already exists
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

        # Basic email format validation
        if '@' not in email.data or '.' not in email.data.split('@')[-1]:
            raise ValidationError('Invalid email format')

class ChatForm(FlaskForm):
    message = StringField('Message',
                         validators=[
                             DataRequired(message='Message cannot be empty'),
                             Length(max=500, message='Message too long (max 500 characters)')
                         ],
                         render_kw={"placeholder": "Ask about environmental science..."})
    
    submit = SubmitField('Send')