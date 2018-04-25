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

    assert template.name == 'index.html'
