"""#3 — [US-1.1] Registration form creates an account."""


def test_register_page_loads(client):
    resp = client.get('/register')
    assert resp.status_code == 200


def test_valid_registration_redirects_to_login(client):
    resp = client.post('/register', data={
        'firstname': 'Ada', 'lastname': 'Lovelace',
        'username': 'ada', 'email': 'ada@test.com',
        'password': 'secure1', 'confirm_password': 'secure1',
    })
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_missing_field_returns_error(client):
    resp = client.post('/register', data={
        'firstname': '', 'lastname': 'Lovelace',
        'username': 'ada2', 'email': 'ada2@test.com',
        'password': 'secure1', 'confirm_password': 'secure1',
    })
    assert resp.status_code == 200
    # code flashes "{field} is required"
    assert b'is required' in resp.data


def test_mismatched_passwords_returns_error(client):
    resp = client.post('/register', data={
        'firstname': 'Ada', 'lastname': 'Lovelace',
        'username': 'ada3', 'email': 'ada3@test.com',
        'password': 'secure1', 'confirm_password': 'different',
    })
    assert resp.status_code == 200
    assert b'Passwords do not match' in resp.data


def test_short_password_returns_error(client):
    resp = client.post('/register', data={
        'firstname': 'Ada', 'lastname': 'Lovelace',
        'username': 'ada4', 'email': 'ada4@test.com',
        'password': 'abc', 'confirm_password': 'abc',
    })
    assert resp.status_code == 200
    assert b'at least 6 characters' in resp.data
