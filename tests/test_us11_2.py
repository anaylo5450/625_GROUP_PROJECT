"""#48 — [US-11.2] Share deck with another user by username."""
from models.deck_model import get_shared_decks


def _register_login(client, username, email, password='pass123'):
    client.post('/register', data={
        'firstname': 'Test', 'lastname': 'User',
        'username': username, 'email': email,
        'password': password, 'confirm_password': password,
    })
    client.post('/login', data={'username': username, 'password': password})


def _create_deck(client, title='Shared Deck'):
    resp = client.post('/deck/create', data={
        'title': title, 'description': '', 'color': '#6366f1',
        'tags': '', 'visibility': '0',
    })
    return int(resp.headers['Location'].rstrip('/').split('/')[-1])


def _add_card(client, deck_id, front='Q', back='A'):
    client.post(f'/deck/{deck_id}/card/create', data={'front': front, 'back': back})


def test_share_with_valid_username_creates_share_record(client, app):
    _register_login(client, 'shareowner', 'shareowner@test.com')
    deck_id = _create_deck(client)

    # Create target user (register then switch back)
    with client.session_transaction() as sess:
        original = dict(sess)
    client.get('/logout')
    _register_login(client, 'sharetarget', 'sharetarget@test.com')
    from db import db, User
    with app.app_context():
        target = db.session.execute(
            db.select(User).where(User.username == 'sharetarget')
        ).scalar_one()
        target_id = target.id

    client.get('/logout')
    _register_login(client, 'shareowner', 'shareowner@test.com')

    client.post(f'/deck/{deck_id}/share', data={'username': 'sharetarget'})

    with app.app_context():
        shared = get_shared_decks(target_id)
        deck_ids = [d['id'] for d in shared]
        assert deck_id in deck_ids


def test_share_with_unknown_username_returns_error(client):
    _register_login(client, 'so2', 'so2@test.com')
    deck_id = _create_deck(client)

    resp = client.post(f'/deck/{deck_id}/share', data={'username': 'doesnotexist'},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert b'No user found' in resp.data


def test_share_with_self_returns_error(client):
    _register_login(client, 'so3', 'so3@test.com')
    deck_id = _create_deck(client)

    resp = client.post(f'/deck/{deck_id}/share', data={'username': 'so3'},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert b'cannot share a deck with yourself' in resp.data


def test_shared_user_can_access_study(client, app):
    # register both users before logging in as either
    client.post('/register', data={'firstname': 'A', 'lastname': 'B', 'username': 'so4',
                                   'email': 'so4@test.com', 'password': 'pass123',
                                   'confirm_password': 'pass123'})
    client.post('/register', data={'firstname': 'C', 'lastname': 'D', 'username': 'st4',
                                   'email': 'st4@test.com', 'password': 'pass123',
                                   'confirm_password': 'pass123'})
    client.post('/login', data={'username': 'so4', 'password': 'pass123'})
    deck_id = _create_deck(client)
    _add_card(client, deck_id)
    client.post(f'/deck/{deck_id}/share', data={'username': 'st4'})
    client.get('/logout')

    client.post('/login', data={'username': 'st4', 'password': 'pass123'})
    resp = client.get(f'/deck/{deck_id}/study')
    assert resp.status_code == 200


def test_non_shared_user_cannot_access_study(client):
    _register_login(client, 'so5', 'so5@test.com')
    deck_id = _create_deck(client)
    _add_card(client, deck_id)
    client.get('/logout')

    _register_login(client, 'stranger5', 'stranger5@test.com')
    resp = client.get(f'/deck/{deck_id}/study')
    # non-owner non-shared → redirected (deck not found for this user)
    assert resp.status_code == 302
