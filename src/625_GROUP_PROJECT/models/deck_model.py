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

def create_deck(user_id, title, description, color):
    conn = get_db()
    cursor = conn.execute(
        'INSERT INTO decks (user_id, title, description, color) VALUES (?, ?, ?, ?)',
        (user_id, title, description, color)
    )
    deck_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return deck_id

def update_deck(deck_id, user_id, title, description, color):
    conn = get_db()
    conn.execute(
        'UPDATE decks SET title=?, description=?, color=?, updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?',
        (title, description, color, deck_id, user_id)
    )
    conn.commit()
    conn.close()

def delete_deck(deck_id, user_id):
    conn = get_db()
    conn.execute('DELETE FROM decks WHERE id = ? AND user_id = ?', (deck_id, user_id))
    conn.commit()
    conn.close()
