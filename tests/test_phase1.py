def test_phase1(client_logged, orm_mock, context):
    response = client_logged.get('/phase1', follow_redirects=True)

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'phase1.html'
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
