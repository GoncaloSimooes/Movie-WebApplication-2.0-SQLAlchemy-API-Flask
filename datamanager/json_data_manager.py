import json
from abc import ABC
import requests
from data_manager_interface import DataManagerInterface

api_request = "http://www.omdbapi.com/?apikey=1c26b87f"


class JSONDataManager(DataManagerInterface, ABC):
    def __init__(self, filename):
        """
        Initializes a JSONDataManager object.
        """
        self.filename = filename
        self.data = []
        self.load_data()

    def load_data(self):
        """
        Loads data from the JSON file and updates the internal data attribute.
        """
        try:
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = []

    def data_api(self, title_movie):
        """Makes a request to the OMDB API and returns the JSON response."""
        params = {'t': title_movie}
        response = requests.get(api_request, params)
        response_json = response.json()
        if response_json.get('Response') == 'False':
            raise ValueError(f"Could not find movie with title '{title_movie}'.")
        return response_json

    def save_data(self, user_id):
        """
        Saves the data to the JSON file.
        """
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)

    def get_all_users(self):
        """
        Retrieves a list of all users in the MovieWeb App.

        Returns:
            list: A list of dictionaries containing user information, with keys 'ID' and 'name'.
        """

        users = []
        for user_data in self.data:
            users.append({
                'ID': int(user_data['ID']),
                'name': user_data['name']
            })
        return users

    def get_user_movies(self, user_id):
        """
        Retrieves the list of movies for a specific user in the MovieWeb App.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of dictionaries containing movie information for the specified user.
        """
        user_movies = []
        for user_data in self.data:
            if user_data['ID'] == int(user_id):
                user_movies = user_data["movies"]
                break
        return user_movies

    def get_user_name(self, user_id):
        """
        Retrieves the name of a specific user in the MovieWeb App.

        Args:
            user_id (int): The ID of the user.

        Returns:
            str or None: The name of the user if found, otherwise None.
        """
        for user_data in self.data:
            if user_data['ID'] == int(user_id):
                return user_data["name"]
            return None

    def add_user(self, user_name):
        """
        Adds a new user.

        Args:
            user_name (dict): The user object to be added.
        """
        next_id = max([user['ID'] for user in self.data]) + 1 if self.data else 1
        user_name['ID'] = next_id
        self.data.append(user_name)
        self.save_data(next_id)

    def delete_user(self, user_id):
        """
        Deletes a user.

        Args:
            user_id (int): The ID of the user to be deleted.
        """
        self.data = [user for user in self.data if user['ID'] != user_id]
        self.save_data(user_id)

    def add_movie_to_user(self, user_id, movie):
        """
        Adds a movie to a user's collection.

        Args:
            user_id (int): The ID of the user.
            movie (dict): The movie object to be added.

        Raises:
            ValueError: If the user with the specified ID is not found.
        """
        self.load_data()
        for user in self.data:
            if user['ID'] == user_id:
                user['movies'].append(movie)
                self.save_data(user_id)
                return
        raise ValueError(f"User with ID {user_id} not found.")

    def update_movie(self, user_id, movie_id, new_title, new_rating):
        """
        Updates the title and rating of a movie in a user's collection.

        Args:
            user_id (int): The ID of the user.
            movie_id (int): The ID of the movie.
            new_title (str): The new title of the movie.
            new_rating (float): The new rating of the movie.

        Raises:
            ValueError: If the user or movie is not found.
        """
        user = next((user for user in self.data if user['ID'] == user_id), None)
        if user:
            movie = next((movie for movie in user['movies'] if movie['imdb_ID'] == movie_id), None)
            if movie:
                movie['title'] = new_title
                movie['rating'] = new_rating
                self.save_data(user_id)
            else:
                raise ValueError(f"Movie with ID {movie_id} not found for user with ID {user_id}.")
        else:
            raise ValueError(f"User with ID {user_id} not found.")

    def delete_movie(self, user_id, movie_id):
        """
        Deletes a movie from a user's collection.

        Args:
            user_id (int): The ID of the user.
            movie_id (str): The ID of the movie to be deleted.
        """
        user = next((user for user in self.data if user['ID'] == user_id), None)
        if user:
            user['movies'] = [movie for movie in user['movies'] if movie['imdb_ID'] != movie_id]
            self.save_data(user_id)
        else:
            raise ValueError(f"User with ID {user_id} not found.")



