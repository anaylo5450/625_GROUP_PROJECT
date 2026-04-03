"""
Authors:    Chidi A Azubike, Richard C Baldwin, Frits Buningh, Andrew P Naylor
Emails:     caazubike0@frostburg.edu, rcbaldwin0@frostburg.edu,
            fbuningh0@frostburg.edu, apnaylor0@frostburg.edu
Date:       2026
Description:
    Flashcards Blueprint package initializer. Creates the blueprint and
    imports routes so they are registered with the application.
"""
# Imports
from flask import Blueprint

# Globals
# blueprint registered at /flashcards by the application factory
bp = Blueprint("flashcards", __name__, url_prefix="/flashcards")

# import routes after bp is defined to avoid circular imports
from . import routes  # noqa: E402, F401
