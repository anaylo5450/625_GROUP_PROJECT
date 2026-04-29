from db import db, User
from werkzeug.security import generate_password_hash, check_password_hash


def _user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'email': user.email,
        'password': user.password,
        'created_at': user.created_at,
        'totp_enabled': user.totp_enabled,
        'totp_secret': user.totp_secret,
        'oauth_provider': user.oauth_provider,
        'oauth_sub': user.oauth_sub,
    }


def create_user(username, email, password, firstname, lastname):
    try:
        db.session.add(User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            firstname=firstname,
            lastname=lastname,
        ))
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        if 'UNIQUE' in str(e):
            if 'users.username' in str(e):
                return False, 'Username already taken'
            if 'users.email' in str(e):
                return False, 'Email already in use'
        return False, str(e)


def get_user_by_credentials(username, password):
    user = db.session.execute(
        db.select(User).where(User.username == username)
    ).scalar_one_or_none()
    if user and user.password and check_password_hash(user.password, password):
        return _user_to_dict(user)
    return None


def get_user_by_username(username):
    user = db.session.execute(
        db.select(User).where(User.username == username)
    ).scalar_one_or_none()
    return _user_to_dict(user) if user else None


def get_user_by_id(user_id):
    user = db.session.get(User, user_id)
    return _user_to_dict(user) if user else None


def get_user_by_email(email):
    user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()
    return _user_to_dict(user) if user else None


def update_user_password(email, new_password):
    user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()


def enable_totp(user_id, secret):
    user = db.session.get(User, user_id)
    if user:
        user.totp_secret = secret
        user.totp_enabled = 1
        db.session.commit()


def upsert_oauth_user(sub, email, firstname, lastname, provider='google'):
    """Return the User dict for the given OAuth sub, creating it if needed."""
    user = db.session.execute(
        db.select(User).where(User.oauth_sub == sub)
    ).scalar_one_or_none()
    if user:
        user.email = email
        user.firstname = firstname
        user.lastname = lastname
        db.session.commit()
    else:
        user = User(
            username=email,
            email=email,
            firstname=firstname,
            lastname=lastname,
            password=None,
            oauth_provider=provider,
            oauth_sub=sub,
        )
        db.session.add(user)
        db.session.commit()
    return _user_to_dict(user)
