from flask import current_app, url_for
from datetime import datetime
from time import time
import jwt
from cinemawebapp import db
from cinemawebapp import login
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

#Booking System Database elements

#Many to many relationship

#UserMixin uses appropriate model for user database

member_booking = db.Table('member_booking', db.Model.metadata, db.Column('id', db.Integer, db.ForeignKey('member.id')), db.Column('booking_id', db.Integer, db.ForeignKey('booking.booking_id')))

guest_booking = db.Table('guest_booking', db.Model.metadata, db.Column('guest_id', db.Integer, db.ForeignKey('guest.guest_id')), db.Column('booking_id', db.Integer, db.ForeignKey('booking.booking_id')))

movie_screening = db.Table('movie_screening', db.Model.metadata, db.Column('movie_id', db.Integer, db.ForeignKey('movie.movie_id')), db.Column('screen_id', db.Integer, db.ForeignKey('screen.screen_id')))




class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150))
    password = db.Column(db.String(150))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_password_token(self, expires=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires},
            current_app.config['SECRET_KEY'],
            algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return Admin.query.get(id)

@login.user_loader
def load_user(id):
    return Admin.query.get(int(id))


class Member(UserMixin, db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150))
    password = db.Column(db.String(150))
    phoneNumber = db.Column(db.Integer())
    age = db.Column(db.Integer())
    memb_bk = db.relationship('Booking', backref='member', lazy='dynamic')

    #Generate password hashes
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    #To reset password
    def get_reset_password_token(self, expires=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires},
            current_app.config['SECRET_KEY'],
            algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return Member.query.get(id)

@login.user_loader
def load_user(id):
    return Member.query.get(int(id))


class Guest(db.Model):
    __tablename__ = 'guest'
    guest_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    gst_bk = db.relationship('Booking', backref='guest', lazy='dynamic')


class Movies(db.Model):
    __tablename__ = 'movie'
    movie_id = db.Column(db.Integer, primary_key=True)
    movie_name = db.Column(db.String(150))
    movie_genre = db.Column(db.String(150))
    movie_ageRate = db.Column(db.String(150))
    movie_releaseDate = db.Column(db.DateTime)
    movie_available = db.Column(db.Boolean)
    movie_sc = db.relationship('Screening', backref='movie', lazy='dynamic')


class Screening(db.Model):
    __tablename__ = 'screen'
    screen_id = db.Column(db.Integer, primary_key=True)
    screen_number = db.Column(db.Integer())
    screen_time = db.Column(db.DateTime)
    screen_date = db.Column(db.DateTime)
    #screen_ticket = db.Column(db.Integer(5))
    movieScreen_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'))


class Booking(db.Model):
    __tablename__ = 'booking'
    booking_id = db.Column(db.Integer, primary_key=True)
    ticket_code = db.Column(db.String(150))
    booking_time = db.Column(db.DateTime, default=datetime.now())
    num_of_booking = db.Column(db.String(100))
    movie_name = db.Column(db.String(150))
    payment_type = db.Column(db.String(150))
    card_id = db.Column(db.String(15))
    card_sec_code = db.Column(db.String(4))
    #booked_movie = db.relationship('Movies', backref='movie', lazy='dynamic')
    memberBooking_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    guestBooking_id = db.Column(db.Integer, db.ForeignKey('guest.guest_id'))
    #movieBooking_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'))

        #Used this to hide card security number which can make it more secure
    def set_password(self, card_sec_code):
        self.card_sec_code = generate_password_hash(card_sec_code)

    def check_password(self, card_sec_code):
        return check_password_hash(self.card_sec_code, card_sec_code)


class Income(db.Model):
    __tablename__ = 'income'
    id = db.Column(db.Integer, primary_key = True)
