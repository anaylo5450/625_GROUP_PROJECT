import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail
from db import db, init_app as db_init_app
from controllers.auth_controller import auth_bp
from controllers.deck_controller import deck_bp
from controllers.flashcard_controller import flashcard_bp
from controllers.stats_controller import stats_bp

load_dotenv()

app = Flask(__name__, template_folder='views/templates')
app.secret_key = 'flashcard_secret_key_2024'

_HERE = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.normpath(os.path.join(_HERE, 'flashcards.db'))}"
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID', '')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', '')

app.config['MAIL_SERVER']         = 'smtp.gmail.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = 'cazubike@gmail.com'
app.config['MAIL_PASSWORD']       = 'zhav mjml sdfx xzyw'
app.config['MAIL_DEFAULT_SENDER'] = 'cazubike@gmail.com'

db_init_app(app)
mail = Mail(app)

app.register_blueprint(auth_bp)
app.register_blueprint(deck_bp)
app.register_blueprint(flashcard_bp)
app.register_blueprint(stats_bp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
