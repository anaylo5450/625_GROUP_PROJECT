from flask import Flask
from models.database import init_db, migrate_decks, migrate_stats
from controllers.auth_controller import auth_bp
from controllers.deck_controller import deck_bp
from controllers.flashcard_controller import flashcard_bp
from controllers.stats_controller import stats_bp

app = Flask(__name__, template_folder='views/templates')
app.secret_key = 'flashcard_secret_key_2024'

app.register_blueprint(auth_bp)
app.register_blueprint(deck_bp)
app.register_blueprint(flashcard_bp)
app.register_blueprint(stats_bp)

# Always initialize DB on startup
init_db()
migrate_decks()
migrate_stats()

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host="0.0.0.0", port=5000)
