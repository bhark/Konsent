import datetime
from contextlib import contextmanager

from flask import request, template_rendered, session
from konsent import app
import konsent

import pytest
from unittest.mock import MagicMock


# http://flask.pocoo.org/docs/0.12/signals/#subscribing-to-signals
@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


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
    user_stab.check_password.return_value = True

    User_mock.query.filter().first.return_value = user_stab


@pytest.fixture
def post_mock(mocker):
    mocker.patch('konsent.db')
    mocker.patch('konsent.update_phases')

    Post_mock = mocker.patch('konsent.Post')

    post_stub = MagicMock()
    post_stub.time_since_create = {'hours': 0}

    Post_mock.query.filter().all.return_value = [post_stub]

    Post_mock.query.filter().filter().all.return_value = [post_stub]
    Post_mock.create_date = datetime.datetime.now()

    return post_stub


@pytest.fixture()
def client_logged(user_mock):
    app.config['TESTING'] = True
    app.secret_key = 'test_views'

    data = {'username': 'test_user',
            'password': 'test_password'}

    with app.test_client() as client:
        client.post('/login', data=data)
        yield client


def is_logged_in_stub(func):
    def wrap(*args, **kwargs):
        return func(*args, **kwargs)


def test_index(client):
    response = client.get('/')
    assert b'Konsent' in response.data


def test_login_non_existing_user(client, mocker):
    User_mock = mocker.patch('konsent.User')
    User_mock.query.filter().first.return_value = None

    data = {'username': 'test_user',
            'password': 'test_password'}

    with captured_templates(app) as templates:

        response = client.post('/login', data=data)

        assert not session

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'login.html'
        assert context['error']


def test_login_existing_user(client, user_mock):

    data = {'username': 'test_user',
            'password': 'test_password'}


    response = client.post('/login', data=data)

    assert  session['logged_in'] == True
    assert  session['username'] == 'test_user'
    assert  session['user_id'] == '1'
    assert  session['connected_union'] == '1'

    assert response.status == '302 FOUND'
    assert b"Redirecting" in response.data
    assert response.headers['Location'].endswith('/')


def test_phase1(client_logged, post_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/phase1')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'phase1.html'
        print('CONT:', context)
        assert context['posts'] == [post_mock]


def test_phase2(client_logged, post_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/phase2')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'phase2.html'
        print('CONT:', context)
        assert context['posts'] == [post_mock]
