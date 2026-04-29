import pyotp
from models.user_model import create_user, enable_totp
from db import db, User


def _create_user(app, username, email, password='testpass'):
    with app.app_context():
        create_user(username, email, password, 'Test', 'User')
        user = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar_one()
        return user.id


def _create_2fa_user(app, username, email, password='testpass'):
    uid = _create_user(app, username, email, password)
    secret = pyotp.random_base32()
    with app.app_context():
        enable_totp(uid, secret)
    return uid, secret


def test_non_2fa_login_goes_to_dashboard(client, app):
    _create_user(app, 'plain', 'plain@test.com')
    resp = client.post('/login', data={'username': 'plain', 'password': 'testpass'})
    assert resp.status_code == 302
    assert 'dashboard' in resp.headers['Location']


def test_2fa_user_correct_password_redirects_to_challenge(client, app):
    _create_2fa_user(app, 'mfa1', 'mfa1@test.com')
    resp = client.post('/login', data={'username': 'mfa1', 'password': 'testpass'})
    assert resp.status_code == 302
    assert 'verify-2fa' in resp.headers['Location']


def test_2fa_challenge_page_renders(client, app):
    _create_2fa_user(app, 'mfa2', 'mfa2@test.com')
    client.post('/login', data={'username': 'mfa2', 'password': 'testpass'})
    resp = client.get('/login/verify-2fa')
    assert resp.status_code == 200
    assert b'Authentication code' in resp.data


def test_verify_2fa_correct_code_completes_login(client, app):
    uid, secret = _create_2fa_user(app, 'mfa3', 'mfa3@test.com')
    client.post('/login', data={'username': 'mfa3', 'password': 'testpass'})
    code = pyotp.TOTP(secret).now()
    resp = client.post('/login/verify-2fa', data={'code': code})
    assert resp.status_code == 302
    assert 'dashboard' in resp.headers['Location']
    # confirm full session is created
    with client.session_transaction() as sess:
        assert 'user_id' in sess
        assert sess['user_id'] == uid


def test_verify_2fa_wrong_code_is_rejected(client, app):
    _create_2fa_user(app, 'mfa4', 'mfa4@test.com')
    client.post('/login', data={'username': 'mfa4', 'password': 'testpass'})
    resp = client.post('/login/verify-2fa', data={'code': '000000'})
    assert resp.status_code == 200
    assert b'Invalid code' in resp.data
    with client.session_transaction() as sess:
        assert 'user_id' not in sess


def test_verify_2fa_without_pending_redirects_to_login(client):
    resp = client.get('/login/verify-2fa')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_2fa_wrong_password_does_not_reach_challenge(client, app):
    _create_2fa_user(app, 'mfa5', 'mfa5@test.com')
    resp = client.post('/login', data={'username': 'mfa5', 'password': 'wrongpass'})
    assert resp.status_code == 200
    assert b'Invalid username or password' in resp.data
