from flask import g, render_template, flash, request, redirect, url_for, session, json, make_response
from cinemawebapp import app, mail
from cinemawebapp.models import Member, Admins, User, Movie, Screen, Booking
from .forms import SignUpForm, LoginForm, ResetPasswordRequestForm, MemberForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
import logging
from flask_mail import Mail, Message
from flask_login import login_user, logout_user, login_required, current_user
from cinemawebapp import db, models
from datetime import datetime, timedelta
from sqlalchemy import desc
import pdfkit
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import sys
import random
from random import randrange

def sqlalchemy_to_csv(q_output, excluded_columns=""):
    excluded_columns = set(excluded_columns)
    rows = q_output

    columns = [i for i in rows[0].__dict__]
    for c_name in excluded_columns:
        columns.pop(columns.index(c_name))

    columns.sort()
    csv = ", ".join(columns) + "\n"

    for row in rows:
        for c_name in columns:
            if c_name not in cexcluded_columns:
                data = str(row.__dict__[c_name])
                data.replace('"','""')
                csv += '"' + data + '"' + ","
        csv += "\n"

    return csv

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', theme=get_user_theme()), 404

# Home page
@app.route("/")
@app.route("/home")
def home():
    return redirect(url_for('popular'))

def send_ticket_mail(booking):
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
    ticket_type = booking.ticket_type
    vip = booking.is_vip
    ticket_code = booking.ticket_code

    is_vip = "NO"
    if vip == 1:
        is_vip = "YES"

    member = Member.query.filter_by(id=booking.member_id).first()
    if not member:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    user = User.query.filter_by(id=member.user_id).first()
    if not user:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    message = Message(subject='Your Ticket', recipients=[user.email])
    message.html = render_template('ticket_raw.html', title='Your Ticket',
        movie_title=movie_title, screening_date=screening_date, movie_duration=movie_duration,
        screen_number=screen_number, seat_number=seat_number, ticket_type=ticket_type,
        is_vip=is_vip, ticket_code=ticket_code)
    mail.send(message)

@app.route("/payment/<screening_id>-<seats>")
def payment(screening_id, seats):
    num_adult = 0
    num_child = 0
    num_elder = 0
    num_vip = 0
    seats_data = seats.split("+")
    member = Member.query.filter_by(user_id=current_user.get_id()).first()
    for i in seats_data:
        elements = i.split(";")
        seat_number = elements[0]
        ticket_type = elements[1]
        is_vip = int(elements[2])

        if is_vip == 1:
            num_vip += 1

        if ticket_type == "Adult":
            num_adult += 1
        elif ticket_type == "Child":
            num_child += 1
        elif ticket_type == "Elder":
            num_elder += 1

        ticket_code = str(member.id) + screening_id + seat_number
        booking = Booking(seat_number=seat_number, ticket_type=ticket_type,
        booking_made=datetime.today(), is_vip=is_vip, ticket_code=ticket_code,
        member_id=member.id, screen_id=screening_id)
        db.session.add(booking)
        send_ticket_mail(booking)
    db.session.commit()

    return render_template('payment.html', theme=get_user_theme(),
        num_adult=num_adult, num_child=num_child, num_elder=num_elder,
        num_vip=num_vip)

@app.route("/popular")
def popular():
    bookings = Booking.query.all()
    if not bookings:
        return render_template('popular.html', theme=get_user_theme(), title='popular', movies=[])

    movies = {}
    movie_data = Movie.query.all()
    for movie in movie_data:
        movies[movie.id] = 0

    for booking in bookings:
        screening = Screen.query.filter_by(id=booking.screen_id).first()
        if screening:
            movie = Movie.query.filter_by(id=screening.movie_id).first()
            if movie:
                movies[movie.id] += 1

    popular = []
    for i in range(len(movies)):
        id = max(movies, key=movies.get)
        popular.append(id)
        del movies[id]

    result = []
    for i in popular:
        movie = Movie.query.filter_by(id=i).first()
        result.append(movie)

    return render_template('popular.html', theme=get_user_theme(), title='popular', movies=result)

# For you page
@app.route("/foryou")
def foryou():
    movies = Movie.query.all()
    new_release = Movie.query.order_by( desc("releaseDate")).limit(10)
    return render_template('foryou.html', theme=get_user_theme(), title= 'for you' , movies=movies)

# Search page
@app.route("/search", methods=['GET','POST'])
def search():
    class Forms:
        pass
    forms = Forms();

    if request.method == 'POST':
        forms.search_title = request.form.getlist('search_title')[0]
        forms.genres = request.form.getlist('genres')
        select = request.form.get('order')
    else:
        forms.search_title = ""
        forms.genres = []
        select = ""

    # print(vars(forms))
    i = len(forms.genres) - 1
    if select == "Newest" :
        if i == -1 :
            movies = Movie.query.filter( ((Movie.name.contains(forms.search_title) | Movie.description.contains(forms.search_title) )& Movie.available==True)).order_by(desc(Movie.releaseDate))
        else:
            movies = Movie.query.filter( ((Movie.name.contains(forms.search_title) | Movie.description.contains(forms.search_title) )& (Movie.genre.contains(forms.genres[i]))& Movie.available==True)).order_by(desc(Movie.releaseDate))
    elif select =="Alphabetically":
        if i == -1 :
            movies = Movie.query.filter( ((Movie.name.contains(forms.search_title) | Movie.description.contains(forms.search_title) )& Movie.available==True)).order_by(desc(Movie.name))
        else:
            movies = Movie.query.filter( ((Movie.name.contains(forms.search_title) | Movie.description.contains(forms.search_title) )& (Movie.genre.contains(forms.genres[i]))& Movie.available==True)).order_by(desc(Movie.name))
    else:
       movies = Movie.query.all()
    forms.genres
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

@app.route("/sales")
@login_required
def sales():
    filter_after = datetime.today()
    movies = Movie.query.filter(Movie.releaseDate <= filter_after, filter_after <= Movie.endDate)
    return render_template('sales.html', theme=get_user_theme(), movies=movies)

@app.route("/takingsperweek")
@login_required
def takingsperweek():
    data = []

    overall = 0
    income = 0

    filter_after = datetime.today() - timedelta(days=7)
    bookings = Booking.query.filter(Booking.booking_made >= filter_after)

    if not bookings:
        return redirect(url_for('admin'))

    last_date = bookings[0].booking_made.date()

    for booking in bookings:
        current_date = booking.booking_made.date()
        if current_date > last_date:
            data.append((last_date.strftime('%d/%m/%Y'), income))
            overall += income
            income = 0
            last_date = current_date

        if booking.ticket_type == "Adult":
            income += 10.0
        elif booking.ticket_type == "Child":
            income += 5.0
        elif booking.ticket_type == "Elder":
            income += 7.5

        if booking.is_vip:
            income += 2.25

    data.append((last_date.strftime('%d/%m/%Y'), income))
    overall += income

    label = [row[0] for row in data]
    value = [row[1] for row in data]

    return render_template('takingsperweek.html',theme=get_user_theme(),
        label=label, value=value, income=overall)

@app.route("/takingspermovie/<movie_id>")
@login_required
def takingspermovie(movie_id):
    data = []

    overall = 0
    income = 0

    movie = Movie.query.filter_by(id=movie_id).first()
    if not movie:
        return redirect(url_for('admin'))

    filter_after = datetime.today() - timedelta(days=7)
    bookings = Booking.query.filter(Booking.booking_made >= filter_after)

    if not bookings:
        return redirect(url_for('admin'))

    last_date = bookings[0].booking_made.date()

    for booking in bookings:
        screening = Screen.query.filter_by(id=booking.screen_id).first()
        if not screening:
            continue

        movie_booking = Movie.query.filter_by(id=screening.movie_id).first()
        if not movie_booking:
            continue

        if int(movie_id) != int(movie_booking.id):
            continue

        current_date = booking.booking_made.date()
        if not current_date == last_date:
            if not income == 0:
                data.append((last_date.strftime('%d/%m/%Y'), income))
                overall += income
                income = 0
            last_date = current_date

        if booking.ticket_type == "Adult":
            income += 10.0
        elif booking.ticket_type == "Child":
            income += 5.0
        elif booking.ticket_type == "Elder":
            income += 7.5

        if booking.is_vip:
            income += 2.25

    data.append((last_date.strftime('%d/%m/%Y'), income))
    overall += income

    label = [row[0] for row in data]
    value = [row[1] for row in data]

    return render_template('takingspermovie.html',theme=get_user_theme(),
        label=label, value=value, income=overall, name=movie.name)

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

        member = Member(user_id=user.id)
        db.session.add(member)
        db.session.commit()

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
        payment = Member(phone=form.phone.data,date_of_birth=form.date_of_birth.data)
        db.session.add(payment)
        db.session.commit()

    member = Member.query.filter_by(user_id=current_user.get_id()).first()
    bookings = Booking.query.filter_by(member_id=member.id)
    if not bookings:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    movies = []
    for i in bookings:
        screening = Screen.query.filter_by(id=i.screen_id).first()
        date = screening.screen_time
        movie = Movie.query.filter_by(id=screening.movie_id).first()
        name = movie.name
        movies.append([i.id, name, date, i.ticket_type])

    return render_template('member.html',theme=get_user_theme(),form=form,bookings=movies)

@app.route("/seats/<screening_id>", methods=['GET','POST'])
@login_required
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
    return render_template('seats.html', theme=get_user_theme(), width=grid_width, height=grid_height, grid=grid, screening_id=screening.id, movie_id=screening.movie_id)

@app.route("/ticket/<id>")
@login_required
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
    ticket_type = booking.ticket_type
    vip = booking.is_vip
    ticket_code = booking.ticket_code

    is_vip = "NO"
    if vip == 1:
        is_vip = "YES"

    return render_template('ticket.html', theme=get_user_theme(), title='Your Ticket',
        movie_title=movie_title, screening_date=screening_date, movie_duration=movie_duration,
        screen_number=screen_number, seat_number=seat_number, ticket_type=ticket_type,
        is_vip=is_vip, ticket_code=ticket_code)

@app.route("/ticket/download/<ticket_code>")
@login_required
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
    ticket_type = booking.ticket_type
    vip = booking.is_vip
    ticket_code = booking.ticket_code

    is_vip = "NO"
    if vip == 1:
        is_vip = "YES"

    rendered = render_template('ticket_raw.html', title='Your Ticket',
        movie_title=movie_title, screening_date=screening_date, movie_duration=movie_duration,
        screen_number=screen_number, seat_number=seat_number, ticket_type=ticket_type,
        is_vip=is_vip, ticket_code=ticket_code)
    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=ticket.pdf'
    return response
