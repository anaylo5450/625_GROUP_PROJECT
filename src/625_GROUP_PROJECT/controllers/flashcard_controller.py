import os

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename

from controllers.auth_controller import login_required
from models.deck_model import get_deck_by_id
from models.flashcard_model import get_card_by_id, create_card, update_card, delete_card

flashcard_bp = Blueprint('flashcard', __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def save_uploaded_image(file_storage, deck_id, side_prefix):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_image(file_storage.filename):
        return None

    safe_name = secure_filename(file_storage.filename)
    final_name = f"deck{deck_id}_{side_prefix}_{safe_name}"

    upload_folder = current_app.config.get(
        "UPLOAD_FOLDER",
        os.path.join(current_app.root_path, "static", "uploads")
    )
    os.makedirs(upload_folder, exist_ok=True)

    image_path = os.path.join(upload_folder, final_name)
    file_storage.save(image_path)
    return final_name


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
            front_image_file = request.files.get('front_image')
            back_image_file = request.files.get('back_image')

            front_image_filename = save_uploaded_image(front_image_file, deck_id, 'front')
            back_image_filename = save_uploaded_image(back_image_file, deck_id, 'back')

            if front_image_file and front_image_file.filename and front_image_filename is None:
                flash('Front image must be png, jpg, jpeg, gif, or webp.', 'error')
                return render_template('card_form.html', deck=deck, card=None, action='Create')

            if back_image_file and back_image_file.filename and back_image_filename is None:
                flash('Back image must be png, jpg, jpeg, gif, or webp.', 'error')
                return render_template('card_form.html', deck=deck, card=None, action='Create')

            create_card(
                deck_id,
                front,
                back,
                front_image_filename,
                back_image_filename
            )

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
            front_image_filename = card['front_image_filename']
            back_image_filename = card['back_image_filename']

            front_image_file = request.files.get('front_image')
            back_image_file = request.files.get('back_image')

            if front_image_file and front_image_file.filename:
                saved_front = save_uploaded_image(front_image_file, deck_id, 'front')
                if saved_front is None:
                    flash('Front image must be png, jpg, jpeg, gif, or webp.', 'error')
                    return render_template('card_form.html', deck=deck, card=card, action='Edit')
                front_image_filename = saved_front

            if back_image_file and back_image_file.filename:
                saved_back = save_uploaded_image(back_image_file, deck_id, 'back')
                if saved_back is None:
                    flash('Back image must be png, jpg, jpeg, gif, or webp.', 'error')
                    return render_template('card_form.html', deck=deck, card=card, action='Edit')
                back_image_filename = saved_back

            update_card(
                card_id,
                deck_id,
                front,
                back,
                front_image_filename,
                back_image_filename
            )

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