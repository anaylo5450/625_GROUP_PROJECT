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
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str | None] = mapped_column(String, nullable=True)
    totp_secret: Mapped[str | None] = mapped_column(String, nullable=True)
    totp_enabled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


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
