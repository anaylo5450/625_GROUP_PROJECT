from models.user_model import create_user
from models.deck_model import create_deck, share_deck
from db import db, User


def _login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password},
                       follow_redirects=False)


def _make_users_and_deck(app):
    create_user('owner1', 'owner1@test.com', 'pass123', 'Owner', 'One')
    create_user('viewer1', 'viewer1@test.com', 'pass123', 'View', 'Er')
    owner = db.session.execute(db.select(User).where(User.username == 'owner1')).scalar_one()
    viewer = db.session.execute(db.select(User).where(User.username == 'viewer1')).scalar_one()
    deck_id = create_deck(owner.id, 'Test Deck', 'desc', '#6366f1')
    share_deck(deck_id, viewer.id)
    return deck_id, owner.id, viewer.id


def test_owner_can_view_stats(client, app):
    deck_id, owner_id, _ = _make_users_and_deck(app)
    _login(client, 'owner1', 'pass123')
    r = client.get(f'/deck/{deck_id}/stats')
    assert r.status_code == 200


def test_shared_viewer_can_view_stats(client, app):
    deck_id, _, _ = _make_users_and_deck(app)
    _login(client, 'viewer1', 'pass123')
    r = client.get(f'/deck/{deck_id}/stats')
    assert r.status_code == 200, f"shared viewer got {r.status_code}, expected 200"


def test_unshared_user_cannot_view_stats(client, app):
    deck_id, _, _ = _make_users_and_deck(app)
    create_user('stranger1', 'stranger1@test.com', 'pass123', 'Str', 'Anger')
    _login(client, 'stranger1', 'pass123')
    r = client.get(f'/deck/{deck_id}/stats', follow_redirects=False)
    assert r.status_code == 302, "non-shared user should be redirected"
