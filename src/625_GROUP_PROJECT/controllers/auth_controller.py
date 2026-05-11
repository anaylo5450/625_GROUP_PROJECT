from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import create_user, get_user_by_credentials

from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from models.user_model import (
    create_user, get_user_by_credentials, get_user_by_email,
    update_user_password, enable_totp, upsert_oauth_user,
)

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
        missing = next(
            (name for name, val in [
                ('firstname', firstname), ('lastname', lastname),
                ('username', username), ('email', email), ('password', password),
            ] if not val),
            None,
        )
        if missing:
            flash(f'{missing} is required', 'error')
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
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = get_user_by_credentials(username, password)
        if user:
            session.clear()
            if user['totp_enabled']:
                session['pending_user_id'] = user['id']
                return redirect(url_for('auth.verify_2fa'))
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('deck.dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')


@auth_bp.route('/login/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'pending_user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        import pyotp
        from db import db, User
        pending_id = session.pop('pending_user_id', None)
        user = db.session.get(User, pending_id)
        code = request.form.get('code', '').strip()
        if user and pyotp.TOTP(user.totp_secret).verify(code):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('deck.dashboard'))
        flash('Invalid code.', 'error')
        return render_template('verify_2fa.html')
    return render_template('verify_2fa.html')


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


@auth_bp.route('/settings/security', methods=['GET'])
@login_required
def security_settings():
    from db import db, User
    user = db.session.get(User, session['user_id'])
    return render_template('security_settings.html', totp_enabled=bool(user.totp_enabled))


@auth_bp.route('/settings/security/enable-2fa', methods=['POST'])
@login_required
def enable_2fa():
    import pyotp, qrcode, qrcode.image.svg, io
    secret = pyotp.random_base32()
    session['pending_totp_secret'] = secret
    uri = pyotp.TOTP(secret).provisioning_uri(
        name=session['username'], issuer_name='FlashCards'
    )
    factory = qrcode.image.svg.SvgImage
    buf = io.BytesIO()
    qrcode.make(uri, image_factory=factory).save(buf)
    qr_svg = buf.getvalue().decode('utf-8')
    return render_template('security_settings.html', qr_svg=qr_svg, totp_uri=uri, pending=True)


@auth_bp.route('/settings/security/confirm-2fa', methods=['POST'])
@login_required
def confirm_2fa():
    import pyotp
    secret = session.get('pending_totp_secret')
    code = request.form.get('code', '').strip()
    if not secret:
        flash('Session expired. Please try again.', 'error')
        return redirect(url_for('auth.security_settings'))
    if pyotp.TOTP(secret).verify(code):
        enable_totp(session['user_id'], secret)
        session.pop('pending_totp_secret', None)
        flash('Two-factor authentication enabled.', 'success')
        return redirect(url_for('auth.security_settings'))
    flash('Invalid code. Please try again.', 'error')
    return redirect(url_for('auth.security_settings'))


# ── OAuth helpers ─────────────────────────────────────────────────────────────

def _exchange_code_for_profile(code, redirect_uri, client_id, client_secret):
    """Exchange OAuth code for tokens, then fetch and return the userinfo dict."""
    import json, urllib.request, urllib.parse
    token_data = json.loads(urllib.request.urlopen(
        urllib.request.Request(
            'https://oauth2.googleapis.com/token',
            data=urllib.parse.urlencode({
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
            }).encode(),
            method='POST',
        )
    ).read())
    profile = json.loads(urllib.request.urlopen(
        urllib.request.Request(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {token_data["access_token"]}'},
        )
    ).read())
    return profile


# ── OAuth routes ──────────────────────────────────────────────────────────────

@auth_bp.route('/login/oauth/google')
def oauth_google():
    import secrets, urllib.parse
    from flask import current_app
    if not current_app.config.get('GOOGLE_CLIENT_ID') or not current_app.config.get('GOOGLE_CLIENT_SECRET'):
        return 'Google OAuth is not configured on this server.', 503
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    params = {
        'client_id': current_app.config['GOOGLE_CLIENT_ID'],
        'redirect_uri': url_for('auth.oauth_callback', _external=True),
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
    }
    return redirect('https://accounts.google.com/o/oauth2/auth?' + urllib.parse.urlencode(params))


@auth_bp.route('/login/oauth/callback')
def oauth_callback():
    from flask import current_app
    state = request.args.get('state', '')
    if state != session.pop('oauth_state', None):
        return 'State mismatch', 400
    code = request.args.get('code', '')
    profile = _exchange_code_for_profile(
        code=code,
        redirect_uri=url_for('auth.oauth_callback', _external=True),
        client_id=current_app.config['GOOGLE_CLIENT_ID'],
        client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
    )
    user = upsert_oauth_user(
        sub=profile['sub'],
        email=profile['email'],
        firstname=profile.get('given_name', ''),
        lastname=profile.get('family_name', ''),
        provider='google',
    )
    session['user_id'] = user['id']
    session['username'] = user['username']
    return redirect(url_for('deck.dashboard'))
