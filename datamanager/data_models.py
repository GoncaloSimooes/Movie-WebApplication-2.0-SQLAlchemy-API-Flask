from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define the UserMovie association table
user_movie_association = db.Table('user_movie_association',
                                  db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')),
                                  db.Column('movie_id', db.Integer, db.ForeignKey('movie.movie_id'))
                                  )


class User(db.Model):
    """
    Model class representing a user.

    Attributes:
        user_id (int): The primary key for the user.
        username (str): The username of the user.
        movies (relationship): A relationship to the Movie model.

    Methods:
        __repr__: Returns a string representation of the user.
        add_user: Adds a new user to the database.
        delete_user: Deletes a user from the database.

    """
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    movies = db.relationship('Movie', backref='user', lazy=True)

    def __repr__(self):
        return f"user_id={self.user_id}, username='{self.username}'"

    @classmethod
    def add_user(cls, username):
        """
        Adds a new user to the database.

        Args:
            username (str): The username of the new user.
        """
        new_user = cls(username=username)
        db.session.add(new_user)
        db.session.commit()

    @classmethod
    def delete_user(cls, user_id):
        """
        Deletes a user from the database, also updating associated movies.

        Args:
            user_id (int): The ID of the user to be deleted.
        """
        user = cls.query.get(user_id)
        if user:
            # Set the user_id of associated movies to None or delete them
            for movie in user.movies:
                movie.user_id = None  # Set user_id to None
                # Alternatively, you can delete the associated movies:
                # db.session.delete(movie)
            db.session.delete(user)
            db.session.commit()


class Movie(db.Model):
    """
    Model class representing a movie.

    Attributes:
        movie_id (int): The primary key for the movie.
        title (str): The title of the movie.
        year (str): The year of release of the movie.
        rating (str): The rating of the movie.
        user_id (int): The ID of the user who added the movie.
        imdbID (str): The IMDb ID of the movie.
        poster (str): The URL of the movie poster.

    Methods:
        __repr__: Returns a string representation of the movie.
        delete_movie: Deletes a movie from the database.
        update_movie: Updates movie information in the database.
        to_dict: Converts the movie attributes to a dictionary.

    """
    __tablename__ = 'movie'
    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    rating = db.Column(db.String(10), nullable=False, default="N/A")
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    imdbID = db.Column(db.String(30), unique=True, nullable=False)
    poster = db.Column(db.String(100000), nullable=False)

    reviews = db.relationship('Review', backref='movie', cascade='all, delete-orphan')

    def __repr__(self):
        return f"movie_id={self.movie_id}, title='{self.title}', rating='{self.rating}'"

    @classmethod
    def delete_movie(cls, movie_id):
        """
        Deletes a movie from the database.

        Args:
            movie_id (int): The ID of the movie to be deleted.
        """
        movie = cls.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()

    @classmethod
    def update_movie(cls, movie_id, user_id, update_data):
        """
        Updates movie information in the database.

        Args:
            movie_id (int): The ID of the movie to be updated.
            user_id (int): The ID of the user who owns the movie.
            update_data (dict): A dictionary containing the updated movie information.
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        movie = cls.query.get(movie_id)
        if movie:
            # Handle imdbID changes and related database updates here
            if 'imdbID' in update_data:
                # Handle the case where imdbID changes here
                # You may need to update related data accordingly
                pass

            # Update other movie attributes
            movie.title = update_data.get('title', movie.title)
            movie.year = update_data.get('year', movie.year)
            movie.rating = update_data.get('rating', movie.rating)
            # Update more attributes as needed

            db.session.commit()
            return True  # Return True to indicate successful update
        else:
            return False  # Return False if movie doesn't exist

    @classmethod
    def update_movie_info(cls, title, new_title, new_rating):
        """
        Updates the title and rating of a movie in the database.

        Args:
            movie_id (int): The ID of the movie to be updated.
            new_title (str): The new title for the movie.
            new_rating (str): The new rating for the movie.
        """
        movie = cls.query.get(title)
        if movie:
            movie.title = new_title
            movie.rating = new_rating
            db.session.commit()

    def to_dict(self):
        """
        Converts the movie attributes to a dictionary.

        Returns:
            dict: A dictionary containing the movie attributes.
        """
        return {
            'movie_id': self.movie_id,
            'title': self.title,
            'year': self.year,
            'rating': self.rating,
            'poster': self.poster,
            # Add more attributes as needed
        }

    def get_reviews(self):
        return Review.query.filter_by(movie_id=self.movie_id).all()


class Review(db.Model):
    """
    Model class representing a review for a movie.

    Attributes:
        review_id (int): The primary key for the review.
        user_id (int): The ID of the user who wrote the review.
        movie_id (int): The ID of the movie being reviewed.
        review_text (str): The text of the review.
        rating (int): The rating given in the review.

    Methods:
        __repr__: Returns a string representation of the review.
        add_review: Adds a new review to the database.
        delete_review: Deletes a review from the database.
        update_review: Updates a review in the database.
        get_reviews_for_movie: Returns a list of reviews for a specific movie.

    """
    __tablename__ = 'review'
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'), nullable=False)
    review_text = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Review(review_id={self.review_id}, movie_id={self.movie_id}, user_id={self.user_id}, rating={self.rating})"

    @classmethod
    def add_review(cls, user_id, movie_id, review_text, rating):
        new_review = cls(user_id=user_id, movie_id=movie_id, review_text=review_text, rating=rating)
        db.session.add(new_review)
        db.session.commit()

    @classmethod
    def delete_review(cls, review_id):
        review = cls.query.get(review_id)
        if review:
            db.session.delete(review)
            db.session.commit()

    @classmethod
    def update_review(cls, review_id, new_review_text, new_rating):
        review = cls.query.get(review_id)
        if review:
            review.review_text = new_review_text
            review.rating = new_rating
            db.session.commit()

    @classmethod
    def get_reviews_for_movie(cls, movie_id):
        return cls.query.filter_by(movie_id=movie_id).all()
