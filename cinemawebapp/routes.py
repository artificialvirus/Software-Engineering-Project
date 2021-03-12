from flask import render_template, flash, request, redirect, url_for, session, json
from cinemawebapp import app
from cinemawebapp.models import Member, Admin, Guest, Movies, Screening, Booking
from .forms import SignUpForm, LoginForm, ResetPasswordRequestForm, AdminLoginForm, MoviesForm, BookingForm, PaymentForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
import logging
from flask_mail import Mail, Message
from flask_login import login_user, logout_user, login_required, current_user

from cinemawebapp import db, models

# Sample movie data
movies = [
    {
        'director': 'Michael Bay',
        'title' : 'Explosions',
        'description' : 'Boom'
    },
    {
        'director': 'Guy Richie',
        'title' : 'Hilarity',
        'description' : 'A funny film'
    }

]


@app.route("/")
@app.route("/home")
def home():
    # movies = Post.query.all()
    return render_template('layout.html')


@app.route("/")
@app.route("/admin")
def admin():
    
    # sales = Booking.query.all()

    return render_template('admin.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    app.logger.info('Signup request route')
    app.logger.debug('Debug level logging')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignUpForm()
    if form.validate_on_submit():
        user = Member(username=form.username.data, email=form.email.data, phoneNumber=forn.user_phone.data, age=form.user_age.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        msg = Message('You have successfully created your account.', sender = 'yourId@gmail.com', recipients = [user.email])
        msg.body = "Email from Cinema"
        mail.send(msg)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    app.logger.info('Login request route')
    app.logger.debug('Debug level logging')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Member.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    app.logger.info('Logout route')
    app.logger.debug('Debug level logging')
    logout_user()
    return redirect(url_for('home'))
