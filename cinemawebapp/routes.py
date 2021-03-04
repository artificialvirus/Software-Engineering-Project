from flask import render_template
from cinemawebapp import app

# Sample movie data
movies = [
	{
		'director': 'Michael Bay',
		'title' : 'Explosions',
		'description' : 'Boom'
	},
	{
		'director': 'Guy Richie',
		'title' : 'Hilarity',
		'description' : 'A funny film'
	}

]

@app.route("/")
@app.route("/home")
def home():
	# movies = Post.query.all()
	return render_template('home.html', movies=movies)

@app.route("/")
@app.route("/admin")
def admin():
	return render_template('admin.html')
