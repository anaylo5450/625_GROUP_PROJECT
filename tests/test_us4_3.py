"""#16 — [US-4.3] Update deck tags."""
from db import db


def _register_login(client, username='owner', email='owner@test.com'):
    client.post('/register', data={
        'firstname': 'Test', 'lastname': 'User',
        'username': username, 'email': email,
        'password': 'pass123', 'confirm_password': 'pass123',
    })
    client.post('/login', data={'username': username, 'password': 'pass123'})


def _create_deck(client, title='My Deck', tags='', visibility='0'):
    resp = client.post('/deck/create', data={
        'title': title, 'description': '', 'color': '#6366f1',
        'tags': tags, 'visibility': visibility,
    })
    return int(resp.headers['Location'].rstrip('/').split('/')[-1])


def test_update_tags_saves_new_value(client, app):
    _register_login(client)
    deck_id = _create_deck(client)

    client.post(f'/deck/{deck_id}/edit', data={
        'title': 'My Deck', 'description': '', 'color': '#6366f1',
        'tags': 'python,flask', 'visibility': '0',
    })

    # verify via the edit form (route uses raw SQL — unaffected by ORM cache)
    resp = client.get(f'/deck/{deck_id}/edit')
    assert b'python,flask' in resp.data


def test_update_tags_to_empty_saves_null(client, app):
    _register_login(client, 'owner2', 'owner2@test.com')
    deck_id = _create_deck(client, tags='old-tag')

    client.post(f'/deck/{deck_id}/edit', data={
        'title': 'My Deck', 'description': '', 'color': '#6366f1',
        'tags': '', 'visibility': '0',
    })

    # verify: old tag gone, deck still loads without error
    resp = client.get(f'/deck/{deck_id}/edit')
    assert b'old-tag' not in resp.data


def test_deck_still_retrievable_after_empty_tags(client):
    _register_login(client, 'owner3', 'owner3@test.com')
    deck_id = _create_deck(client, tags='old-tag')

    client.post(f'/deck/{deck_id}/edit', data={
        'title': 'My Deck', 'description': '', 'color': '#6366f1',
        'tags': '', 'visibility': '0',
    })

    resp = client.get(f'/deck/{deck_id}')
    assert resp.status_code == 200


def test_unauthenticated_edit_redirects_to_login(client):
    resp = client.post('/deck/1/edit', data={
        'title': 'Hacked', 'description': '', 'color': '#6366f1',
        'tags': 'x', 'visibility': '0',
    })
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']
