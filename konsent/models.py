# coding: utf-8
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import hashlib

db = SQLAlchemy()


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    author_name = db.Column(db.Unicode(length=255), nullable=False)
    votes = db.Column(db.Integer, nullable=False, default=0)
    body = db.Column(db.UnicodeText, nullable=False)
    # relationships
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    body = db.Column(db.UnicodeText, nullable=False)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    phase = db.Column(db.Integer, nullable=False, default=1)
    title = db.Column(db.UnicodeText, nullable=False)
    votes_count = db.Column(db.Integer, nullable=False, default=0)
    solution = db.Column(db.UnicodeText)
    # Relationships
    union_id = db.Column(db.Integer, db.ForeignKey('unions.id'), nullable=False)
    union = db.relationship('Union', backref=db.backref('posts', lazy=True))
    vetoed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, default=None)
    vetoed_by = db.relationship('User', backref=db.backref('vetoes', lazy=True))

    @property
    def time_since_create(self):
        """
        assign "posted x minutes/hours ago" values
        """
        if not hasattr(self, '_time_since_create'):
            now = datetime.datetime.now()
            create_date = self.create_date
            time_since = now - create_date
            hours, minutes = time_since.seconds // 3600, (time_since.seconds // 60) % 60
            self._time_since_create = {'hours': hours, 'minutes': minutes}
        return self._time_since_create


class Union(db.Model):
    __tablename__ = 'unions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    union_name = db.Column(db.Unicode(length=255), nullable=False)
    password = db.Column(db.Unicode(length=255), nullable=False)

    def check_password(self, password):
        """
        Checks the validity of the union's password.
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest() == self.password


class User(db.Model):
    __tablename__ = 'users'

    def __init__(self, username, password, name, union):
        self.name = name
        self.password = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
        self.username = username
        self.union = union

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(length=255), nullable=False)
    password = db.Column(db.String(length=255), nullable=False)
    username = db.Column(db.Unicode(length=255), nullable=False, unique=True)
    authority = db.Column(db.Integer, default=0)
    # relationships
    union_id = db.Column(db.Integer, db.ForeignKey('unions.id'), nullable=False)
    union = db.relationship('Union', backref=db.backref('users', lazy=True))


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    # relationships
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    post = db.relationship('Post', backref=db.backref('votes', lazy=True))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    comment = db.relationship('Comment', backref=db.backref('votes', lazy=True))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('votes', lazy=True))
