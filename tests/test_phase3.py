
def test_phase3(client_logged, orm_mock, context):

    response = client_logged.get('/phase3')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'phase3.html'
    assert context['posts'] == [orm_mock['post_stub']]


def test_post3(client_logged, orm_mock, context):

    response = client_logged.get('/phase3/post/1')

    assert response.status == '200 OK'
    [template, context], *_ = context
    assert template.name == 'post.html'
    assert context['post'] == orm_mock['post_stub']
