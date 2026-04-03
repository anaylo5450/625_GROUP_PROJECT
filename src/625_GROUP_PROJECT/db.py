import click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firstname: Mapped[str] = mapped_column(String, nullable=False)
    lastname: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    school: Mapped[str | None] = mapped_column(String, nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)


class Deck(db.Model):
    __tablename__ = "decks"

    deck_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)


class FlashcardQuestion(db.Model):
    __tablename__ = "flashcard_questions"

    question_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    quiz_name: Mapped[str] = mapped_column(String, nullable=False)
    question: Mapped[str] = mapped_column(String, nullable=False)
    choice1: Mapped[str] = mapped_column(String, nullable=False)
    choice2: Mapped[str] = mapped_column(String, nullable=False)
    choice3: Mapped[str] = mapped_column(String, nullable=False)
    choice4: Mapped[str] = mapped_column(String, nullable=False)
    correct_choice: Mapped[int] = mapped_column(Integer, nullable=False)


@click.command("init-db")
def init_db_command():
    """Create database tables."""
    db.create_all()
    click.echo("Database initialised.")


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
    with app.app_context():
        db.create_all()
