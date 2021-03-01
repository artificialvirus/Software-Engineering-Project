from config import SQLALCHEMY_DATABASE_URI
from cinemawebapp import db
import os.path

#Creates the database for cinemawebapp
db.create_all()
