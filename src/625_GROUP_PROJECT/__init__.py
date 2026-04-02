import os
import logging
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-change-me"),
        DATABASE=os.path.join(app.instance_path, "flashcards.db"),
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

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
