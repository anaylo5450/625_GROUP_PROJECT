"""
Authors:    Chidi A Azubike, Richard C Baldwin, Frits Buningh, Andrew P Naylor
Emails:     caazubike0@frostburg.edu, rcbaldwin0@frostburg.edu,
            fbuningh0@frostburg.edu, apnaylor0@frostburg.edu
Date:       2026
Description:
    Flask application factory. Initializes configuration, logging,
    the database, and registers all blueprints.
"""
# Imports
import os
import logging
from flask import Flask, render_template
from dotenv import load_dotenv

# load .env file into os.environ before anything reads the config
load_dotenv()

# Globals
_FALLBACK_SECRET = "dev-change-me"


# Functions
def create_app(test_config=None):
    """
    Input:  test_config (dict | None) - optional config overrides for testing
    Output: Flask application instance
    Details:
        Application factory. Creates and fully configures the Flask app,
        initialises the database, and registers the flashcards blueprint.
        Raises RuntimeError if the fallback secret key is used outside debug mode.
    """
    app = Flask(__name__, instance_relative_config=True)

    # base configuration applied to every environment
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", _FALLBACK_SECRET),
        SQLALCHEMY_DATABASE_URI=(
            "sqlite:///" + os.path.join(app.instance_path, "flashcards.db")
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=not app.debug,
    )

    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    # allow tests to override any config value
    if test_config is not None:
        app.config.from_mapping(test_config)

    # refuse to run in production without a real secret key
    if app.config["SECRET_KEY"] == _FALLBACK_SECRET and not app.debug:
        raise RuntimeError(
            "SECRET_KEY is not set. "
            "Copy .env.example to .env and set a strong SECRET_KEY before running in production."
        )

    # ensure the instance folder exists for the DB and log file
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # write logs to both the instance folder and stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(
                os.path.join(app.instance_path, "flask_app.log"), "a", "utf-8"
            ),
            logging.StreamHandler(),
        ],
    )

    # initialise database and register CLI commands
    from . import db
    db.init_app(app)

    # register the flashcards blueprint at /flashcards
    from .flashcards import bp as flashcards_bp
    app.register_blueprint(flashcards_bp)

    @app.route("/")
    @app.route("/index")
    @app.route("/index.html")
    def index():
        """
        Input:  None
        Output: Rendered index.html template
        Details:
            Root route. Serves the application home page.
        """
        return render_template("index.html")

    return app