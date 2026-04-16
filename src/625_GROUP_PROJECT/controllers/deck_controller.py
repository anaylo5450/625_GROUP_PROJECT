from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from controllers.auth_controller import login_required
from models.deck_model import (get_decks_by_user, get_deck_by_id, get_deck_by_id_for_user,
                               get_public_deck, create_deck, update_deck, delete_deck,
                               share_deck, unshare_deck, get_shares_for_deck, get_shared_decks)
from models.flashcard_model import get_cards_by_deck
from models.user_model import get_user_by_username

deck_bp = Blueprint('deck', __name__)

DECK_COLORS = ['#6366f1','#ec4899','#f59e0b','#10b981','#3b82f6','#8b5cf6','#ef4444','#14b8a6']

@deck_bp.route('/dashboard')
@login_required
def dashboard():
    decks = get_decks_by_user(session['user_id'])
    shared = get_shared_decks(session['user_id'])
    return render_template('dashboard.html', decks=decks, shared=shared)

@deck_bp.route('/deck/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#6366f1')
        tags = request.form.get('tags', '').strip() or None
        visibility = request.form.get('visibility', '0')
        if not title:
            flash('Deck title is required.', 'error')
        else:
            deck_id = create_deck(session['user_id'], title, description, color, tags, visibility)
            flash('Deck created successfully!', 'success')
            return redirect(url_for('deck.view_deck', deck_id=deck_id))
    return render_template('deck_form.html', deck=None, colors=DECK_COLORS, action='Create')

@deck_bp.route('/deck/<int:deck_id>')
@login_required
def view_deck(deck_id):
    deck = get_deck_by_id_for_user(deck_id, session['user_id'])
    if not deck:
        flash('Deck not found.', 'error')
        return redirect(url_for('deck.dashboard'))
    cards = get_cards_by_deck(deck_id)
    is_owner = (deck['user_id'] == session['user_id'])
    shares = get_shares_for_deck(deck_id) if is_owner else []
    public_url = url_for('deck.public_view', deck_id=deck_id, _external=True) \
        if str(deck['visibility']) == '1' else None
    return render_template('deck_view.html', deck=deck, cards=cards,
                           is_owner=is_owner, shares=shares, public_url=public_url)


@deck_bp.route('/deck/<int:deck_id>/share', methods=['POST'])
@login_required
def share(deck_id):
    deck = get_deck_by_id(deck_id, session['user_id'])
    if not deck:
        flash('Deck not found.', 'error')
        return redirect(url_for('deck.dashboard'))
    username = request.form.get('username', '').strip()
    if not username:
        if str(deck['visibility']) == '1':
            public_url = url_for('deck.public_view', deck_id=deck_id, _external=True)
            flash(f'Public link: {public_url}', 'success')
        else:
            flash('Enter a username to share with a specific user, or set the deck to Public for a shareable link.', 'error')
        return redirect(url_for('deck.view_deck', deck_id=deck_id))
    if username == session.get('username'):
        flash('You cannot share a deck with yourself.', 'error')
        return redirect(url_for('deck.view_deck', deck_id=deck_id))
    target = get_user_by_username(username)
    if not target:
        flash(f'No user found with username "{username}".', 'error')
        return redirect(url_for('deck.view_deck', deck_id=deck_id))
    ok, err = share_deck(deck_id, target['id'])
    if ok:
        flash(f'Deck shared with {username}.', 'success')
    else:
        flash(err, 'error')
    return redirect(url_for('deck.view_deck', deck_id=deck_id))


@deck_bp.route('/deck/<int:deck_id>/unshare/<int:user_id>', methods=['POST'])
@login_required
def unshare(deck_id, user_id):
    deck = get_deck_by_id(deck_id, session['user_id'])
    if not deck:
        flash('Deck not found.', 'error')
        return redirect(url_for('deck.dashboard'))
    unshare_deck(deck_id, user_id)
    flash('Share removed.', 'success')
    return redirect(url_for('deck.view_deck', deck_id=deck_id))

@deck_bp.route('/deck/<int:deck_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(deck_id):
    deck = get_deck_by_id(deck_id, session['user_id'])
    if not deck:
        flash('Deck not found.', 'error')
        return redirect(url_for('deck.dashboard'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', deck['color'])
        tags = request.form.get('tags', '').strip() or None
        visibility = request.form.get('visibility', 'private')
        if not title:
            flash('Deck title is required.', 'error')
        else:
            update_deck(deck_id, session['user_id'], title, description, color, tags, visibility)
            flash('Deck updated!', 'success')
            return redirect(url_for('deck.view_deck', deck_id=deck_id))
    return render_template('deck_form.html', deck=deck, colors=DECK_COLORS, action='Edit')

@deck_bp.route('/deck/<int:deck_id>/delete', methods=['POST'])
@login_required
def delete(deck_id):
    deck = get_deck_by_id(deck_id, session['user_id'])
    if deck:
        delete_deck(deck_id, session['user_id'])
        flash('Deck deleted.', 'success')
    return redirect(url_for('deck.dashboard'))

@deck_bp.route('/deck/<int:deck_id>/public')
def public_view(deck_id):
    deck = get_public_deck(deck_id)
    if not deck:
        flash('This deck is not publicly available.', 'error')
        return redirect(url_for('auth.login'))
    cards = get_cards_by_deck(deck_id)
    return render_template('deck_view_public.html', deck=deck, cards=cards)


@deck_bp.route('/deck/<int:deck_id>/study')
@login_required
def study(deck_id):
    deck = get_deck_by_id_for_user(deck_id, session['user_id'])
    if not deck:
        flash('Deck not found.', 'error')
        return redirect(url_for('deck.dashboard'))
    cards = get_cards_by_deck(deck_id)
    if not cards:
        flash('Add some cards before studying!', 'error')
        return redirect(url_for('deck.view_deck', deck_id=deck_id))
    # Convert sqlite3.Row objects to plain dicts so tojson works in template
    cards_list = [dict(c) for c in cards]
    return render_template('study.html', deck=dict(deck), cards=cards_list)
