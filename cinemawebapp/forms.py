from flask_wtf import FlaskForm
from flask import request
from wtforms import TextField, SubmitField, TextAreaField, PasswordField, StringField, SelectMultipleField, IntegerField, DateField
from wtforms.validators import DataRequired, Required, Email, EqualTo, ValidationError, Length
from .models import Member, User, Admins, Movie, Screen, Booking

class SignUpForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    email = StringField('Email', validators = [DataRequired(),Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    repeatPassword = PasswordField('repeat password', validators=[DataRequired(), EqualTo('password')])
    register = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username already exists. Please choose a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email address already exists. Please use a different email address')

class LoginForm(FlaskForm):
    username = StringField('username', validators = [DataRequired()])
    password = PasswordField('password', validators = [DataRequired()])
    signin = SubmitField('Sign In')
    
class MemberForm(FlaskForm):
    phone = TextField('Phone Number', validators = [DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    r_password = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField('Request Password Reset')
