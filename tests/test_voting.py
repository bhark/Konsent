
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
