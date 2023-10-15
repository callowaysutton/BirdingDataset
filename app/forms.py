from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
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
    email = StringField('Email',
                             validators=[DataRequired(), Length(min=1, max=20)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            flash('Username is taken!', 'danger')
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class LinkForm(FlaskForm):
    username = StringField('URL', validators=[DataRequired(), Length(min=2, max=1024)], default="https://google.com")
    password = StringField('Nickname', validators=[DataRequired()], default="Google")
    submit = SubmitField('Submit')

class BirdUploadForm(FlaskForm):
    name = StringField('Bird Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    picture = FileField('Upload Bird Picture', validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired()])
    longitude = FloatField('Longitude', validators=[DataRequired()])

class BirdValidationForm(FlaskForm):
    rating = IntegerField('Rating (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    description = TextAreaField('Description', validators=[DataRequired()])
