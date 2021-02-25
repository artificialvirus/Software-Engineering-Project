from flask import Flask

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' 

# db = SQLAlchemy(app)

from cinemawebapp import routes