from flask import Flask
from flask_mail import Mail
from models.database import init_db, migrate_decks, migrate_stats, migrate_shares
from controllers.auth_controller import auth_bp
from controllers.deck_controller import deck_bp
from controllers.flashcard_controller import flashcard_bp
from controllers.stats_controller import stats_bp



# 1. Create app FIRST
app = Flask(__name__, template_folder='views/templates')
app.secret_key = 'flashcard_secret_key_2024'

# 2. Then configure it
app.config['MAIL_SERVER']         = 'smtp.gmail.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = 'cazubike@gmail.com'   # ← replace
app.config['MAIL_PASSWORD']       = 'zhav mjml sdfx xzyw'      # ← replace with Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'cazubike@gmail.com'   # ← replace


# 3. Then initialize extensions

mail = Mail(app)

# 4. Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(deck_bp)
app.register_blueprint(flashcard_bp)
app.register_blueprint(stats_bp)

# Always initialize DB on startup
init_db()
migrate_decks()
migrate_stats()
migrate_shares()

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5001)
