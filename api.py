from flask import Blueprint, jsonify, request
from app_movieweb.datamanager.data_models import User, Movie, db
import requests


api = Blueprint('api', __name__)


@api.route('/api/message', methods=['GET'])
def get_message():
    return jsonify({'message': 'Hello, world!'})


@api.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{'user_id': user.user_id, 'username': user.username} for user in users]
    return jsonify(user_list)


@api.route('/api/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    user_movies = [{'movie_id': movie.movie_id, 'title': movie.title, 'year': movie.year} for movie in user.movies]
    return jsonify(user_movies)


@api.route('/api/users/<int:user_id>/movies', methods=['POST'])
def add_user_movie(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    title = data.get('title')
    year = data.get('year')

    if not title or not year:
        return jsonify({'error': 'Title and year are required'}), 400

    movie = Movie(title=title, year=year)
    user.movies.append(movie)
    db.session.commit()

    return jsonify({'message': 'Movie added successfully'})


def fetch_movie_details(movie_title):
    api_key = '7b5a0029'
    url = f'http://www.omdbapi.com/?apikey={api_key}&t={movie_title}'

    try:
        response = requests.get(url)
        response.raise_for_status()

        if response.status_code == 200:
            movie_data = response.json()
            return movie_data
        else:
            return {}
    except requests.RequestException as e:
        print("An error occurred during the API request:", str(e))
        return {}
