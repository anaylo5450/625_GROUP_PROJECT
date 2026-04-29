"""#49 — [US-11.3] Restrict edit and delete to deck owner."""


def _register(client, username, email, password='pass123'):
    client.post('/register', data={
        'firstname': 'Test', 'lastname': 'User',
        'username': username, 'email': email,
        'password': password, 'confirm_password': password,
    })


def _login(client, username, password='pass123'):
    client.post('/login', data={'username': username, 'password': password})


def _create_deck(client, title='Owner Deck'):
    resp = client.post('/deck/create', data={
        'title': title, 'description': '', 'color': '#6366f1',
        'tags': '', 'visibility': '0',
    })
    return int(resp.headers['Location'].rstrip('/').split('/')[-1])


def test_non_owner_get_edit_is_redirected(client):
    _register(client, 'o1', 'o1@test.com')
    _register(client, 'n1', 'n1@test.com')
    _login(client, 'o1')
    deck_id = _create_deck(client)
    client.get('/logout')

    _login(client, 'n1')
    resp = client.get(f'/deck/{deck_id}/edit')
    assert resp.status_code == 302


def test_non_owner_post_edit_is_redirected_and_deck_unchanged(client):
    _register(client, 'o2', 'o2@test.com')
    _register(client, 'n2', 'n2@test.com')
    _login(client, 'o2')
    deck_id = _create_deck(client, title='Original Title')
    client.get('/logout')

    _login(client, 'n2')
    resp = client.post(f'/deck/{deck_id}/edit', data={
        'title': 'Hacked Title', 'description': '', 'color': '#6366f1',
        'tags': '', 'visibility': '0',
    })
    assert resp.status_code == 302
    client.get('/logout')

    _login(client, 'o2')
    resp = client.get(f'/deck/{deck_id}')
    assert b'Original Title' in resp.data


def test_non_owner_post_delete_is_redirected_and_deck_survives(client):
    _register(client, 'o3', 'o3@test.com')
    _register(client, 'n3', 'n3@test.com')
    _login(client, 'o3')
    deck_id = _create_deck(client, title='Survivor Deck')
    client.get('/logout')

    _login(client, 'n3')
    resp = client.post(f'/deck/{deck_id}/delete')
    assert resp.status_code == 302
    client.get('/logout')

    _login(client, 'o3')
    resp = client.get(f'/deck/{deck_id}')
    assert resp.status_code == 200


def test_owner_can_edit_deck(client):
    _register(client, 'o4', 'o4@test.com')
    _login(client, 'o4')
    deck_id = _create_deck(client, title='Before Edit')

    client.post(f'/deck/{deck_id}/edit', data={
        'title': 'After Edit', 'description': '', 'color': '#6366f1',
        'tags': '', 'visibility': '0',
    })

    resp = client.get(f'/deck/{deck_id}')
    assert b'After Edit' in resp.data


def test_owner_can_delete_deck(client):
    _register(client, 'o5', 'o5@test.com')
    _login(client, 'o5')
    deck_id = _create_deck(client, title='Delete Me')

    client.post(f'/deck/{deck_id}/delete')

    # after deletion the deck view should redirect (deck not found)
    resp = client.get(f'/deck/{deck_id}')
    assert resp.status_code == 302
