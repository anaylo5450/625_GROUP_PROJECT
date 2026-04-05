"""
Run this script once to manually create the SQLite database and tables.
Usage: python create_db.py
"""
from models.database import init_db, DB_PATH

print(f"Creating database at: {DB_PATH}")
init_db()
print("✓ Tables created: users, decks, flashcards")
