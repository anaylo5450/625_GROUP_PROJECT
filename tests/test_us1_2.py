from werkzeug.security import check_password_hash
from models.user_model import create_user, get_user_by_credentials
from db import db, User


def test_password_is_hashed(app):
    create_user('htest', 'htest@test.com', 'plaintext', 'Hash', 'Test')
    with app.app_context():
        user = db.session.execute(db.select(User).where(User.username == 'htest')).scalar_one()
        assert user.password != 'plaintext', "password stored as plaintext"
        assert check_password_hash(user.password, 'plaintext'), "stored hash does not verify"


def test_correct_password_authenticates(app):
    create_user('authok', 'authok@test.com', 'goodpass', 'Auth', 'Ok')
    result = get_user_by_credentials('authok', 'goodpass')
    assert result is not None, "correct password should return a user"
    assert result['username'] == 'authok'


def test_wrong_password_rejected(app):
    create_user('authfail', 'authfail@test.com', 'realpass', 'Auth', 'Fail')
    result = get_user_by_credentials('authfail', 'wrongpass')
    assert result is None, "wrong password should return None"
