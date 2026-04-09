from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from controllers.auth_controller import login_required
from models.deck_model import get_decks_by_user, get_deck_by_id, create_deck, update_deck, delete_deck
from models.flashcard_model import get_cards_by_deck

deck_bp = Blueprint('deck', __name__)

#DECK_COLORS = ['#6366f1','#ec4899','#f59e0b','#10b981','#3b82f6','#8b5cf6','#ef4444','#14b8a6']
DECK_COLORS = '#3b82f6'

@deck_bp.route('/dashboard')
@login_required
def dashboard():
    decks = get_decks_by_user(session['user_id'])
    #return render_template('dashboard.html', decks=decks, colors=DECK_COLORS)
    return render_template('dashboard.html', decks=decks)

@deck_bp.route('/deck/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#6366f1')
        if not title:
            flash('Deck title is required.', 'error')
        else:
            deck_id = create_deck(session['user_id'], title, description, color)
            flash('Deck created successfully!', 'success')
            return redirect(url_for('deck.view_deck', deck_id=deck_id))
    return render_template('deck_form.html', deck=None, colors=DECK_COLORS, action='Create')

@deck_bp.route('/deck/<int:deck_id>')
@login_required
def view_deck(deck_id):
    deck = get_deck_by_id(deck_id, session['user_id'])
    if not deck:
         flash('Deck not found.', 'error')
         return redirect(url_for('deck.dashboard'))
    cards = get_cards_by_deck(deck_id)
    return render_template('deck_view.html', deck=deck, cards=cards)

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
        if not title:
            flash('Deck title is required.', 'error')
        else:
            update_deck(deck_id, session['user_id'], title, description, color)
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

@deck_bp.route('/deck/<int:deck_id>/study')
@login_required
def study(deck_id):
    deck = get_deck_by_id(deck_id, session['user_id'])
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
