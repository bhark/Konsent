import datetime
from contextlib import contextmanager

from flask import request,  session, template_rendered
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


def test_login_existing_user(client, user_mock, passwd_mock):

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


def test_logout(client_logged):
    with captured_templates(app) as templates:

        response = client_logged.get('/logout')

        assert not session.get('logged_in')


def test_phase1(client_logged, orm_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/phase1')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'phase1.html'
        assert context['posts'] == [orm_mock['post_stub']]


def test_phase2(client_logged, orm_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/phase2')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'phase2.html'
        assert context['posts'] == [orm_mock['post_stub']]


def test_phase3(client_logged, orm_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/phase3')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'phase3.html'
        assert context['posts'] == [orm_mock['post_stub']]


def test_post1_get(client_logged, orm_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/phase1/post/1')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'post.html'
        assert context['post_data']['voted'] == True
        # MagicMock __len__ returns 0
        assert context['post_data']['votes'] == 0


def test_post1_post_vote_up(client_logged, user_mock, orm_mock, forms_mock):
    user_mock['User_mock'].query.filter().count.return_value = 1
    orm_mock['Vote_query'].return_value = None
    orm_mock['post_stub'].votes_count = 0

    with captured_templates(app) as templates:

        response = client_logged.post('/phase1/post/1',
                                      data={'minutes': 0, 'hours': 0}, follow_redirects=True)

        assert response.status == '200 OK'

        [template, context], *_ = templates
        assert template.name == 'phase1.html'

        assert orm_mock['post_stub'].votes_count == 1


def test_post1_post_vote_down(client_logged, orm_mock, forms_mock):
    orm_mock['post_stub'].votes_count = 1

    with captured_templates(app) as templates:

        response = client_logged.post('/phase1/post/1',
                                      data={'minutes': 0, 'hours': 0},
                                      follow_redirects=True)

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'phase1.html'
        assert orm_mock['post_stub'].votes_count == 0


def test_post2_get(client_logged, orm_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/phase2/post/1')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'post.html'
        assert context['post'] == orm_mock['post_stub']


def test_post2_post(client_logged, orm_mock, forms_mock):
    with captured_templates(app) as templates:

        response = client_logged.post('/phase2/post/1')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'post.html'
        assert context['post'] == orm_mock['post_stub']
        orm_mock['db'].session.add.assert_called_with(orm_mock['comment_stub'])


def test_post3(client_logged, orm_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/phase3/post/1')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'post.html'
        assert context['post'] == orm_mock['post_stub']


def test_post_completed(client_logged, orm_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/completed/post/1')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'post.html'
        assert context['post'] == orm_mock['post_stub']


def test_register_get(client, orm_mock):
    with captured_templates(app) as templates:

        response = client.get('/register')

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'register.html'


def test_register_post(client, user_mock, passwd_mock, orm_mock, forms_mock):
    user_mock['query'].return_value = None

    with captured_templates(app) as templates:

        # why this works? :O
        response = client.post('/register',
                              data={'username': 'test_username',
                                    'password': 'test_passw0rD'})

        assert response.status == '200 OK'
        [template, context], *_ = templates
        assert template.name == 'login.html'


def test_register_union_get(client, orm_mock):

    with captured_templates(app) as templates:

        response = client.get('/register-union')

        assert response.status == '200 OK'
        [template, context], *_ = templates

        assert template.name == 'register-union.html'


def test_register_union_post(client, passwd_mock, orm_mock, forms_mock):
    with captured_templates(app) as templates:

        response = client.post('/register-union',
                              data={'union_name': 'test_union_username',
                                    'password': 'test_passw0rD',
                                    'confirm': 'test_passw0rD'})

        assert response.status == '200 OK'
        [template, context], *_ = templates

        # XXX: This should not redirect to index
        assert template.name == 'index.html'


def test_vote_comment(client_logged, orm_mock):
    orm_mock['Vote_query'].return_value = None
    orm_mock['comment_stub'].votes_count = 0

    with captured_templates(app) as templates:

        response = client_logged.get('/post/vote/1/1', follow_redirects=True)

        assert response.status == '200 OK'
        [template, context], *_ = templates

        assert template.name == 'post.html'

    assert orm_mock['comment_stub'].votes_count == 1


def test_unvote_comment(client_logged, orm_mock):
    orm_mock['Vote_query'].return_value = 'A Vote'
    orm_mock['comment_stub'].votes_count = 1

    with captured_templates(app) as templates:

        response = client_logged.get('/post/unvote/1/1', follow_redirects=True)

        assert response.status == '200 OK'
        [template, context], *_ = templates

        assert template.name == 'post.html'

    assert orm_mock['comment_stub'].votes_count == 0


def test_new_post_post(client_logged, orm_mock, forms_mock):
    forms_mock['article_stub'].title.data = 'test post title'
    forms_mock['article_stub'].body.data = 'test post data'

    with captured_templates(app) as templates:

        response = client_logged.post('/new_post', follow_redirects=True)

        assert response.status == '200 OK'
        [template, context], *_ = templates

        assert template.name == 'phase1.html'

        orm_mock['Post_mock'].assert_called_with('test post title', 'test post data', '1', '1')


def test_vetoed(client_logged, orm_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/vetoed')

        assert response.status == '200 OK'
        [template, context], *_ = templates

        assert template.name == 'vetoed.html'


def test_vetoed_post(client_logged, orm_mock, forms_mock):
    orm_mock['post_stub'].phase = 3
    orm_mock['post_stub'].vetoed_by_id

    with captured_templates(app) as templates:

        response = client_logged.post('/veto/1', follow_redirects=True)

        assert response.status == '200 OK'
        [template, context], *_ = templates

        assert template.name == 'vetoed.html'


def test_members(client_logged, orm_mock):
    with captured_templates(app) as templates:

        response = client_logged.get('/members')

        assert response.status == '200 OK'
        [template, context], *_ = templates

        assert template.name == 'union-members.html'

