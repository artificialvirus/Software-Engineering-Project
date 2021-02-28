from flask import current_app, url_for
from datetime import datetime
from time import time
import jwt
from database import db
from database import login
from sqlalchemy.orm import relationship
from flask_login import UserMixin

#Boiking System Database elements

#Many to many relationship


#UserMixin uses appropriate model for user database

member_booking = db.Table('member_booking', db.Model.metadata, db.Column('member_id', db.Integer, db.ForeignKey('member.member_id')), db.Column('booking_id', db.Integer, db.ForeignKey(booking.booking_id)))

guest_booking = db.Table('guest_booking', db.Model.metadata, db.Column('guest_id', db.Integer, db.ForeignKey('guest.guest_id')), db.Column('booking_id', db.Integer, db.ForeignKey(booking.booking_id)))

movie_screening = db.Table('movie_screening', db.Model.metadata, db.Column('movie_id', db.Integer, db.ForeignKey('movie.movie_id')), db.Column('screen_id'), db.Integer, db.ForeignKey(screen.screen_id))


class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_username = db.Column(db.String(150))
    admin_email = db.Column(db.String(150))
    admin_password = db.Column(db.String(150))


class Member(UserMixin, db.Model):
    __tablename__ = 'member'
    member_id = db.Column(db.Integer, primary_key=True)
    member_username = db.Column(db.String(150))
    member_email = db.Column(db.String(150))
    member_password = db.Column(db.String(150))
    member_phoneNumber = db.Column(db.Integer(50))
    member_age = db.Column(db.Integer(5))
    memb_bk = db.Relationship('Booking', backref='member', lazy='dynamic')


class Guest(db.Model):
    __tablename__ = 'guest'
    guest_id = db.Column(db.Integer, primary_key=True)
    guest_email = db.Column(db.String(150))
    gst_bk = db.Relationship('Booking', backref='member', lazy='dynamic')


class Movies(db.Model):
    __tablename__ = 'movie'
    movie_id = db.Column(db.Integer, primary_key=True)
    movie_name = db.Column(db.String(150))
    movie_genre = db.Column(db.String(150))
    movie_ageRate = db.Column(db.String(150))
    movie_releaseDate = db.Column(db.DateTime)
    movie_available = db.Column(db.Boolean)
    movie_sc = db.Relationship('Screen', backref='member', lazy='dynamic')


class Screening(db.Model):
    __tablename__ = 'screen'
    screen_id = db.Column(db.Integer, primary_key=True)
    screen_number = db.Column(db.Integer(5))
    screen_time = db.Column(db.DateTime)
    screen_date = db.Column(db.DateTime)
    #screen_ticket = db.Column(db.Integer(5))
    movieScreen_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'))


class Booking(db.Model):
    __tablename__ = 'booking'
    booking_id = db.Column(db.Integer, primary_key=True)
    ticket_code = db.Column(db.String(150))
    memberBooking_id = db.Column(db.Integer, db.ForeignKey('member.member_id'))
    guestBooking_id = db.Column(db.Integer, db.ForeignKey('guest.guest_id'))
