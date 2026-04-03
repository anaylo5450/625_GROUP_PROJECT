"""
Authors:    Chidi A Azubike, Richard C Baldwin, Frits Buningh, Andrew P Naylor
Emails:     caazubike0@frostburg.edu, rcbaldwin0@frostburg.edu,
            fbuningh0@frostburg.edu, apnaylor0@frostburg.edu
Date:       2026
Description:
    Application entry point. Creates and runs the Flask app via the
    application factory.
"""
# Imports
from . import create_app

# Globals
app = create_app()


# Functions
def main():
    """
    Input:  None
    Output: None
    Details:
        Starts the Flask development server. Use `flask run` in production
        instead of calling this directly.
    """
    app.run()


if __name__ == "__main__":
    main()
