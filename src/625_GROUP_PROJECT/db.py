"""
Authors:    Chidi A Azubike, Richard C Baldwin, Frits Buningh, Andrew P Naylor
Emails:     caazubike0@frostburg.edu, rcbaldwin0@frostburg.edu,
            fbuningh0@frostburg.edu, apnaylor0@frostburg.edu
Date:       2026
Description:
    SQLAlchemy database instance and ORM model definitions mirroring the
    existing flashcards.db schema exactly so no migration is required.
"""
import click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    firstname: Mapped[str] = mapped_column(String, nullable=False)
    lastname: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[str | None] = mapped_column(String, nullable=True)
    totp_secret: Mapped[str | None] = mapped_column(String, nullable=True)
    totp_enabled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    oauth_provider: Mapped[str | None] = mapped_column(String, nullable=True)
    oauth_sub: Mapped[str | None] = mapped_column(String, nullable=True)


class Deck(db.Model):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[str | None] = mapped_column(String, nullable=True)
    visibility: Mapped[str] = mapped_column(String, nullable=False, default="0")
    color: Mapped[str | None] = mapped_column(String, nullable=True, default="#6366f1")
    created_at: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[str | None] = mapped_column(String, nullable=True)


class Flashcard(db.Model):
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deck_id: Mapped[int] = mapped_column(Integer, ForeignKey("decks.id"), nullable=False)
    front: Mapped[str] = mapped_column(String, nullable=False)
    back: Mapped[str] = mapped_column(String, nullable=False)
    front_image_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    back_image_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[str | None] = mapped_column(String, nullable=True)


class StudySession(db.Model):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    deck_id: Mapped[int] = mapped_column(Integer, ForeignKey("decks.id"), nullable=False)
    cards_total: Mapped[int] = mapped_column(Integer, nullable=False)
    cards_seen: Mapped[int] = mapped_column(Integer, nullable=False)
    cards_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cards_wrong: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[str | None] = mapped_column(String, nullable=True)


class DeckShare(db.Model):
    __tablename__ = "deck_shares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deck_id: Mapped[int] = mapped_column(Integer, ForeignKey("decks.id"), nullable=False)
    shared_with_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (UniqueConstraint("deck_id", "shared_with_user_id"),)


class FlashcardQuestion(db.Model):
    """Separate table for the history-quiz question-creation workflow."""
    __tablename__ = "flashcard_questions"

    question_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_name: Mapped[str] = mapped_column(String, nullable=False)
    question: Mapped[str] = mapped_column(String, nullable=False)
    front_image_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    back_image_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    choice1: Mapped[str] = mapped_column(String, nullable=False)
    choice2: Mapped[str] = mapped_column(String, nullable=False)
    choice3: Mapped[str] = mapped_column(String, nullable=False)
    choice4: Mapped[str] = mapped_column(String, nullable=False)
    correct_choice: Mapped[int] = mapped_column(Integer, nullable=False)


@click.command("init-db")
def init_db_command():
    db.create_all()
    click.echo("Database initialised.")


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
    with app.app_context():
        db.create_all()
        _migrate_totp_columns()
        _migrate_oauth_columns()


def _migrate_totp_columns():
    """Add totp_secret and totp_enabled to users if the columns are missing."""
    conn = db.engine.raw_connection()
    try:
        cur = conn.cursor()
        existing = {row[1] for row in cur.execute("PRAGMA table_info(users)")}
        if "totp_secret" not in existing:
            cur.execute("ALTER TABLE users ADD COLUMN totp_secret TEXT")
        if "totp_enabled" not in existing:
            cur.execute("ALTER TABLE users ADD COLUMN totp_enabled INTEGER NOT NULL DEFAULT 0")
        conn.commit()
    finally:
        conn.close()


def _migrate_oauth_columns():
    """Make password nullable and add oauth_provider/oauth_sub.

    SQLite cannot drop NOT NULL via ALTER TABLE, so when password is still
    NOT NULL we recreate the table with the full target schema.
    """
    conn = db.engine.raw_connection()
    try:
        cur = conn.cursor()
        pragma = cur.execute("PRAGMA table_info(users)").fetchall()
        existing = {row[1] for row in pragma}
        password_notnull = next((r[3] for r in pragma if r[1] == "password"), 0)

        needs_provider = "oauth_provider" not in existing
        needs_sub = "oauth_sub" not in existing
        needs_nullable_pw = password_notnull == 1

        if not (needs_provider or needs_sub or needs_nullable_pw):
            return

        if needs_nullable_pw:
            # Recreate the table so password loses its NOT NULL constraint.
            # Include all columns that exist in the backup so no data is lost.
            cur.execute("ALTER TABLE users RENAME TO _users_backup")
            cur.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR NOT NULL UNIQUE,
                    firstname VARCHAR NOT NULL,
                    lastname VARCHAR NOT NULL,
                    email VARCHAR NOT NULL UNIQUE,
                    password VARCHAR,
                    created_at VARCHAR,
                    totp_secret VARCHAR,
                    totp_enabled INTEGER NOT NULL DEFAULT 0,
                    oauth_provider VARCHAR,
                    oauth_sub VARCHAR
                )
            """)
            backup_cols = [r[1] for r in pragma]
            new_cols = [
                "id", "username", "firstname", "lastname", "email",
                "password", "created_at", "totp_secret", "totp_enabled",
                "oauth_provider", "oauth_sub",
            ]
            copy_cols = ", ".join(c for c in new_cols if c in backup_cols)
            cur.execute(f"INSERT INTO users ({copy_cols}) SELECT {copy_cols} FROM _users_backup")
            cur.execute("DROP TABLE _users_backup")
        else:
            if needs_provider:
                cur.execute("ALTER TABLE users ADD COLUMN oauth_provider TEXT")
            if needs_sub:
                cur.execute("ALTER TABLE users ADD COLUMN oauth_sub TEXT")

        conn.commit()
    finally:
        conn.close()
