import sqlite3
import os

# Always resolve DB path relative to this file, regardless of working directory
_HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_HERE, '..', 'flashcards.db')
DB_PATH = os.path.normpath(DB_PATH)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            visibility BOOLEAN DEFAULT 0,
            color TEXT DEFAULT '#6366f1',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
        );
    ''')
    conn.commit()
    conn.close()


def migrate_decks():
    """Add tags and visibility columns to decks if they don't exist yet."""
    conn = get_db()
    existing = [row[1] for row in conn.execute('PRAGMA table_info(decks)').fetchall()]
    if 'tags' not in existing:
        conn.execute('ALTER TABLE decks ADD COLUMN tags TEXT')
    if 'visibility' not in existing:
        conn.execute("ALTER TABLE decks ADD COLUMN visibility TEXT NOT NULL DEFAULT 'private'")
    conn.commit()
    conn.close()


def migrate_stats():
    """Add study_sessions table if it doesn't exist yet."""
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            deck_id INTEGER NOT NULL,
            cards_total INTEGER NOT NULL,
            cards_seen INTEGER NOT NULL,
            cards_correct INTEGER NOT NULL DEFAULT 0,
            cards_wrong INTEGER NOT NULL DEFAULT 0,
            duration_seconds INTEGER NOT NULL DEFAULT 0,
            completed INTEGER NOT NULL DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
        );
    ''')
    conn.commit()
    conn.close()
