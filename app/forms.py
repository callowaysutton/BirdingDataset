from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask import flash
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name',
                             validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Last Name',
                             validators=[DataRequired(), Length(min=1, max=20)])
    organization = StringField('Organization',
                             validators=[Length(min=1, max=20)])
    location = StringField('Location',
                             validators=[Length(min=1, max=20)])
    email = StringField('Email',
                             validators=[DataRequired(), Length(min=1, max=20)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            flash('Username is taken!', 'danger')
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class LinkForm(FlaskForm):
    username = StringField('URL',
                           validators=[DataRequired(), Length(min=2, max=1024)], default="https://google.com")
    password = StringField('Nickname', validators=[DataRequired()], default="Google")
    submit = SubmitField('Submit')
