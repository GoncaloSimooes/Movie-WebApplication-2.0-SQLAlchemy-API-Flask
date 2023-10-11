from app_movieweb.datamanager.data_manager_interface import DataManagerInterface
from app_movieweb.datamanager.data_models import User, Movie, Review, db
import requests

api_request = "http://www.omdbapi.com/"


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app):
        """
        Initializes the SQLiteDataManager with a Flask application instance and the SQLAlchemy database.

        Args:
            app: The Flask application instance.
        """
        self.app = app
        self.db = db

    def get_all_users(self):
        """
        Gets all users in the database.

        Returns:
            A list of User objects representing all users.
        """
        return User.query.all()

    def get_user_movies(self, user_id):
        """
        Gets all movies for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            A list of Movie objects representing the user's movies, each with associated reviews.
        """
        user = self.db.session.get(User, user_id)
        if user:
            return user.movies
        return []

    def get_user_name(self, user_id):
        """
        Gets the username of a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            The username of the user or None if the user is not found.
        """
        user = self.db.session.get(User, user_id)
        if user:
            return user.username
        return None

    def add_user(self, username):
        """
        Adds a new user to the database.

        Args:
            username: The username of the new user.
        """
        new_user = User(username=username)
        self.db.session.add(new_user)
        self.db.session.commit()

    def delete_user(self, user_id):
        """
        Deletes a user from the database and associated movies.

        Args:
            user_id: The ID of the user to be deleted.
        """
        user = self.db.session.get(User, user_id)
        if user:
            # Delete associated movies first
            for movie in user.movies:
                self.db.session.delete(movie)
            self.db.session.delete(user)
            self.db.session.commit()

    def add_movie_to_user(self, user_id, movie):
        """
        Adds a movie to a user's collection.

        Args:
            user_id: The ID of the user.
            movie: A dictionary containing movie information (title, year, rating, poster, imdbid).
        """
        user = self.db.session.get(User, user_id)
        if user:
            new_movie = Movie(
                title=movie['title'],
                year=movie['year'],
                rating=movie['rating'],
                user_id=user_id,
                poster=movie['poster'],
                imdbID=movie['imdbID'],  # Corrected the reference to 'imdbID'
            )
            self.db.session.add(new_movie)
            self.db.session.commit()

    def update_movie(self, user_id, movie_id, new_title, new_rating):
        """
        Updates the title and rating of a movie in a user's collection.

        Args:
            user_id: The ID of the user.
            movie_id: The ID of the movie to be updated.
            new_title: The new title of the movie.
            new_rating: The new rating of the movie.

        Returns:
            True if the update is successful, False if the movie is not found.
        """
        movie = self.db.session.get(Movie, movie_id)
        if movie and movie.user_id == user_id:
            movie.title = new_title
            movie.rating = new_rating
            self.db.session.commit()
            return True
        else:
            return False

    def delete_movie(self, user_id, movie_id):
        """
        Deletes a movie from a user's collection.

        Args:
            user_id: The ID of the user.
            movie_id: The ID of the movie to be deleted.
        """
        movie = self.db.session.get(Movie, movie_id)
        if movie and movie.user_id == user_id:
            self.db.session.delete(movie)
            self.db.session.commit()

    def get_reviews_for_movie(self, movie_id):
        """
        Gets reviews for a specific movie.

        Args:
            movie_id: The ID of the movie.

        Returns:
            A list of Review objects representing the reviews for the movie.
        """
        movie = self.db.session.get(Movie, movie_id)
        if movie:
            return movie.reviews
        return []

    def get_movie(self, user_id, movie_id):
        # Recupere um filme específico com base no user_id e no movie_id
        movie = self.db.session.get(Movie, movie_id)
        return movie

    def add_review(self, user_id, movie_id, review_text, rating):
        """
        Adiciona uma revisão a um filme na lista de filmes de um usuário.

        Args:
            user_id (int): O ID do usuário.
            movie_id (str): O ID do filme.
            review_text (str): O texto da revisão.
            rating (int): A classificação da revisão.

        Raises:
            ValueError: Se o filme ou usuário não for encontrado.
        """
        user = self.db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")

        movie = self.db.session.get(Movie, movie_id)
        if not movie:
            raise ValueError(f"Movie with ID {movie_id} not found.")

        review = Review(user_id=user_id, movie_id=movie_id, review_text=review_text, rating=rating)
        self.db.session.add(review)
        self.db.session.commit()

    def save_data(self, user_id, movies):
        """
        Saves updated movie data for a user.

        Args:
            user_id: The ID of the user.
            movies: A list of Movie objects representing the updated movies.
        """
        user = self.db.session.get(User, user_id)
        if user:
            user.movies = movies
            self.db.session.commit()

    def data_api(self, title_movie):
        """
        Queries the OMDB API to get movie information based on the title.

        Args:
            title_movie: The title of the movie to search for in the API.

        Returns:
            A dictionary containing movie information or raises a ValueError if the movie is not found.
        """
        apikey = "7b5a0029"
        params = {'t': title_movie, 'apikey': apikey}
        response = requests.get(api_request, params=params)
        response_json = response.json()
        if response_json.get('Response') == 'False':
            raise ValueError(f"Could not find a movie with title '{title_movie}'.")
        return response_json

    def get_user(self, user_id):
        pass
