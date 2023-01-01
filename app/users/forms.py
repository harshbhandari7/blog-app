from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed 
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

from app.models import User

class RegistrationForm(FlaskForm):
    # First Param is label
    username = StringField('Username',
        validators=[
            DataRequired(), Length(min=3, max=20) ])
    email = StringField('Email',
        validators=[DataRequired(), Email() ])
    password = PasswordField('Password',
        validators=[ DataRequired(), Length(min=8, max=20) ])
    confirm_password = PasswordField('Confirm Password',
        validators=[ DataRequired(), Length(min=8, max=20), EqualTo('password') ])
    submit = SubmitField('Sign Up')

    # Custom Form Field Validation Error Method Template
    '''
        def validate_fieldname(self, field_name):
            # logic to validate

            if validation_failed:
                raise ValidationError('Error Message')
    '''

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if len(username.data) < 10:
            raise ValidationError('Username is too short !!!')

        if user:
            raise ValidationError('username is already taken')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('This email is already registered!')


class LoginForm(FlaskForm):
    email = StringField('Email',
        validators=[DataRequired(), Email() ])
    password = PasswordField('Password',
        validators=[ DataRequired(), Length(min=8, max=20) ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AccountUpdateForm(FlaskForm):
    username = StringField('Username',
        validators=[
            DataRequired(), Length(min=3, max=20) ])
    email = StringField('Email',
        validators=[DataRequired(), Email() ])
    pfp = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if username.data != current_user.username:
            if len(username.data) < 10:
                raise ValidationError('Username is too short !!!')

            if user:
                raise ValidationError('username is already taken')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if email.data != current_user.email:
            if user:
                raise ValidationError('This email is already registered!')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[ DataRequired(), Email() ])
    submit = SubmitField('Request Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is None:
            raise ValidationError('There is no account associated with this mail!')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
        validators=[ DataRequired(), Length(min=8, max=20) ])
    confirm_password = PasswordField('Confirm Password',
        validators=[ DataRequired(), Length(min=8, max=20), EqualTo('password') ])
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is None:
            raise ValidationError('There is no account associated with this mail!')
