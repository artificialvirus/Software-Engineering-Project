from flask import g, render_template, flash, request, redirect, url_for, session, json, make_response
from cinemawebapp import app, mail
from cinemawebapp.models import Member, Admins, User, Movie, Screen, Booking
from .forms import SignUpForm, LoginForm, ResetPasswordRequestForm, AdminLoginForm, MoviesForm, BookingForm, MemberForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
import logging
from flask_mail import Mail, Message
from flask_login import login_user, logout_user, login_required, current_user
from cinemawebapp import db, models
from datetime import datetime, timedelta
from sqlalchemy import desc
import pdfkit

 #for debugging
import random
from random import randrange

class Theme:
    def __init__(self, primary_colours, field_colours, text_colours, font):
        self.primary_colours = primary_colours
        self.field_colours = field_colours
        self.text_colours = text_colours
        self.font = font
        self.font_size = "20px"

class DarkTheme(Theme):
    def __init__(self):
        super().__init__(
            ("#00020f", "#090a2e", "#191847"),
            ("#380012", "#5c001f", "#8c0031"),
            ("#746da6", "#b7b2ff", "#ffffff"),
            "Calibri Body")

def get_user_theme(theme_str="default"):
    return DarkTheme()

# Home page
@app.route("/")
@app.route("/home")
def home():
    return redirect(url_for('popular'))

import sys

@app.route("/payment/<screening_id>-<seats>")
def payment(screening_id, seats):
    seats_data = seats.split("?")
    seat_number = ""
    ticket_type = ""
    ticket_code = elements[0] + screening_id + elements[1] 
    for i in seats_data:
        elements = i.split(";")
        seat_number = elements[0]
        ticket_type = elements[1]

    booking = Booking(seat_number=seat_number, ticket_type=ticket_type, ticket_code=ticket_code, member_id=1, screen_id=screening_id)
    db.session.add(booking)
    db.session.commit()

    return render_template('payment.html', theme=get_user_theme(), booking_id=booking.id)

@app.route("/popular")
def popular():
    movies = Movie.query.all()
    new_release = Movie.query.order_by( desc("releaseDate")).limit(10)
    return render_template('popular.html', theme=get_user_theme(), title='popular' ,new=new_release,movies=movies)

# For you page
@app.route("/foryou")
def foryou():
    # member login required
    # based on genre most watched genre

    movies = Movie.query.all()
    return render_template('foryou.html', theme=get_user_theme(), title= 'for you' , movies=movies)

# Search page
@app.route("/search", methods=['GET','POST'])
def search():
    class Forms:
        pass
    forms = Forms();

    if request.method == 'POST':
        forms.search_title = request.form.getlist('search_title')[0]
        forms.start_date = request.form.getlist('start_date')[0]
        forms.start_time = request.form.getlist('start_time')[0]
        forms.end_date = request.form.getlist('end_date')[0]
        forms.end_time = request.form.getlist('end_time')[0]
        forms.genres = request.form.getlist('genres')
    else:
        forms.search_title = ""
        forms.start_date = datetime.today().strftime("%Y-%m-%d")
        forms.start_time = datetime.now().strftime("%H:%M")
        forms.end_date = (datetime.today() + timedelta(days=14)).strftime("%Y-%m-%d");
        forms.end_time = forms.start_time
        forms.genres = []

    print(vars(forms))

    # movies = Movie.query.all()
    # more_movies = movies * 10;
    movies = Movie.query.filter( (Movie.name.contains(forms.search_title) | Movie.description.contains(forms.search_title)))
    # movies = Movie.query.filter(Movie.genre.contains(forms.genres))
    # movies = sql movies matching criteria
    return render_template('search.html', theme=get_user_theme(), title='search', movies=movies, forms=forms)

#  Individual movie details page
@app.route("/movie/<movie_id>")
def movie(movie_id):
    #for debugging
    random.seed(10)

    # class Movie:
    #     pass
    class MovieDate:
        pass
    class Screening:
        pass

    movie = Movie.query.filter_by(id=movie_id).first()
    if not movie:
        return redirect(url_for('popular.html'))

    screenings = Screen.query.filter_by(movie_id=movie_id)
    if not screenings:
        return redirect(url_for('popular.html'))

    movie.movie_dates = []
    for i in range(screenings.count()):
        movie_date = MovieDate()
        movie_date.date = screenings[i].screen_time.date()
        movie_date.screenings = []
        for j in range(screenings.count()):
            if screenings[i].screen_time.date() == screenings[j].screen_time.date():
                screening = Screening()
                screening.time = screenings[i].screen_time.time()
                screening.id = screenings[i].id
                movie_date.screenings.append(screening)
        movie.movie_dates.append(movie_date)

    return render_template('movie.html', theme=get_user_theme(), movie=movie)

# About cinema page - not yet implemented
# @app.route("/about")
# def about():
#     return render_template('about.html', title='about')


#Admin page
@app.route("/admin")
@login_required
def admin():
    return render_template('admin.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    app.logger.info('Signup request route')
    app.logger.debug('Debug level logging')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        #not added the mail feature yet
        #msg = Message('You have successfully created your account.', sender = 'yourId@gmail.com', recipients = [user.email])
        #msg.body = "Email from Cinema"
        #mail.send(msg)

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('signup.html', theme=get_user_theme(), title='Sign Up', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    app.logger.info('Login request route')
    app.logger.debug('Debug level logging')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', theme=get_user_theme(), title='Sign In', form=form)


@app.route('/admin-signup', methods=['GET','POST'])
def adminsignup():
    app.logger.info('Signup request route')
    app.logger.debug('Debug level logging')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignUpForm()
    if form.validate_on_submit():
        admin = Admins(username=form.username.data, email=form.email.data)
        admin.set_password(form.password.data)

        db.session.add(admin)
        db.session.commit()

        #msg = Message('You have successfully created your account.', sender = 'yourId@gmail.com', recipients = [user.email])
        #msg.body = "Email from Cinema"
        #mail.send(msg)

        flash('Congratulations, you are now a registered Admin!')
        return redirect(url_for('admin'))
    return render_template('adminSignUp.html', title='Sign Up', form=form)


@app.route('/admin-login', methods=['GET','POST'])
def adminlogin():
    app.logger.info('Login request route')
    app.logger.debug('Debug level logging')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admins.query.filter_by(username=form.username.data).first()
        if admin is None or not admin.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('adminlogin'))

        login_user(admin, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin')
        return redirect(next_page)
    return render_template('adminLogin.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    app.logger.info('Logout route')
    app.logger.debug('Debug level logging')
    logout_user()
    return redirect(url_for('home'))


@app.route('/member', methods=['GET', 'POST'])
@login_required
def member():

    form = MemberForm()

    if form.validate_on_submit():
        payment = Member(phone=form.phone.data,date_of_birth=form.date_of_birth.data,
        card_number=form.card_number.data,card_expiration_date=form.card_expiration_date.data,
        card_cvv=form.card_cvv.data)

        db.session.add(payment)
        db.session.commit()


    return render_template('member.html',theme=get_user_theme(),form=form)


@app.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():

    form = BookingForm()

    if form.validate_on_submit():
        booking = Booking(seat_number=form.seatings.data)

        db.session.add(booking)
        db.session.commit()

    return render_template('booking.html',theme=get_user_theme(),form=form)


@app.route('/add-movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    form = MoviesForm()
    if form.validate_on_submit():
        addMovie = Movie(name=form.name.data, duration=form.duration.data,
           genre=form.genre.data, certificate=form.certificate.data,
           releaseDate=form.releaseDate.data, endDate=form.endDate.data)

        db.session.add(addMovie)
        db.session.commit()
    return render_template('addMovie.html', theme=get_user_theme(), form=form)

@app.route("/seats/<screening_id>", methods=['GET','POST'])
def seats(screening_id):
    if request.method == 'POST':
        print(request.form.getlist('seat_list'))

    grid_width = 30
    grid_height = 10

    grid = []
    for x in range(grid_width):
        row = []
        for y in range(grid_height):
            row.append(str(x) + "," + str(y))
        grid.append(row)

    screening = Screen.query.filter_by(id=screening_id).first()
    g.movie_id = screening.movie_id
    g.screening_id = screening.id
    movie = Movie.query.all()
    return render_template('seats.html', theme=get_user_theme(), width=grid_width, height=grid_height, grid=grid, movie=movie)

@app.route("/ticket/<id>")
def ticket(id):
    booking = Booking.query.filter_by(id=id).first()
    if not booking:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    screening = Screen.query.filter_by(id=booking.screen_id).first()
    if not screening:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    movie = Movie.query.filter_by(id=screening.movie_id).first()
    if not movie:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    ticket_id=booking.id
    movie_title = movie.name
    screening_date = screening.screen_time
    movie_duration = movie.duration
    screen_number = screening.screen_number
    seat_number = booking.seat_number
    ticket_code = booking.ticket_code

    return render_template('ticket.html', theme=get_user_theme(), title='Your Ticket',
        movie_title=movie_title, screening_date=screening_date, movie_duration=movie_duration,
        screen_number=screen_number, seat_number=seat_number, ticket_code=ticket_code)

@app.route("/ticket/download/<ticket_code>")
def ticket_download(ticket_code):
    booking = Booking.query.filter_by(ticket_code=ticket_code).first()
    if not booking:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    screening = Screen.query.filter_by(id=booking.screen_id).first()
    if not screening:
        return render_template('ticket_not_found.html', title='Invalid Ticket')

    movie = Movie.query.filter_by(id=screening.movie_id).first()
    if not movie:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    ticket_id=booking.id
    movie_title = movie.name
    screening_date = screening.screen_time
    movie_duration = movie.duration
    screen_number = screening.screen_number
    seat_number = booking.seat_number
    ticket_code = booking.ticket_code

    rendered = render_template('ticket_raw.html', title='Your Ticket',
        movie_title=movie_title, screening_date=screening_date, movie_duration=movie_duration,
        screen_number=screen_number, seat_number=seat_number, ticket_code=ticket_code)
    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=ticket.pdf'
    return response

app.route("/ticket/email/<id>")
#@login_required
def ticket_email(id):
    booking = Booking.query.filter_by(id=id).first()
    if not booking:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    screening = Screen.query.filter_by(id=booking.screen_id).first()
    if not screening:
        return render_template('ticket_not_found.html', title='Invalid Ticket')

    movie = Movie.query.filter_by(id=screening.movie_id).first()
    if not movie:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    movie_title = movie.name
    screening_date = screening.screen_time
    movie_duration = movie.duration
    screen_number = screening.screen_number
    seat_number = booking.seat_number
    ticket_code = booking.ticket_code

    member = Member.query.filter_by(id=booking.member_id).first()
    if not member:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    user = User.query.filter_by(id=member.user_id).first()
    if not user:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    message = Message(subject='Your Ticket', recipients=[user.email])
    message.html = render_template('ticket_raw.html', title='Your Ticket',
        movie_title=movie_title, screening_date=screening_date, movie_duration=movie_duration,
        screen_number=screen_number, seat_number=seat_number, ticket_code=ticket_code)
    mail.send(message)

    return redirect(url_for('popular'))
