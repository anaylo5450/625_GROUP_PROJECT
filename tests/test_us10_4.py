from unittest.mock import patch
from db import db, User

_FAKE_PROFILE = {
    'sub': 'google-sub-001',
    'email': 'oauthuser@example.com',
    'given_name': 'OAuth',
    'family_name': 'User',
}


def _do_oauth_callback(client, profile=_FAKE_PROFILE, state='teststate'):
    with client.session_transaction() as sess:
        sess['oauth_state'] = state
    with patch(
        'controllers.auth_controller._exchange_code_for_profile',
        return_value=profile,
    ):
        return client.get(f'/login/oauth/callback?state={state}&code=fakecode')


def test_first_oauth_login_creates_user(client, app):
    resp = _do_oauth_callback(client)
    assert resp.status_code == 302

    with app.app_context():
        users = db.session.execute(
            db.select(User).where(User.oauth_sub == 'google-sub-001')
        ).scalars().all()
        assert len(users) == 1
        assert users[0].email == 'oauthuser@example.com'
        assert users[0].oauth_provider == 'google'
        assert users[0].password is None


def test_second_oauth_login_retrieves_same_user(client, app):
    _do_oauth_callback(client)
    _do_oauth_callback(client)

    with app.app_context():
        count = db.session.execute(
            db.select(User).where(User.oauth_sub == 'google-sub-001')
        ).scalars().all()
        assert len(count) == 1, "second OAuth login must not create a duplicate row"


def test_oauth_login_creates_session(client):
    resp = _do_oauth_callback(client)
    assert resp.status_code == 302
    with client.session_transaction() as sess:
        assert 'user_id' in sess
        assert 'username' in sess


def test_oauth_login_redirects_to_dashboard(client):
    resp = _do_oauth_callback(client)
    assert resp.status_code == 302
    assert 'dashboard' in resp.headers['Location']


def test_second_oauth_login_also_creates_session(client, app):
    _do_oauth_callback(client)
    # clear session between calls to simulate a fresh browser visit
    with client.session_transaction() as sess:
        sess.clear()
    _do_oauth_callback(client)
    with client.session_transaction() as sess:
        assert 'user_id' in sess


def test_oauth_user_cannot_login_with_password(client, app):
    """OAuth-only users have no password; credential login must return None."""
    _do_oauth_callback(client)
    with app.app_context():
        from models.user_model import get_user_by_credentials
        result = get_user_by_credentials('oauthuser@example.com', 'anypassword')
        assert result is None
