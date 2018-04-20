import datetime

from flask import template_rendered
from konsent import app

from unittest.mock import MagicMock
import pytest


@pytest.fixture()
def client():
    app.config['TESTING'] = True
    app.secret_key = 'test_views'
    with app.test_client() as client:
        yield client


@pytest.fixture
def user_mock(mocker):
    User_mock = mocker.patch('konsent.User')

    user_stab = MagicMock()
    user_stab.union.union_name = 'test_union'
    user_stab.union.id = '1'
    user_stab.id = '1'

    query = User_mock.query.filter().first
    query.return_value = user_stab

    return locals()


@pytest.fixture
def passwd_mock(mocker):
    check_password = mocker.patch('konsent.check_password')
    check_password.return_value = True
    mocker.patch('konsent.hash_password')


@pytest.fixture
def orm_mock(mocker):
    db = mocker.patch('konsent.db')

    Post_mock = mocker.patch('konsent.Post')

    post_stub = MagicMock()
    post_stub.time_since_create = {'hours': 0}
    post_stub.union_id = '1'

    Post_mock.query.filter().all.return_value = [post_stub]

    Post_mock.query.filter().filter().all.return_value = [post_stub]
    Post_mock.create_date = datetime.datetime.now()

    Post_mock.query.get.return_value = post_stub

    Union_mock = mocker.patch('konsent.Union')
    Union_mock.query.filter().count.return_value = 1
    union_stub = Union_mock.query.filter().first()

    Vote_mock = mocker.patch('konsent.Vote')
    Vote_query = Vote_mock.query.filter().first

    Comment_mock = mocker.patch('konsent.Comment')
    comment_stub = MagicMock()
    Comment_mock.return_value = comment_stub
    Comment_mock.query.get.return_value = comment_stub

    return locals()


@pytest.fixture
def forms_mock(mocker):
    UpvoteForm_mock = mocker.patch('konsent.UpvoteForm')
    UpvoteForm_mock().validate.return_value = True

    CommentForm_mock = mocker.patch('konsent.CommentForm')
    CommentForm_mock().validate.return_value = True

    RegisterForm_mock = mocker.patch('konsent.RegisterForm')
    RegisterForm_mock().validate.return_value = True

    RegisterUnionForm_mock = mocker.patch('konsent.RegisterUnionForm')
    RegisterUnionForm_mock().validate.return_value = True

    ArticleForm_mock = mocker.patch('konsent.ArticleForm')
    article_stub = MagicMock()
    ArticleForm_mock.return_value = article_stub
    ArticleForm_mock().validate.return_value = True

    VetoForm_mock = mocker.patch('konsent.VetoForm')
    VetoForm_mock().validate.return_value = True

    return locals()


@pytest.fixture()
def client_logged(user_mock, passwd_mock):
    app.config['TESTING'] = True
    app.secret_key = 'test_views'

    data = {'username': 'test_user',
            'password': 'test_password'}

    with app.test_client() as client:
        client.post('/login', data=data)
        yield client
