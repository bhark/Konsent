# coding: utf-8
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, unique=True)
    author_name = db.Column(db.Unicode(length=255), nullable=False)
    votes_count = db.Column(db.Integer, nullable=False, default=0)
    body = db.Column(db.UnicodeText, nullable=False)
    # relationships
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))

    def __init__(self, post, author, body, author_name=None):
        if isinstance(post, Post):
            self.post = post
        else:
            self.post_id = post
        if isinstance(author, User):
            self.author = author
            self.author_name = author.name
        else:
            self.author_id = author
            self.author_name = author_name
        self.body = body


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, unique=True)
    body = db.Column(db.UnicodeText, nullable=False)
    create_date = db.Column(
        db.DateTime, nullable=False, default=datetime.now())
    phase = db.Column(db.Integer, nullable=False, default=1)
    title = db.Column(db.UnicodeText, nullable=False)
    votes_count = db.Column(db.Integer, nullable=False, default=0)
    solution = db.Column(db.UnicodeText)
    resting_time_minutes = db.Column(db.Integer, nullable=False, default=1440)
    # Relationships
    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True),
                             foreign_keys=[author_id])
    union_id = db.Column(
        db.Integer, db.ForeignKey('unions.id'), nullable=False)
    union = db.relationship('Union', backref=db.backref('posts', lazy=True))
    vetoed_by_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True, default=None)
    vetoed_by = db.relationship(
        'User', backref=db.backref('vetoes', lazy=True),
        foreign_keys=[vetoed_by_id])

    def __init__(self, title, body, union, author, resting_time_minutes, create_date=None):
        if create_date is None:
            create_date = datetime.now()
        self.title = title
        self.body = body
        if isinstance(union, Union):
            self.union = union
        else:
            self.union_id = union
        if isinstance(author, User):
            self.author = author
        else:
            self.author_id = author
        self.create_date = create_date
        self.resting_time_minutes = resting_time_minutes

    @property
    def time_since_create(self):
        """
        assign "posted x minutes/hours ago" values
        """
        if not hasattr(self, '_time_since_create'):
            now = datetime.now()
            create_date = self.create_date
            time_since = now - create_date
            hours, minutes = time_since.seconds // 3600, (
                time_since.seconds // 60) % 60
            self._time_since_create = {'hours': hours, 'minutes': minutes}
        print(self._time_since_create)
        return self._time_since_create


class Union(db.Model):
    __tablename__ = 'unions'

    def __init__(self, union_name, password):
        self.union_name = union_name
        self.password = password

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, unique=True)
    union_name = db.Column(db.Unicode(length=255), nullable=False)
    password = db.Column(db.String(length=255), nullable=False)


class User(db.Model):
    __tablename__ = 'users'

    def __init__(self, username, password, union):
        self.password = password
        self.username = username
        self.union = union

    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(length=255), nullable=False)
    username = db.Column(db.Unicode(length=191), nullable=False, unique=True)
    authority = db.Column(db.Integer, default=0)
    # relationships
    union_id = db.Column(
        db.Integer, db.ForeignKey('unions.id'), nullable=False)
    union = db.relationship('Union', backref=db.backref('users', lazy=True))


class Vote(db.Model):
    __tablename__ = 'votes'

    def __init__(self, author, target, target_type=None):
        if isinstance(author, User):
            self.author = author
        else:
            self.author_id = author
        if isinstance(target, Post):
            self.post = target
        elif isinstance(target, Comment):
            self.comment = target
        elif target_type == 'post':
            self.post_id = target
        elif target_type == 'comment':
            self.comment_id = target

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, unique=True)
    # relationships
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    post = db.relationship('Post', backref=db.backref('votes', lazy=True))
    comment_id = db.Column(
        db.Integer, db.ForeignKey('comments.id'), nullable=True)
    comment = db.relationship(
        'Comment', backref=db.backref('votes', lazy=True))
    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('votes', lazy=True))
