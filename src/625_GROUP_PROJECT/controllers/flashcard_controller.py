from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from controllers.auth_controller import login_required
from models.deck_model import get_deck_by_id
from models.flashcard_model import get_card_by_id, create_card, update_card, delete_card

flashcard_bp = Blueprint('flashcard', __name__)

@flashcard_bp.route('/deck/<int:deck_id>/card/create', methods=['GET', 'POST'])
@login_required
def create(deck_id):
    deck = get_deck_by_id(deck_id, session['user_id'])
    if not deck:
        flash('Deck not found.', 'error')
        return redirect(url_for('deck.dashboard'))
    if request.method == 'POST':
        front = request.form.get('front', '').strip()
        back = request.form.get('back', '').strip()
        if not front or not back:
            flash('Both sides of the card are required.', 'error')
        else:
            create_card(deck_id, front, back)
            if request.form.get('add_another'):
                flash('Card added! Add another.', 'success')
                return redirect(url_for('flashcard.create', deck_id=deck_id))
            flash('Card created!', 'success')
            return redirect(url_for('deck.view_deck', deck_id=deck_id))
    return render_template('card_form.html', deck=deck, card=None, action='Create')

@flashcard_bp.route('/deck/<int:deck_id>/card/<int:card_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(deck_id, card_id):
    deck = get_deck_by_id(deck_id, session['user_id'])
    if not deck:
        flash('Deck not found.', 'error')
        return redirect(url_for('deck.dashboard'))
    card = get_card_by_id(card_id, deck_id)
    if not card:
        flash('Card not found.', 'error')
        return redirect(url_for('deck.view_deck', deck_id=deck_id))
    if request.method == 'POST':
        front = request.form.get('front', '').strip()
        back = request.form.get('back', '').strip()
        if not front or not back:
            flash('Both sides of the card are required.', 'error')
        else:
            update_card(card_id, deck_id, front, back)
            flash('Card updated!', 'success')
            return redirect(url_for('deck.view_deck', deck_id=deck_id))
    return render_template('card_form.html', deck=deck, card=card, action='Edit')

@flashcard_bp.route('/deck/<int:deck_id>/card/<int:card_id>/delete', methods=['POST'])
@login_required
def delete(deck_id, card_id):
    deck = get_deck_by_id(deck_id, session['user_id'])
    if deck:
        delete_card(card_id, deck_id)
        flash('Card deleted.', 'success')
    return redirect(url_for('deck.view_deck', deck_id=deck_id))
