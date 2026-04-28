def _reg(client, **overrides):
    data = dict(
        firstname='Jane', lastname='Doe', username='janedoe',
        email='jane@test.com', password='secret1', confirm_password='secret1',
    )
    data.update(overrides)
    return client.post('/register', data=data, follow_redirects=True)


def test_duplicate_email(client):
    _reg(client)  # first registration succeeds
    r = _reg(client, username='janedoe2')  # same email, different username
    assert r.status_code == 200
    assert b'Email already in use' in r.data


def test_duplicate_username(client):
    _reg(client)  # first registration succeeds
    r = _reg(client, email='other@test.com')  # same username, different email
    assert r.status_code == 200
    assert b'Username already taken' in r.data


def test_short_password(client):
    r = _reg(client, password='abc', confirm_password='abc')
    assert r.status_code == 200
    assert b'at least 6 characters' in r.data


def test_missing_field_firstname(client):
    r = _reg(client, firstname='')
    assert r.status_code == 200
    assert b'firstname' in r.data


def test_missing_field_email(client):
    r = _reg(client, email='')
    assert r.status_code == 200
    assert b'email' in r.data
