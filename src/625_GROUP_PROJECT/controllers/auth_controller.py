from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import create_user, get_user_by_credentials

from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from models.user_model import create_user, get_user_by_credentials, get_user_by_email, update_user_password

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def _get_serializer():
    from flask import current_app
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def generate_reset_token(email):
    return _get_serializer().dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    try:
        email = _get_serializer().loads(token, salt='password-reset-salt', max_age=expiration)
    except (SignatureExpired, BadSignature):
        return None
    return email

# ── routes ───────────────────────────────────────────────────────────────────

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('deck.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('deck.dashboard'))
    if request.method == 'POST':
        firstname = request.form.get('firstname', '').strip()
        lastname = request.form.get('lastname', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not firstname or not lastname or not username or not email or not password:
            flash('All fields are required.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
        else:
            success, error = create_user(username, email, password, firstname, lastname)
            if success:
                flash('Account created! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(error, 'error')
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('deck.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = get_user_by_credentials(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('deck.dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        from flask import current_app
        from app import mail
        email = request.form.get('email', '').strip()
        user  = get_user_by_email(email)
        if user:
            token     = generate_reset_token(email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg      = Message('Password Reset Request', recipients=[email])
            msg.body = (
                f"Hi,\n\n"
                f"Click the link below to reset your password. It expires in 1 hour.\n\n"
                f"{reset_url}\n\n"
                f"If you didn't request this, you can ignore this email."
            )
            mail.send(msg)
        # Always show success to prevent email enumeration
        flash('If that email is registered, a reset link has been sent.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('That reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        if password != confirm:
            flash('Passwords do not match.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
        else:
            update_user_password(email, password)
            flash('Password updated! Please sign in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('reset_password.html', token=token)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
