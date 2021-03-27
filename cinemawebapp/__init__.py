from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail, Message

import logging

from logging.handlers import SMTPHandler

import os

from flask_qrcode import QRcode

app = Flask(__name__)
qrcode = QRcode(app)

app.config.from_pyfile("config.py")

mail = Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

logging.basicConfig(filename= 'debug.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

login = LoginManager()
#We need to make login page to use this
login.login_view = 'login'
login.init_app(app)

from .models import Admin, Member, User, Movie, Screen, Booking

@app.before_first_request
def create_tables():
    from .models import Admin, Member, User, Movie, Screen, Booking
    db.create_all()

from cinemawebapp import routes, models
