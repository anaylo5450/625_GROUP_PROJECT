from models.database import get_db

def create_session(user_id, deck_id, cards_total):
    conn = get_db()
    cursor = conn.execute(
        '''INSERT INTO study_sessions (user_id, deck_id, cards_total, cards_seen, cards_correct, cards_wrong, duration_seconds, completed)
           VALUES (?, ?, ?, 0, 0, 0, 0, 0)''',
        (user_id, deck_id, cards_total)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def finish_session(session_id, cards_seen, cards_correct, cards_wrong, duration_seconds, completed):
    conn = get_db()
    conn.execute(
        '''UPDATE study_sessions
           SET cards_seen=?, cards_correct=?, cards_wrong=?, duration_seconds=?, completed=?
           WHERE id=?''',
        (cards_seen, cards_correct, cards_wrong, duration_seconds, int(completed), session_id)
    )
    conn.commit()
    conn.close()

def get_deck_stats(deck_id, user_id):
    conn = get_db()

    sessions = conn.execute(
        '''SELECT * FROM study_sessions
           WHERE deck_id=? AND user_id=?
           ORDER BY started_at DESC''',
        (deck_id, user_id)
    ).fetchall()

    summary = conn.execute(
        '''SELECT
             COUNT(*) as total_sessions,
             SUM(completed) as completed_sessions,
             SUM(cards_seen) as total_cards_seen,
             SUM(cards_correct) as total_correct,
             SUM(cards_wrong) as total_wrong,
             SUM(duration_seconds) as total_time,
             AVG(duration_seconds) as avg_time,
             MAX(started_at) as last_studied
           FROM study_sessions
           WHERE deck_id=? AND user_id=?''',
        (deck_id, user_id)
    ).fetchone()

    conn.close()
    return [dict(s) for s in sessions], dict(summary)

def get_user_stats(user_id):
    conn = get_db()

    per_deck = conn.execute(
        '''SELECT d.title, d.color, d.id as deck_id,
             COUNT(s.id) as sessions,
             SUM(s.completed) as completed,
             SUM(s.cards_seen) as cards_seen,
             SUM(s.cards_correct) as correct,
             SUM(s.duration_seconds) as total_time
           FROM decks d
           LEFT JOIN study_sessions s ON s.deck_id = d.id AND s.user_id = d.user_id
           WHERE d.user_id = ?
           GROUP BY d.id
           ORDER BY cards_seen DESC''',
        (user_id,)
    ).fetchall()

    overall = conn.execute(
        '''SELECT
             COUNT(*) as total_sessions,
             SUM(completed) as completed_sessions,
             SUM(cards_seen) as cards_seen,
             SUM(cards_correct) as correct,
             SUM(cards_wrong) as wrong,
             SUM(duration_seconds) as total_time
           FROM study_sessions WHERE user_id=?''',
        (user_id,)
    ).fetchone()

    # Last 14 days activity
    daily = conn.execute(
        '''SELECT DATE(started_at) as day, COUNT(*) as sessions, SUM(cards_seen) as cards
           FROM study_sessions
           WHERE user_id=? AND started_at >= DATE('now', '-13 days')
           GROUP BY DATE(started_at)
           ORDER BY day ASC''',
        (user_id,)
    ).fetchall()

    conn.close()
    return [dict(d) for d in per_deck], dict(overall), [dict(d) for d in daily]
