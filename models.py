# coding: utf-8
from flask_app import db


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.Unicode, nullable=False)
    votes = db.Column(db.Integer, nullable=False, default=0)
    body = db.Column(db.UnicodeText, nullable=False)
    parent = db.Column(db.Integer, nullable=False, server_default=db.Text("'0'"))
    # relationships
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('posts', lazy=True))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100, u'utf8_unicode_ci'), nullable=False)
    belongs_to_union = db.Column(db.String(100, u'utf8_unicode_ci'), nullable=False)
    body = db.Column(db.Text(collation=u'utf8_unicode_ci'), nullable=False)
    create_date = db.Column(DateTime, nullable=False, server_default=db.Text("CURRENT_TIMESTAMP"))
    phase = db.Column(db.Integer, nullable=False, server_default=db.Text("'1'"))
    title = db.Column(db.Text(collation=u'utf8_unicode_ci'), nullable=False)
    votes = db.Column(db.Integer, nullable=False, server_default=db.Text("'0'"))
    solution = db.Column(db.Text(collation=u'utf8_unicode_ci'))
    vetoed_by = db.Column(db.String(100, u'utf8_unicode_ci'))


class Union(db.Model):
    __tablename__ = 'unions'

    id = db.Column(db.Integer, primary_key=True)
    union_name = db.Column(db.String(255, u'utf8_unicode_ci'), nullable=False)
    password = db.Column(db.String(255, u'utf8_unicode_ci'), nullable=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    connected_union = db.Column(db.String(255, u'utf8_unicode_ci'), nullable=False)
    name = db.Column(db.String(255, u'utf8_unicode_ci'), nullable=False)
    password = db.Column(db.String(255, u'utf8_unicode_ci'), nullable=False)
    username = db.Column(db.String(255, u'utf8_unicode_ci'), nullable=False)
    authority = db.Column(db.Integer, server_default=db.Text("'0'"))


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(255, u'utf8_unicode_ci'), nullable=False)
    type = db.Column(db.String(100, u'utf8_unicode_ci'), nullable=False, server_default=db.Text("'post'"))
