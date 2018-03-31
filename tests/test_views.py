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
    app.secret_key = 'test_views'
    app.testing = True
    with app.test_client() as client:
        yield client


def _mock_user_query(mocker, return_value):
    User_mock = mocker.patch('konsent.User')
    filter_mock =  MagicMock()
    filter_mock.first.return_value = return_value
    User_mock.query.filter.return_value = filter_mock


def test_index(client):
    response = client.get('/')
    assert b'Konsent' in response.data


def test_login_non_existing_user(client, mocker):
    _mock_user_query(mocker, None)

    data = {'username': 'test_user',
            'password': 'test_password'}

    with captured_templates(app) as templates:

        response = client.post('/login', data=data)

        assert not session

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'login.html'
        assert context['error']


def test_login_existing_user(client, mocker):
    user_mock = MagicMock()
    user_mock.union.union_name = 'test_union'
    user_mock.union.id = '1'
    user_mock.id = '1'
    user_mock.check_password.return_value = True
    _mock_user_query(mocker, user_mock)

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
