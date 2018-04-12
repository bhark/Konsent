# coding: utf-8
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

db = SQLAlchemy()

class ExternalDiscussion(db.Model):
    __tablename__ = 'external_discussions'

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, unique=True
    )
    author = db.Column(db.UnicodeText, nullable=False)
    author_name = db.Column(db.UnicodeText, nullable=False)
    url = db.Column(db.UnicodeText, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)

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

    def list_votes(self):
        votes = Vote.query.filter(Vote.comment_id == self.id).all()
        result = []
        for vote in votes:
            author = User.query.filter(User.id == vote.author_id).one()
            result.append(author.username)
        return result


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
    resting_time = db.Column(db.Integer, nullable=False, default=86400) # in seconds, 86400 = 1 day
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

    def __init__(self, title, body, union, author, resting_time, create_date=None):
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
        self.resting_time = resting_time

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

    def list_votes(self):
        votes = Vote.query.filter(Vote.post_id == self.id).all()
        result = []
        for vote in votes:
            author = User.query.filter(User.id == vote.author_id).one()
            result.append(author.username)
        return result

    def list_comments(self, username):
        user = User.query.filter(User.username == username).one()

        # find all comments in database belonging to this specific post
        comments = sorted(self.comments, reverse=True, key=lambda x: x.votes_count)

        # make a tuple with the result
        result = []
        for c in comments:
            comment = {
                'author': c.author.username,
                'body': c.body,
                'votes': c.votes_count,
                'id': c.id}
            user_voted = Vote.query.filter(and_(
                Vote.author_id == user.id,
                Vote.comment_id == c.id
            )).count()
            comment['voted'] = user_voted > 0
            result.append(comment)

        return result

    def list_external_discussions(self):
        external_discussions = ExternalDiscussion.query.filter(
            ExternalDiscussion.post_id == self.id
        )

        # make a tuple with the result
        for e in external_discussions:
            external_discussion = {
                'author': e.author,
                'author_id': e.author_id,
                'url': e.url,
                'post_id': e.post_id
            }

class Union(db.Model):
    __tablename__ = 'unions'

    def __init__(self, union_name, password):
        self.union_name = union_name
        self.password = password

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, unique=True)
    union_name = db.Column(db.Unicode(length=255), nullable=False)
    password = db.Column(db.String(length=255), nullable=False)

    @staticmethod
    def print():
        return [union.union_name for union in Union.query.all()]

    @staticmethod
    def list():
        unions = Union.query.all()

        result = []
        for union in unions:
            result.append((union.union_name, union.union_name))
        return result

    def list_members(self):
        members = User.query.filter(User.union_id == self.id).all()
        return [member.username for member in members]


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
