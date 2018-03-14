# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String, Text, text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Comment(Base):
    __tablename__ = 'comments'

    author = Column(String(100, u'utf8_unicode_ci'), nullable=False)
    votes = Column(Integer, nullable=False, server_default=text("'0'"))
    body = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    id = Column(Integer, primary_key=True)
    parent = Column(Integer, nullable=False, server_default=text("'0'"))
    post_id = Column(Integer, nullable=False)


class Post(Base):
    __tablename__ = 'posts'

    author = Column(String(100, u'utf8_unicode_ci'), nullable=False)
    belongs_to_union = Column(String(100, u'utf8_unicode_ci'), nullable=False)
    body = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    id = Column(Integer, primary_key=True)
    phase = Column(Integer, nullable=False, server_default=text("'1'"))
    title = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    votes = Column(Integer, nullable=False, server_default=text("'0'"))
    solution = Column(Text(collation=u'utf8_unicode_ci'))
    vetoed_by = Column(String(100, u'utf8_unicode_ci'))


class Union(Base):
    __tablename__ = 'unions'

    id = Column(Integer, primary_key=True)
    union_name = Column(String(255, u'utf8_unicode_ci'), nullable=False)
    password = Column(String(255, u'utf8_unicode_ci'), nullable=False)


class User(Base):
    __tablename__ = 'users'

    connected_union = Column(String(255, u'utf8_unicode_ci'), nullable=False)
    id = Column(Integer, primary_key=True)
    name = Column(String(255, u'utf8_unicode_ci'), nullable=False)
    password = Column(String(255, u'utf8_unicode_ci'), nullable=False)
    username = Column(String(255, u'utf8_unicode_ci'), nullable=False)
    authority = Column(Integer, server_default=text("'0'"))


class Vote(Base):
    __tablename__ = 'votes'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, nullable=False)
    username = Column(String(255, u'utf8_unicode_ci'), nullable=False)
    type = Column(String(100, u'utf8_unicode_ci'), nullable=False, server_default=text("'post'"))
