import pyotp
from models.user_model import create_user, enable_totp
from db import db, User


def _register_and_login(client, username, email, password='testpass'):
    client.post('/register', data={
        'firstname': 'Test', 'lastname': 'User',
        'username': username, 'email': email,
        'password': password, 'confirm_password': password,
    })
    client.post('/login', data={'username': username, 'password': password})


def test_secret_is_valid_base32(app):
    secret = pyotp.random_base32()
    # base32 alphabet: A-Z and 2-7
    import base64
    try:
        base64.b32decode(secret)
    except Exception:
        assert False, "generated secret is not valid base32"


def test_totp_correct_code_accepted(app):
    secret = pyotp.random_base32()
    code = pyotp.TOTP(secret).now()
    assert pyotp.TOTP(secret).verify(code), "current TOTP code should verify"


def test_totp_wrong_code_rejected(app):
    secret = pyotp.random_base32()
    assert not pyotp.TOTP(secret).verify('000000'), "wrong code should not verify"


def test_enable_totp_persists_to_db(app):
    with app.app_context():
        create_user('totpuser', 'totp@test.com', 'pass123', 'Totp', 'User')
        user = db.session.execute(
            db.select(User).where(User.username == 'totpuser')
        ).scalar_one()
        secret = pyotp.random_base32()
        enable_totp(user.id, secret)

        db.session.expire_all()
        user = db.session.get(User, user.id)
        assert user.totp_enabled == 1, "totp_enabled should be 1 after enable_totp"
        assert user.totp_secret == secret, "totp_secret should match saved secret"


def test_security_settings_requires_login(client):
    resp = client.get('/settings/security')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_security_settings_accessible_when_logged_in(client):
    _register_and_login(client, 'secuser', 'sec@test.com')
    resp = client.get('/settings/security')
    assert resp.status_code == 200
    assert b'Two-Factor Authentication' in resp.data


def test_enable_2fa_returns_qr_page(client):
    _register_and_login(client, 'qruser', 'qr@test.com')
    resp = client.post('/settings/security/enable-2fa')
    assert resp.status_code == 200
    assert b'Scan this QR code' in resp.data


def test_confirm_2fa_with_correct_code(app, client):
    _register_and_login(client, 'confirmuser', 'confirm@test.com')
    # trigger enable-2fa to plant the secret in the session
    client.post('/settings/security/enable-2fa')
    # retrieve the secret from the DB-level session
    with app.app_context():
        with client.session_transaction() as sess:
            secret = sess.get('pending_totp_secret')
    assert secret, "pending_totp_secret should be in session after enable-2fa"
    code = pyotp.TOTP(secret).now()
    resp = client.post('/settings/security/confirm-2fa', data={'code': code})
    assert resp.status_code == 302

    with app.app_context():
        user = db.session.execute(
            db.select(User).where(User.username == 'confirmuser')
        ).scalar_one()
        assert user.totp_enabled == 1
        assert user.totp_secret == secret


def test_confirm_2fa_with_wrong_code(client):
    _register_and_login(client, 'badcodeuser', 'badcode@test.com')
    client.post('/settings/security/enable-2fa')
    resp = client.post('/settings/security/confirm-2fa', data={'code': '000000'})
    # should redirect back with error (not 200, stays on security page)
    assert resp.status_code == 302
