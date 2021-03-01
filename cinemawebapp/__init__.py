from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' 

app.config.from_pyfile("config.py")

db = SQLAlchemy(app)

migrate = Migrate(app, db)

from cinemawebapp import routes
