from models.database import get_db

def get_cards_by_deck(deck_id):
    conn = get_db()
    cards = conn.execute(
        '''
        SELECT id, deck_id, front, back, front_image_filename, back_image_filename,
               created_at, updated_at
        FROM flashcards
        WHERE deck_id = ?
        ORDER BY created_at ASC
        ''',
        (deck_id,)
    ).fetchall()
    conn.close()
    return cards


def get_card_by_id(card_id, deck_id):
    conn = get_db()
    card = conn.execute(
        '''
        SELECT id, deck_id, front, back, front_image_filename, back_image_filename,
               created_at, updated_at
        FROM flashcards
        WHERE id = ? AND deck_id = ?
        ''',
        (card_id, deck_id)
    ).fetchone()
    conn.close()
    return card


def create_card(deck_id, front, back, front_image_filename=None, back_image_filename=None):
    conn = get_db()
    cursor = conn.execute(
        '''
        INSERT INTO flashcards (
            deck_id,
            front,
            back,
            front_image_filename,
            back_image_filename
        )
        VALUES (?, ?, ?, ?, ?)
        ''',
        (deck_id, front, back, front_image_filename, back_image_filename)
    )
    card_id = cursor.lastrowid

    conn.execute(
        'UPDATE decks SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (deck_id,)
    )

    conn.commit()
    conn.close()
    return card_id


def update_card(card_id, deck_id, front, back, front_image_filename=None, back_image_filename=None):
    conn = get_db()
    conn.execute(
        '''
        UPDATE flashcards
        SET front = ?,
            back = ?,
            front_image_filename = ?,
            back_image_filename = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND deck_id = ?
        ''',
        (front, back, front_image_filename, back_image_filename, card_id, deck_id)
    )

    conn.execute(
        'UPDATE decks SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (deck_id,)
    )

    conn.commit()
    conn.close()


def delete_card(card_id, deck_id):
    conn = get_db()
    conn.execute(
        'DELETE FROM flashcards WHERE id = ? AND deck_id = ?',
        (card_id, deck_id)
    )
    conn.execute(
        'UPDATE decks SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (deck_id,)
    )
    conn.commit()
    conn.close()