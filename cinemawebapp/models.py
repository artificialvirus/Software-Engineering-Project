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

user_member = db.Table('user_member', db.Model.metadata, db.Column('id', db.Integer, db.ForeignKey('user.id')), db.Column('id', db.Integer, db.ForeignKey('member.id')))

movie_screen = db.Table('movie_screening', db.Model.metadata, db.Column('id', db.Integer, db.ForeignKey('movie.id')), db.Column('id', db.Integer, db.ForeignKey('screen.id')))

movie_booking = db.Table('movie_booking', db.Model.metadata, db.Column('id', db.Integer, db.ForeignKey('member.id')), db.Column('id', db.Integer, db.ForeignKey('booking.id')))

screen_booking = db.Table('screen_booking', db.Model.metadata, db.Column('id', db.Integer, db.ForeignKey('screen.id')), db.Column('id', db.Integer, db.ForeignKey('booking.id')))

class Admins(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150))
    password = db.Column(db.String(150))

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
        return Admins.query.get(id)

@login.user_loader
def load_user(id):
    return Admins.query.get(int(id))



class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150))
    password = db.Column(db.String(150))
    user_details = db.relationship('Member', backref='user', lazy='dynamic')

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
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.Integer())
    date_of_birth = db.Column(db.Integer())
    card_number = db.Column(db.String(15))
    card_expiration_date = db.Column(db.DateTime)
    card_cvv = db.Column(db.String(4))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mem_bk = db.relationship('Booking', backref='member', lazy='dynamic')

        #Used this to hide card cvv which can make it more secure
    def set_password(self, card_cvv):
        self.card_cvv = generate_password_hash(card_cvv)

    def check_password(self, card_cvv):
        return check_password_hash(self.card_cvv, card_cvv)


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(150))
    ticket_code = db.Column(db.String(255))
    ticket_type = db.Column(db.String(64))
    #multiple bookings
    #tickets = db.Column(db.Integer())
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    screen_id = db.Column(db.Integer, db.ForeignKey('screen.id'))



class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    duration = db.Column(db.String(150))
    genre = db.Column(db.String(150))
    description = db.Column(db.String(500))
    certificate = db.Column(db.String(150))
    releaseDate = db.Column(db.DateTime)
    #movie end date can be set so movie can be removed from the list
    endDate = db.Column(db.DateTime)
    #to check whether movie is available
    available = db.Column(db.Boolean)
    movie_sc = db.relationship('Screen', backref='movie', lazy='dynamic')
    #movie_bk = db.relationship('Booking', backref='booking', lazy='dynamic')


class Screen(db.Model):
    __tablename__ = 'screen'
    id = db.Column(db.Integer, primary_key=True)
    screen_number = db.Column(db.Integer())
    screen_time = db.Column(db.DateTime)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    scrn_bk = db.relationship('Booking', backref='screen', lazy='dynamic')


class Income(db.Model):
    __tablename__ = 'income'
    id = db.Column(db.Integer, primary_key = True)
