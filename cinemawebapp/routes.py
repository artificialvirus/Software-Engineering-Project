from flask import render_template, flash, request, redirect, url_for, session, json, make_response
from cinemawebapp import app
from cinemawebapp.models import Member, Admin, User, Movie, Screen, Booking
from .forms import SignUpForm, LoginForm, ResetPasswordRequestForm, AdminLoginForm, MoviesForm, BookingForm, PaymentForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
import logging
from flask_mail import Mail, Message
from flask_login import login_user, logout_user, login_required, current_user
from cinemawebapp import db, models
from datetime import datetime, timedelta
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

# Sample movie data
movies = [
    {
        'director': 'Michael Bay',
        'title' : '20 Million Miles To Earth',
        'description' : 'Boom',
        'id' : "f3b05c50",
        'poster' : "https://freeclassicimages.com/images/20-Million-Miles-To-Earth-07-movie-poster.jpg"
    },
    {
        'director': 'Guy Richie',
        'title' : '99 Women',
        'description' : 'A funny film',
        'id' : "2c917f21",
        'poster' : "https://freeclassicimages.com/images/99-Women-01-movie-poster.jpg"
    },
    {
        'director': 'Guy Richie',
        'title' : '20th century',
        'description' : 'A funny film',
        'id' : "2c917f21",
        'poster' : "https://freeclassicimages.com/images/20th-century-1934-movie-poster.jpg"
    },
    {
        'director': 'Guy Richie',
        'title' : '13 Rue Madeleine',
        'description' : 'A funny film',
        'id' : "2c917f21",
        'poster' : "https://freeclassicimages.com/images/13-rue-madeleine-1946-movie-poster.jpg"
    }
]
new_release = [
	{
		'director': 'Michael Bay',
		'title' : 'new film',
		'description' : 'Boom',
                'id' : "925da9f",
                'poster' : "https://freeclassicimages.com/images/99-Women-01-movie-poster.jpg"
	},
	{
		'director': 'Guy Richie',
		'title' : 'newer films',
		'description' : 'A funny film',
                'id' : "7faefe57",
                'poster' : "https://freeclassicimages.com/images/99-Women-01-movie-poster.jpg"
	}

]

@app.route("/home")
@login_required
def home():
    redirect(url_for('popular'))

# Home page
@app.route("/")
@app.route("/popular")
def popular():
	# movies = sql query all movies and available sort by n of tickets sold
	# new_releases = sql squery 8 newest movies and available
	return render_template('popular.html', theme=get_user_theme(), title='popular' ,new=new_release,movies=movies)

# For you page
@app.route("/foryou")
def foryou():
	# based on genre?
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

    more_movies = movies * 10;

    # movies = sql movies matching criteria
    return render_template('search.html', theme=get_user_theme(), title='search', movies=more_movies, forms=forms)

#  Individual movie details page
@app.route("/movie/<movie_id>")
def movie(movie_id):
    #for debugging
    random.seed(10)

    class Movie:
        pass
    class MovieDate:
        pass
    class Screening:
        pass

    movie = Movie()
    movie.title = "Film Title"
    movie.movie_dates = []

    for i in range(100):
        if bool(random.getrandbits(1)):
            movie_date = MovieDate()
            movie_date.date = (datetime.today() + timedelta(days=i)).strftime("%m-%d")
            movie_date.screenings = []
            for j in range(7, 22, 4):
                if bool(random.getrandbits(1)):
                    screening = Screening();
                    screening.time = (datetime.now().replace(hour=j, minute=randrange(0, 60, 5))).strftime("%H:%M")
                    screening.id = "a5849e62"
                    movie_date.screenings.append(screening)
            if len(movie_date.screenings) > 0:
                movie.movie_dates.append(movie_date)


    return render_template('movie.html', theme=get_user_theme(), movie=movie)

# About cinema page - not yet implemented
# @app.route("/about")
# def about():
# 	return render_template('about.html', title='about')


#Admin page
@app.route("/admin")
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


@app.route('/logout')
@login_required
def logout():
    app.logger.info('Logout route')
    app.logger.debug('Debug level logging')
    logout_user()
    return redirect(url_for('home'))

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


    #movies = Post.query.all()
    return render_template('seats.html', theme=get_user_theme(), width=grid_width, height=grid_height, grid=grid)

@app.route("/ticket/<id>")
def ticket(id):
    booking = Booking.query.filter_by(id=id).first()
    if not booking:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    screening = Screen.query.filter_by(id=booking.screen_id).first()
    if not screening:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    movie = Movies.query.filter_by(id=screening.movie_id).first()
    if not movie:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    ticket_id=booking.id
    movie_title = movie.name
    screening_date = screening.time
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

    movie = Movies.query.filter_by(id=screening.movie_id).first()
    if not movie:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    ticket_id=booking.id
    movie_title = movie.name
    screening_date = screening.time
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

@app.route("/ticket/email/<id>")
@login_required
def ticket_email(id):
    booking = Booking.query.filter_by(id=id).first()
    if not booking:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    screening = Screen.query.filter_by(id=booking.screen_id).first()
    if not screening:
        return render_template('ticket_not_found.html', title='Invalid Ticket')

    movie = Movies.query.filter_by(id=screening.movie_id).first()
    if not movie:
        return render_template('ticket_not_found.html', theme=get_user_theme(), title='Invalid Ticket')

    ticket_id=booking.id
    movie_title = movie.name
    screening_date = screening.time
    movie_duration = movie.duration
    screen_number = screening.screen_number
    seat_number = booking.seat_number
    ticket_code = booking.ticket_code

    user = User.query.filter_by(id=id).first()

    message = Message(subject='Your Ticket', recipients=[user.email])
    message.html = render_template('ticket_raw.html', title='Your Ticket',
        movie_title=movie_title, screening_date=screening_date, movie_duration=movie_duration,
        screen_number=screen_number, seat_number=seat_number, ticket_code=ticket_code)
    mail.send(message)

    redirect(url_for('popular'))
