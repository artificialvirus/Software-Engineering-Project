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

class AdminLoginForm(FlaskForm):
    username = TextField('username', validators = [DataRequired()])
    email = StringField('Email', validators = [DataRequired(),Email()])
    password = PasswordField('password', validators = [DataRequired()])
    signin = SubmitField('Sign In')

class MoviesForm(FlaskForm):
    name = TextField('Movie Name', validators = [DataRequired()])
    duration = TextField('Movie Duration', validators = [DataRequired()])
    genre = TextField('Movie Genre', validators = [DataRequired()])
    certificate = TextField('Certificate', validators = [DataRequired()])
    releaseDate = DateField('Release Date', format='%Y/%m/%d')
    endDate = DateField('End Date', format='%Y/%m/%d')
    submit = SubmitField('Submit')

    def validate_enddate_field(form, field):
        if field.data < form.startdate_field.data:
            raise ValidationError("End date must not be earlier than start date.")

class BookingForm(FlaskForm):


    #movie_name = SelectMultipleField('Movie Name', choices=[('example movie')])
    movie_name = SelectMultipleField('Card Type', choices=[('movie1'), ('movie2')])
    #movie_date = SelectMultipleField('Movie Date', choices=[('example dates')])
    movie_date = DateField('Release Date', format='%Y-%m-%d')
    #screen_time = SelectMultipleField('Screen Time', choices=[('example times')])
    screen_time = TextField('Screen Time', validators = [DataRequired()])
    seatings = SelectMultipleField('Movie Seating', choices=[('premium'), ('classic')])
    #num_of_tickets = SelectMultipleField('Tickets', choices=[('1'), ('2'), ...])
    tickets = TextField('Tickets', validators = [DataRequired()])

class MemberForm(FlaskForm):
    phone = TextField('Phone Number', validators = [DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    card_type = SelectMultipleField('Card Type', choices=[('MasterCard'), ('Visa')])
    card_number = TextField('Card Number', validators=[DataRequired()])
    card_expiration_date = DateField('Expiration Date', validators=[DataRequired()])
    card_cvv = PasswordField('Card CVV', validators=[DataRequired()])

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    r_password = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField('Request Password Reset')
