# coding: utf-8
from flask_app import db
from datetime import datetime


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    author_name = db.Column(db.Unicode, nullable=False)
    votes = db.Column(db.Integer, nullable=False, default=0)
    body = db.Column(db.UnicodeText, nullable=False)
    parent = db.Column(db.Integer, nullable=False, server_default=db.Text("'0'"))
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
    votes = db.Column(db.Integer, nullable=False, default=0)
    solution = db.Column(db.UnicodeText)
    # Relationships
    union_id = db.Column(db.Integer, db.ForeignKey('unions.id'), nullable=False)
    union = db.relationship('Union', backref=db.backref('posts', lazy=True))
    vetoed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, default=None)
    vetoed_by = db.relationship('User', backref=db.backref('vetoes', lazy=True))


class Union(db.Model):
    __tablename__ = 'unions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    union_name = db.Column(db.Unicode, nullable=False)
    password = db.Column(db.Unicode, nullable=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    password = db.Column(db.String, nullable=False)
    username = db.Column(db.Unicode, nullable=False, unique=True)
    authority = db.Column(db.Integer, default=0)
    # relationships
    union_id = db.Column(db.Integer, db.ForeignKey('unions.id'), nullable=False)
    union = db.relationship('Union', backref=db.backref('users', lazy=True))


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255, u'utf8_unicode_ci'), nullable=False)
    type = db.Column(db.String(100, u'utf8_unicode_ci'), nullable=False, server_default=db.Text("'post'"))
    # relationships
    post_id = db.Column(db.Integer, nullable=False)
    post = db.relationship('Post', backref=db.backref('votes', lazy=True))
