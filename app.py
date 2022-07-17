# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)


# Создаем неймспэйсы
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


# Модели
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# Схемы
class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


# Роуты
@movies_ns.route('/')
class MoviesView(Resource):

    def get(self):
        movies = db.session.query(Movie)

        args = request.args

        director_id = args.get('director_id')
        if director_id is not None:
            movies = movies.filter(Movie.director_id == director_id)

        genre_id = args.get('genre_id')
        if genre_id is not None:
            movies = movies.filter(Movie.genre_id == genre_id)

        movies = movies.all()

        return movies_schema.dump(movies), 200

    def post(self):
        movie = movie_schema.load(request.json)
        db.session.add(Movie(**movie))
        db.session.commit()

        return "Ok", 201


@movies_ns.route('/<int:id>')
class MovieView(Resource):

    def get(self, id):
        try:
            movie = Movie.query.get(id)
            return movie_schema.dump(movie), 200
        except Exception as e:
            return "", 404

    def put(self, id):
        db.session.query(Movie).filter(Movie.id == id).update(request.json)
        db.session.commit()
        return "", 204

    def delete(self, id):
        db.session.query(Movie).filter(Movie.id == id).delete()
        db.session.commit()
        return "", 204

@directors_ns.route('/')
class DirectorsView(Resource):

    def get(self):
        directors = db.session.query(Director).all()
        return directors_schema.dump(directors), 200


@directors_ns.route('/<int:id>')
class DirectorView(Resource):

    def get(self, id):
        try:
            director = Director.query.get(id)
            return director_schema.dump(director), 200
        except Exception as e:
            return "", 404

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "", 201


@genres_ns.route('/')
class GenresView(Resource):

    def get(self):
        genres = db.session.query(Genre).all()
        return genres_schema.dump(genres), 200


@genres_ns.route('/<int:id>')
class GenreView(Resource):

    def get(self, id):
        try:
            genre = Genre.query.get(id)
            return genre_schema.dump(genre), 200
        except Exception as e:
            return "", 404


if __name__ == '__main__':
    app.run(debug=True)
