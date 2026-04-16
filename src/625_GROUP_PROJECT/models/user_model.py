from models.database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(username, email, password, firstname, lastname):
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, email, password, firstname, lastname) VALUES (?, ?, ?, ?, ?)',
            (username, email, generate_password_hash(password), firstname, lastname)
        )
        conn.commit()
        return True, None
    except Exception as e:
        if 'UNIQUE' in str(e):
            if 'username' in str(e):
                return False, 'Username already taken'
            return False, 'Email already registered'
        return False, str(e)
    finally:
        conn.close()

def get_user_by_credentials(username, password):
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        return user
    return None

def get_user_by_username(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user
