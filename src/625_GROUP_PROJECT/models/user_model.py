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
            if 'username' in str(e):
                return False, 'Username already taken'
            return False, 'Email already registered'
        return False, str(e)


def get_user_by_credentials(username, password):
    user = db.session.execute(
        db.select(User).where(User.username == username)
    ).scalar_one_or_none()
    if user and check_password_hash(user.password, password):
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
