from flask import Blueprint

bp = Blueprint("flashcards", __name__, url_prefix="/flashcards")

from . import routes  # noqa: E402, F401
