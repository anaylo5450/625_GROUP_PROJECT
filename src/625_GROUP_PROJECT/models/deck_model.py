from models.database import get_db

def get_decks_by_user(user_id):
    conn = get_db()
    decks = conn.execute('''
        SELECT d.*, COUNT(f.id) as card_count
        FROM decks d
        LEFT JOIN flashcards f ON f.deck_id = d.id
        WHERE d.user_id = ?
        GROUP BY d.id
        ORDER BY d.updated_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return decks

def get_deck_by_id(deck_id, user_id):
    conn = get_db()
    deck = conn.execute(
        'SELECT * FROM decks WHERE id = ? AND user_id = ?', (deck_id, user_id)
    ).fetchone()
    conn.close()
    return deck

def create_deck(user_id, title, description, color, tags=None, visibility='private'):
    conn = get_db()
    cursor = conn.execute(
        'INSERT INTO decks (user_id, title, description, color, tags, visibility) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, title, description, color, tags, visibility)
    )
    deck_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return deck_id

def update_deck(deck_id, user_id, title, description, color, tags=None, visibility='private'):
    conn = get_db()
    conn.execute(
        'UPDATE decks SET title=?, description=?, color=?, tags=?, visibility=?, updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?',
        (title, description, color, tags, visibility, deck_id, user_id)
    )
    conn.commit()
    conn.close()

def delete_deck(deck_id, user_id):
    conn = get_db()
    conn.execute('DELETE FROM decks WHERE id = ? AND user_id = ?', (deck_id, user_id))
    conn.commit()
    conn.close()

def get_public_deck(deck_id):
    """Return a deck only if it is publicly visible."""
    conn = get_db()
    deck = conn.execute(
        "SELECT * FROM decks WHERE id = ? AND visibility IN ('1', 1)", (deck_id,)
    ).fetchone()
    conn.close()
    return deck

def get_deck_by_id_for_user(deck_id, user_id):
    """Return a deck if the user owns it or it has been shared with them."""
    conn = get_db()
    deck = conn.execute(
        '''SELECT d.* FROM decks d
           WHERE d.id = ? AND (
               d.user_id = ?
               OR EXISTS (
                   SELECT 1 FROM deck_shares s
                   WHERE s.deck_id = d.id AND s.shared_with_user_id = ?
               )
           )''',
        (deck_id, user_id, user_id)
    ).fetchone()
    conn.close()
    return deck

def share_deck(deck_id, shared_with_user_id):
    """Insert a share record; silently ignores duplicate."""
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO deck_shares (deck_id, shared_with_user_id) VALUES (?, ?)',
            (deck_id, shared_with_user_id)
        )
        conn.commit()
        return True, None
    except Exception as e:
        if 'UNIQUE' in str(e):
            return False, 'Deck already shared with that user'
        return False, str(e)
    finally:
        conn.close()

def unshare_deck(deck_id, shared_with_user_id):
    conn = get_db()
    conn.execute(
        'DELETE FROM deck_shares WHERE deck_id = ? AND shared_with_user_id = ?',
        (deck_id, shared_with_user_id)
    )
    conn.commit()
    conn.close()

def get_shares_for_deck(deck_id):
    """Return list of users this deck is shared with."""
    conn = get_db()
    rows = conn.execute(
        '''SELECT u.id, u.username FROM users u
           JOIN deck_shares s ON s.shared_with_user_id = u.id
           WHERE s.deck_id = ?
           ORDER BY s.created_at ASC''',
        (deck_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_shared_decks(user_id):
    """Return decks shared with this user (that they do not own)."""
    conn = get_db()
    decks = conn.execute(
        '''SELECT d.*, COUNT(f.id) as card_count FROM decks d
           JOIN deck_shares s ON s.deck_id = d.id
           LEFT JOIN flashcards f ON f.deck_id = d.id
           WHERE s.shared_with_user_id = ?
           GROUP BY d.id
           ORDER BY d.updated_at DESC''',
        (user_id,)
    ).fetchall()
    conn.close()
    return decks
