import sqlite3
import os
import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname     TEXT NOT NULL,
            lastname      TEXT NOT NULL,
            username      TEXT NOT NULL UNIQUE,
            school        TEXT,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS flashcard_questions (
            question_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            quiz_name      TEXT NOT NULL,
            question       TEXT NOT NULL,
            choice1        TEXT NOT NULL,
            choice2        TEXT NOT NULL,
            choice3        TEXT NOT NULL,
            choice4        TEXT NOT NULL,
            correct_choice INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """
    )
    db.commit()


@click.command("init-db")
def init_db_command():
    """Create database tables."""
    init_db()
    click.echo("Database initialised.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
