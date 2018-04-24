def test_index(client):
    response = client.get('/')
    assert b'Konsent' in response.data


def test_post_completed(client_logged, orm_mock, context):

    response = client_logged.get('/completed/post/1')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'post.html'
    assert context['post'] == orm_mock['post_stub']


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
