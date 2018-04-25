def test_phase2(client_logged, orm_mock, context):

    response = client_logged.get('/phase2')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'phase2.html'
    assert context['posts'] == [orm_mock['post_stub']]


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
