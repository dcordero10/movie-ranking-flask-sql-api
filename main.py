from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import text
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, URL
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///my-movies.db"
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=True)
    year = db.Column(db.Integer, unique=False, nullable=True)
    description = db.Column(db.String(750), unique=True, nullable=True)
    rating = db.Column(db.Float, unique=False, nullable=True)
    ranking = db.Column(db.Float, unique=False, nullable=True)
    review = db.Column(db.String(750), unique=True, nullable=True)
    img_url = db.Column(db.String(750), unique=True, nullable=True)

db.create_all()

class Form(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    year = IntegerField()
    description = StringField('Description', validators=[DataRequired()])
    rating = IntegerField()
    ranking = IntegerField()
    review = StringField('Review', validators=[DataRequired()])
    img_url = StringField('Img URL', validators=[DataRequired()])
    submit = SubmitField('Submit')



@app.route("/")
def home():
    all_movies = db.session.query(Movie).order_by(text("ranking desc"))



    return render_template("index.html", movies=all_movies)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    print("done")
    movie_id = request.args.get("id")
    current_movie = Movie.query.get(movie_id)
    db.session.delete(current_movie)
    db.session.commit()

    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add():
    form = Form()
    if form.validate_on_submit():
        new_movie = Movie(
            title=form.title.data,
            year=form.year.data,
            description=form.description.data,
            rating=form.rating.data,
            ranking=form.ranking.data,
            review=form.review.data,
            img_url=form.img_url.data
        )
        db.session.add(new_movie)
        db.session.commit()
    return render_template("add.html", form=form)

class Smartadd(FlaskForm):
    title = StringField("Type a movie title")
    submit = SubmitField("Done")

@app.route("/smartadd", methods=["GET", "POST"])
def smart_add():
    form = Smartadd()
    if form.validate_on_submit():
        title_search = form.title.data
        params = {
            "query": title_search,
            "api_key": os.environ["API_KEY"]
        }
        response = requests.get(url="https://api.themoviedb.org/3/search/movie?", params=params)
        movie_response = response.json()
        overview = movie_response["results"][0]["overview"]
        poster_path = movie_response["results"][0]["poster_path"]
        year = movie_response["results"][0]["release_date"].split("-")[0]
        title = movie_response["results"][0]["original_title"]
        rating = movie_response["results"][0]["vote_average"]
        print
        print(year)
        print(overview)
        print(poster_path)
        print(rating)
        new_movie = Movie(
            title=title,
            year=year,
            description=overview,
            rating=rating,
            ranking=rating,
            review=overview,
            img_url= f"https://www.themoviedb.org/t/p/w600_and_h900_bestv2{poster_path}"
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))


    return render_template("smart-add.html", form=form)


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RateMovieForm()

    movie_id = request.args.get("id")
    current_movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        new_rating = float(form.rating.data)
        new_review = form.review.data
        current_movie.rating = new_rating
        current_movie.review = new_review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, title=current_movie.title, rating=current_movie.rating,
                           review=current_movie.review
                           )



if __name__ == '__main__':
    app.run(debug=True)
