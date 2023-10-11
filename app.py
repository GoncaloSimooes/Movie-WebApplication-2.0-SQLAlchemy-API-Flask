from flask import Flask, render_template, request, redirect, url_for
from app_movieweb.datamanager.data_models import User, Movie, Review, db
from app_movieweb.datamanager.sql_data_manager import SQLiteDataManager
from app_movieweb.api import api

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

data_manager = SQLiteDataManager(app)

app.register_blueprint(api, url_prefix='/api')


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


@app.route('/users/<int:user_id>')
def get_user_movies(user_id):
    user = User.query.get(user_id)
    user_name = user.username
    user_movies = user.movies
    try:
        reviews = user.get_reviews()
    except Exception as e:
        reviews = []
    return render_template('user_movies.html', user_name=user_name, user_movies=user_movies, user_id=user_id, reviews=reviews)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Adds a new user to the MovieWeb App.
    Returns:
        str: The rendered HTML template for adding a new user.
    """
    if request.method == 'POST':
        username = request.form['username']
        data_manager.add_user(username)
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
    if request.method == 'POST':
        movie_title = request.form['movie_title']
        try:
            movie_data = data_manager.data_api(movie_title)
            if 'Title' not in movie_data or 'Year' not in movie_data:
                raise ValueError("API response is missing required movie information.")
            movie = {
                'title': movie_data['Title'],
                'year': movie_data['Year'],
                'rating': movie_data['imdbRating'],
                'poster': movie_data['Poster'],
                'imdbID': movie_data['imdbID']
            }
            data_manager.add_movie_to_user(user_id, movie)
            return redirect(url_for('get_user_movies', user_id=user_id))
        except ValueError as e:
            return str(e)
    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    if request.method == 'POST':
        new_title = request.form['new_title']
        new_rating = request.form['new_rating']
        success = data_manager.update_movie(user_id, movie_id, new_title, new_rating)
        if success:
            return redirect(url_for('get_user_movies', user_id=user_id))
        else:
            return "Movie not found or update failed."
    movie = data_manager.get_movie(user_id, movie_id)
    if movie:
        return render_template('update_movie.html', user_id=user_id, movie_id=movie_id, title=movie.title, rating=movie.rating)
    else:
        return "Movie not found."


@app.route('/users/<int:user_id>/delete_movie/<string:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(user_id, movie_id)
    return redirect(url_for('get_user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/add_review/<string:movie_id>', methods=['GET', 'POST'])
def add_review(user_id, movie_id):
    if request.method == 'POST':
        review_text = request.form['review_text']
        rating = request.form['rating']
        user = User.query.get(user_id)
        try:
            if not user:
                return render_template('error.html', error_message="User not found.")
            movie = Movie.query.filter_by(movie_id=movie_id).first()
            if not movie:
                return render_template('error.html', error_message="Movie not found.")
            review = Review(user_id=user_id, movie_id=movie.movie_id, review_text=review_text, rating=rating)
            db.session.add(review)
            db.session.commit()
            return redirect(url_for('get_user_movies', user_id=user_id))
        except ValueError as e:
            return str(e)
    user_movies = User.query.get(user_id).movies
    movie_id = int(movie_id)
    movie = next((movie for movie in user_movies if movie.movie_id == movie_id), None)
    reviews = movie.reviews
    return render_template('add_review.html', user_id=user_id, movie=movie, reviews=reviews)


@app.route('/users/<user_id>/movies/<movie_id>/update_review/<review_id>', methods=['GET', 'POST'])
def update_review(user_id, movie_id, review_id):
    if request.method == 'POST':
        try:
            new_review_text = request.form['new_review_text']
            new_rating = int(request.form['new_rating'])

            Review.update_review(review_id, new_review_text, new_rating)

            return redirect(url_for('get_user_movies', user_id=user_id))
        except Exception as e:
            # Handle exceptions related to updating a review
            print("An error occurred while updating a review:", str(e))
            return render_template('error.html', error_message="An error occurred while updating a review")

    review = Review.query.get(review_id)
    movie_id = int(movie_id)
    return render_template('update_review.html', user_id=user_id, movie_id=movie_id, review=review_id)


@app.route('/users/<user_id>/delete_review/<movie_id>/<review_id>', methods=['POST'])
def delete_review(user_id, movie_id, review_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return render_template('404.html', error_message="User not found.")
        movie = Movie.query.filter_by(movie_id=movie_id).first()
        if not movie:
            return render_template('404.html', error_message="Movie not found.")
        review = Review.query.get(review_id)
        if not review:
            return render_template('404.html', error_message="Review not found.")
        db.session.delete(review)
        db.session.commit()
        return redirect(url_for('movie_reviews', user_id=user_id, movie_id=movie_id))
    except Exception as e:
        print("An error occurred while deleting a review:", str(e))
        return render_template('error.html', error_message="An error occurred while deleting a review")


@app.route('/users/<int:user_id>/movies/<string:movie_id>/reviews')
def movie_reviews(user_id, movie_id):
    user_name = data_manager.get_user_name(user_id)
    movie = data_manager.get_movie(user_id, movie_id)
    if not movie:
        return render_template('404.html', error_message="Movie not found.")
    reviews = data_manager.get_reviews_for_movie(movie_id)
    return render_template('movie_reviews.html', user_name=user_name, movie=movie, reviews=reviews, user_id=user_id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
