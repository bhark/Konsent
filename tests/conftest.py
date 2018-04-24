"""Use the power of the mock with discipline, and remember:
Mock always where you use the object, not where it comes from.
"""
import datetime

import konsent
from konsent import make_app, login_manager

from flask import template_rendered

from unittest.mock import MagicMock
import pytest


@pytest.fixture(autouse=True)
def test_app(user_mock, orm_mock, forms_mock):
    app = make_app(db_uri=None)
    app.config['TESTING'] = True
    app.secret_key = 'test_views'
    # turn off flask-login
    app.config['LOGIN_DISABLED'] = True
    login_manager.init_app(app)
    return app


# http://flask.pocoo.org/docs/0.12/signals/#subscribing-to-signals
@pytest.fixture()
def context(test_app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, test_app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, test_app)


@pytest.fixture()
def client(test_app):
    with test_app.test_client() as client:
        yield client


@pytest.fixture()
def client_logged(test_app):

    data = {'username': 'test_user',
            'password': 'test_password'}

    with test_app.test_client() as client:
        client.post('/login', data=data)
        yield client


@pytest.fixture()
def user_mock(mocker):
    User_mock = mocker.patch('konsent.User')
    mocker.patch('konsent.views.phase1.User', User_mock)
    mocker.patch('konsent.views.authentication.User', User_mock)

    user_stab = MagicMock()
    user_stab.union.union_name = 'test_union'
    user_stab.union_id = '1'
    user_stab.id = '1'

    User_mock.query.get.return_value = user_stab
    query = User_mock.query.filter().first
    query.return_value = user_stab
    query().get_id.return_value = 1
    User_mock.query.filter().count.return_value = 1

    check_password = mocker.patch('konsent.views.authentication.check_password')
    check_password.return_value = True
    mocker.patch('konsent.views.authentication.hash_password')

    return locals()


@pytest.fixture()
def orm_mock(mocker, request):
    db = MagicMock()
    mocker.patch('konsent.views.phase1.db', db)
    mocker.patch('konsent.views.phase2.db', db)
    mocker.patch('konsent.views.authentication.db', db)
    mocker.patch('konsent.views.other.db', db)

    Post_mock = MagicMock()
    mocker.patch('konsent.views.phase1.Post', Post_mock)
    mocker.patch('konsent.views.phase2.Post', Post_mock)
    mocker.patch('konsent.views.phase3.Post', Post_mock)
    mocker.patch('konsent.views.other.Post', Post_mock)

    post_stub = MagicMock()
    post_stub.union_id = '1'
    post_stub.resting_time = 1
    post_stub.votes_count = 1000

    Post_mock.query.filter().all.return_value = [post_stub]

    Post_mock.query.filter().filter().all.return_value = [post_stub]
    Post_mock.create_date = datetime.datetime.now()

    Post_mock.query.get.return_value = post_stub

    Union_mock = mocker.patch('konsent.views.other.Union')
    mocker.patch('konsent.views.authentication.Union', Union_mock)
    union_stub = Union_mock.query.filter().first()

    Vote_mock = MagicMock()
    mocker.patch('konsent.views.phase1.Vote', Vote_mock)
    mocker.patch('konsent.views.other.Vote', Vote_mock)
    Vote_query = Vote_mock.query.filter().first

    Comment_mock = MagicMock()
    mocker.patch('konsent.views.phase2.Comment', Comment_mock)
    mocker.patch('konsent.views.other.Comment', Comment_mock)
    comment_stub = MagicMock()
    Comment_mock.return_value = comment_stub
    Comment_mock.query.get.return_value = comment_stub

    return locals()


@pytest.fixture()
def forms_mock(mocker):
    UpvoteForm_mock = mocker.patch('konsent.views.phase1.UpvoteForm')
    UpvoteForm_mock().validate.return_value = True

    CommentForm_mock = mocker.patch('konsent.views.phase2.CommentForm')
    CommentForm_mock().validate.return_value = True

    RegisterForm_mock = mocker.patch('konsent.views.authentication.RegisterForm')
    RegisterForm_mock().validate.return_value = True

    RegisterUnionForm_mock = mocker.patch('konsent.views.authentication.RegisterUnionForm')
    RegisterUnionForm_mock().validate.return_value = True

    ArticleForm_mock = mocker.patch('konsent.views.other.ArticleForm')
    article_stub = MagicMock()
    ArticleForm_mock.return_value = article_stub
    ArticleForm_mock().validate.return_value = True
    ArticleForm_mock().resting_time.data = 1

    VetoForm_mock = mocker.patch('konsent.views.other.VetoForm')
    VetoForm_mock().validate.return_value = True

    return locals()
