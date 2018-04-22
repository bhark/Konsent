import datetime
from contextlib import contextmanager

from flask import request,  session, current_app
from konsent import login_manager, make_app
import konsent

import pytest


def is_logged_in_stub(func):
    def wrap(*args, **kwargs):
        return func(*args, **kwargs)


def test_index(client):
    response = client.get('/')
    assert b'Konsent' in response.data


def test_phase1(client_logged, orm_mock, context):
    response = client_logged.get('/phase1', follow_redirects=True)

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'phase1.html'
    assert context['posts'] == [orm_mock['post_stub']]


def test_phase2(client_logged, orm_mock, context):

    response = client_logged.get('/phase2')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'phase2.html'
    assert context['posts'] == [orm_mock['post_stub']]


def test_phase3(client_logged, orm_mock, context):

    response = client_logged.get('/phase3')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'phase3.html'
    assert context['posts'] == [orm_mock['post_stub']]


def test_post1_get(client_logged, context):

    response = client_logged.get('/phase1/post/1')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'post.html'
    assert context['post_data']['voted'] is True
    # MagicMock __len__ returns 0
    assert context['post_data']['votes'] == 0


def test_post1_post_vote_up(client_logged, orm_mock, context):
    # user_mock['User_mock'].query.filter().count.return_value = 1
    orm_mock['Vote_query'].return_value = None
    orm_mock['post_stub'].votes_count = 0

    response = client_logged.post('/phase1/post/1', follow_redirects=True)

    assert response.status == '200 OK'

    [template, context], *_ = context
    assert template.name == 'phase1.html'

    assert orm_mock['post_stub'].votes_count == 1


def test_post1_post_vote_down(client_logged, orm_mock, context):
    orm_mock['post_stub'].votes_count = 1

    response = client_logged.post('/phase1/post/1',
                                  data={'minutes': 0, 'hours': 0},
                                  follow_redirects=True)

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'phase1.html'
    assert orm_mock['post_stub'].votes_count == 0


def test_post2_get(client_logged, orm_mock, context):

    response = client_logged.get('/phase2/post/1')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'post.html'
    assert context['post'] == orm_mock['post_stub']


def test_post2_post(client_logged, orm_mock, context):

    response = client_logged.post('/phase2/post/1')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'post.html'
    assert context['post'] == orm_mock['post_stub']
    orm_mock['db'].session.add.assert_called_with(orm_mock['comment_stub'])


def test_post3(client_logged, orm_mock, context):

    response = client_logged.get('/phase3/post/1')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'post.html'
    assert context['post'] == orm_mock['post_stub']


def test_post_completed(client_logged, orm_mock, context):

    response = client_logged.get('/completed/post/1')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'post.html'
    assert context['post'] == orm_mock['post_stub']


def test_register_get(client, context):

    response = client.get('/register')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'register.html'


def test_register_post(client, user_mock, context):
    user_mock['query'].return_value = None

    response = client.post('/register',
                           data={'username': 'test_username',
                                 'password': 'test_passw0rD',
                                 'confirm': 'test_passw0rD'},
                           follow_redirects=True)

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'login.html'


def test_register_union_get(client, context):

    response = client.get('/register-union')

    assert response.status == '200 OK'
    [template, context], *_ = context

    assert template.name == 'register-union.html'


def test_register_union_post(client, context):

    response = client.post('/register-union',
                           data={'union_name': 'test_union_username',
                                 'password': 'test_passw0rD',
                                 'confirm': 'test_passw0rD'})

    assert response.status == '200 OK'
    [template, context], *_ = context

    # XXX: This should not redirect to index
    assert template.name == 'index.html'


def test_vote_comment(client_logged, orm_mock, context):
    orm_mock['Vote_query'].return_value = None
    orm_mock['comment_stub'].votes_count = 0


    response = client_logged.get('/post/vote/1/1', follow_redirects=True)

    assert response.status == '200 OK'
    [template, context], *_ = context

    assert template.name == 'post.html'

    assert orm_mock['comment_stub'].votes_count == 1


def test_unvote_comment(client_logged, orm_mock, context):
    orm_mock['Vote_query'].return_value = 'A Vote'
    orm_mock['comment_stub'].votes_count = 1


    response = client_logged.get('/post/unvote/1/1', follow_redirects=True)

    assert response.status == '200 OK'
    [template, context], *_ = context

    assert template.name == 'post.html'

    assert orm_mock['comment_stub'].votes_count == 0


def test_new_post_post(client_logged, forms_mock, context):
    forms_mock['article_stub'].title.data = 'test post title'
    forms_mock['article_stub'].body.data = 'test post data'

    response = client_logged.post('/new-post', data={'unit': 'minutes'}, follow_redirects=True)

    assert response.status == '200 OK'
    [template, context], *_ = context

    assert template.name == 'new-post.html'


def test_vetoed(client_logged, orm_mock, context):

    response = client_logged.get('/vetoed')

    assert response.status == '200 OK'
    [template, context], *_ = context

    assert template.name == 'vetoed.html'


def test_vetoed_post(client_logged, orm_mock, context):
    orm_mock['post_stub'].phase = 3
    orm_mock['post_stub'].vetoed_by_id

    response = client_logged.post('/veto/1', follow_redirects=True)

    assert response.status == '200 OK'
    [template, context], *_ = context

    assert template.name == 'vetoed.html'


def test_members(client_logged, context):

    response = client_logged.get('/members')

    assert response.status == '200 OK'
    [template, context], *_ = context

    assert template.name == 'union-members.html'
