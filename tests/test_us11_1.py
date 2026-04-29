"""#42 — [US-11.1] Shareable link for a public deck."""


def _register_login(client, username='pub_owner', email='pub@test.com'):
    client.post('/register', data={
        'firstname': 'Test', 'lastname': 'User',
        'username': username, 'email': email,
        'password': 'pass123', 'confirm_password': 'pass123',
    })
    client.post('/login', data={'username': username, 'password': 'pass123'})


def _create_deck(client, title='Public Deck', visibility='1'):
    resp = client.post('/deck/create', data={
        'title': title, 'description': '', 'color': '#6366f1',
        'tags': '', 'visibility': visibility,
    })
    return int(resp.headers['Location'].rstrip('/').split('/')[-1])


def test_public_deck_accessible_without_login(client):
    _register_login(client)
    deck_id = _create_deck(client, visibility='1')
    client.get('/logout')

    resp = client.get(f'/deck/{deck_id}/public')
    assert resp.status_code == 200


def test_private_deck_public_url_redirects(client):
    _register_login(client, 'priv_owner', 'priv@test.com')
    deck_id = _create_deck(client, title='Private Deck', visibility='0')
    client.get('/logout')

    resp = client.get(f'/deck/{deck_id}/public')
    assert resp.status_code == 302


def test_owner_deck_view_contains_public_url(client):
    _register_login(client, 'link_owner', 'link@test.com')
    deck_id = _create_deck(client, title='Link Deck', visibility='1')

    resp = client.get(f'/deck/{deck_id}')
    assert resp.status_code == 200
    assert f'/deck/{deck_id}/public'.encode() in resp.data
