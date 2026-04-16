"""
Authors:    Chidi A Azubike, Richard C Baldwin, Frits Buningh, Andrew P Naylor
Emails:     caazubike0@frostburg.edu, rcbaldwin0@frostburg.edu,
            fbuningh0@frostburg.edu, apnaylor0@frostburg.edu
Date:       2026
Description:
    SQLAlchemy database instance and ORM model definitions for users,
    decks, and flashcard questions.
"""
# Imports
import click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey

# Globals
db = SQLAlchemy()


# Models
class User(db.Model):
    """
    Input:  Column values supplied at insert time
    Output: User ORM instance
    Details:
        Represents a registered user. Username must be unique.
        Password is stored as a bcrypt hash, never plaintext.
    """
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firstname: Mapped[str] = mapped_column(String, nullable=False)
    lastname: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    school: Mapped[str | None] = mapped_column(String, nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)


class Deck(db.Model):
    """
    Input:  Column values supplied at insert time
    Output: Deck ORM instance
    Details:
        Represents a flashcard deck owned by a user.
        Foreign key links each deck to its creator.
    """
    __tablename__ = "decks"

    deck_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)                              #US-3.1 - Andrew
    description: Mapped[str | None] = mapped_column(String, nullable=True)                  #US-3.2 - Andrew
    tags: Mapped[str | None] = mapped_column(String, nullable=True)                         #US-3.3 - Andrew
    visibility: Mapped[str] = mapped_column(String, nullable=False, default="private")      #US-3.4 - Andrew


class FlashcardQuestion(db.Model):
    """
    Input:  Column values supplied at insert time
    Output: FlashcardQuestion ORM instance
    Details:
        Represents a multiple-choice flashcard question with four choices.
        correct_choice is stored as a 1-based index (1-4).
    """
    __tablename__ = "flashcard_questions"

    question_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    quiz_name: Mapped[str] = mapped_column(String, nullable=False)
    question: Mapped[str] = mapped_column(String, nullable=False)

    image_filename: Mapped[str | None] = mapped_column(String, nullable=True)

    choice1: Mapped[str] = mapped_column(String, nullable=False)
    choice2: Mapped[str] = mapped_column(String, nullable=False)
    choice3: Mapped[str] = mapped_column(String, nullable=False)
    choice4: Mapped[str] = mapped_column(String, nullable=False)
    correct_choice: Mapped[int] = mapped_column(Integer, nullable=False)


# Functions
@click.command("init-db")
def init_db_command():
    """
    Input:  None (invoked via `flask init-db` CLI)
    Output: None
    Details:
        Creates all database tables defined by the ORM models.
        Safe to run multiple times; existing tables are not dropped.
    """
    db.create_all()
    click.echo("Database initialised.")


def init_app(app):
    """
    Input:  app (Flask) - the application instance
    Output: None
    Details:
        Binds the SQLAlchemy instance to the app, registers the init-db
        CLI command, and creates all tables on startup.
    """
    db.init_app(app)
    app.cli.add_command(init_db_command)
    # create tables immediately so the app is ready without manual migration
    with app.app_context():
        db.create_all()
