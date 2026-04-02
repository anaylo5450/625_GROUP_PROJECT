import os
import logging
from flask import Flask
from dotenv import load_dotenv

load_dotenv()  # loads .env into os.environ before the factory reads it

_FALLBACK_SECRET = "dev-change-me"


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", _FALLBACK_SECRET),
        DATABASE=os.path.join(app.instance_path, "flashcards.db"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=not app.debug,
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    if app.config["SECRET_KEY"] == _FALLBACK_SECRET and not app.debug:
        raise RuntimeError(
            "SECRET_KEY is not set. "
            "Copy .env.example to .env and set a strong SECRET_KEY before running in production."
        )

    os.makedirs(app.instance_path, exist_ok=True)

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

    from . import db
    db.init_app(app)

    from .flashcards import bp as flashcards_bp
    app.register_blueprint(flashcards_bp)

    from flask import render_template

    @app.route("/")
    @app.route("/index")
    @app.route("/index.html")
    def index():
        return render_template("index.html")

    return app
