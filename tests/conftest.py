import sys
import os
import tempfile
import types
import pytest

# Make src importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', '625_GROUP_PROJECT'))

# Stub flask_mail before any app import so the module loads without the package
if 'flask_mail' not in sys.modules:
    _fm = types.ModuleType('flask_mail')
    class _Mail:
        def __init__(self, app=None): pass
    class _Message:
        def __init__(self, *a, **kw): self.body = ''
    _fm.Mail = _Mail
    _fm.Message = _Message
    sys.modules['flask_mail'] = _fm


@pytest.fixture
def app():
    """Fresh Flask app backed by a temporary file-based SQLite database.

    A file DB is used instead of :memory: because the codebase mixes
    SQLAlchemy ORM sessions (db.session) with raw DBAPI connections
    (models/database.py get_db → engine.raw_connection). On :memory: both
    share the same single StaticPool connection, and raw-connection commits
    corrupt SQLAlchemy's transaction-state tracking, making ORM queries
    invisible to subsequent requests. A file DB gives each checkout an
    independent handle so the two paths never interfere.
    """
    from flask import Flask
    from db import db
    from controllers.auth_controller import auth_bp
    from controllers.deck_controller import deck_bp
    from controllers.flashcard_controller import flashcard_bp
    from controllers.stats_controller import stats_bp

    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    test_app = Flask(__name__, template_folder=os.path.join(
        os.path.dirname(__file__), '..', 'src', '625_GROUP_PROJECT', 'views', 'templates'
    ))
    test_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret',
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'MAIL_SERVER': 'localhost',
        'MAIL_DEFAULT_SENDER': 'test@test.com',
        'GOOGLE_CLIENT_ID': 'test-google-client-id',
        'GOOGLE_CLIENT_SECRET': 'test-google-client-secret',
    })

    db.init_app(test_app)
    test_app.register_blueprint(auth_bp)
    test_app.register_blueprint(deck_bp)
    test_app.register_blueprint(flashcard_bp)
    test_app.register_blueprint(stats_bp)

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()

    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()
