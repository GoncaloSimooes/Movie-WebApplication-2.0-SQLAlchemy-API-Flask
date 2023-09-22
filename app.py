from flask import Flask, render_template, request, redirect, url_for
from datamanager.json_data_manager import JSONDataManager

app = Flask(__name__)
data_manager = JSONDataManager('movies.json')


@app.route('/')
def home():
    """
    Renders the home page of the MovieWeb App.

    Returns:
        str: The rendered HTML template for the home page.
    """
    return render_template('index.html')


@app.route('/users')
def list_users():
    """
    Lists all users in the MovieWeb App.

    Returns:
        str: The rendered HTML template for the users list page.
    """
    users = data_manager.get_all_users()
    return render_template("users.html", users=users)


@app.route("/users/<int:user_id>")
def get_user_movies(user_id):
    """
    Retrieves and displays movies for a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        str: The rendered HTML template for the user's movies page.
    """
    user_movies = data_manager.get_user_movies(user_id)
    user_name = data_manager.get_user_name(user_id)
    return render_template('user_movies.html', user_name=user_name, user_movies=user_movies, user_id=user_id)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Adds a new user to the MovieWeb App.

    Returns:
        str: The rendered HTML template for adding a new user.
    """
    if request.method == 'POST':
        username = request.form['username']
        user = {
            'name': username,
            'movies': []
        }
        data_manager.add_user(user)
        return redirect(url_for('list_users'))
    return render_template('add_user.html')


@app.route('/users/<int:user_id>/delete_user', methods=['GET', 'POST'])
def delete_user(user_id):
    """
    Deletes a user from the MovieWeb App.

    Args:
        user_id (int): The ID of the user to be deleted.

    Returns:
        str: The rendered HTML template for deleting a user.
    """
    if request.method == 'POST':
        data_manager.delete_user(user_id)
        return redirect(url_for('list_users'))
    return render_template('delete_user.html', user_id=user_id)


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
    Adds a movie to a user's collection in the MovieWeb App.

    Args:
        user_id (int): The ID of the user.

    Returns:
        str: The rendered HTML template for adding a movie.
    """
    if request.method == 'POST':
        movie_title = request.form['movie_title']
        try:
            movie_data = data_manager.data_api(movie_title)

            if 'Title' not in movie_data or 'Year' not in movie_data or 'Poster' not in movie_data:
                raise ValueError("API response is missing required movie information.")

            rating = movie_data.get('Rating')

            movie = {
                'title': movie_data['Title'],
                'year': movie_data['Year'],
                'rating': rating,
                'poster_url': movie_data['Poster'],
                'imdb_ID': movie_data['imdbID']
            }
            data_manager.add_movie_to_user(user_id, movie)
            return redirect(url_for('get_user_movies', user_id=user_id))
        except ValueError as e:
            return str(e)

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<string:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Updates the title and rating of a movie in a user's collection.

    Args:
        user_id (int): The ID of the user.
        movie_id (str): The ID of the movie.

    Returns:
        str: The rendered HTML template for updating a movie.
    """
    if request.method == 'POST':
        new_title = request.form['new_title']
        new_rating = request.form['new_rating']
        data_manager.update_movie(user_id, movie_id, new_title, new_rating)
        return redirect(url_for('get_user_movies', user_id=user_id))
    user_movies = data_manager.get_user_movies(user_id)
    movie = next((movie for movie in user_movies if movie['imdb_ID'] == movie_id), None)
    return render_template('update_movie.html', user_id=user_id, movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<string:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    """
    Deletes a movie from a user's collection in the MovieWeb App.

    Args:
        user_id (int): The ID of the user.
        movie_id (str): The ID of the movie to be deleted.
    """
    data_manager.delete_movie(user_id, movie_id)
    return redirect(url_for('get_user_movies', user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    """
        Renders a custom 404 page when a page is not found.

        Args:
            e: The exception raised for the page not found error.

        Returns:
            str: The rendered HTML template for the 404 page.
        """
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    app.run(debug=True)
