import os
from db import db

_HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_HERE, '..', 'flashcards.db')
DB_PATH = os.path.normpath(DB_PATH)


def _row_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    conn = db.engine.raw_connection()
    conn.row_factory = _row_factory
    return conn


def init_db():
    pass


def migrate_decks():
    pass


def migrate_shares():
    pass


def migrate_stats():
    pass
