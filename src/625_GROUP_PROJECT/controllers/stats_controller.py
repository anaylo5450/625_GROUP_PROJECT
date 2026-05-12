from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from controllers.auth_controller import login_required
from models.stats_model import create_session, finish_session, get_deck_stats, get_user_stats
from models.deck_model import get_deck_by_id_for_user, get_public_deck
stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/stats')
@login_required
def overview():
    per_deck, overall, daily = get_user_stats(session['user_id'])
    return render_template(
        'stats_overview.html',
        per_deck=per_deck,
        overall=overall,
        daily=daily
    )

@stats_bp.route('/deck/<int:deck_id>/stats')
@login_required
def deck_stats(deck_id):
    deck = get_deck_by_id_for_user(deck_id, session['user_id'])

    if not deck:
        deck = get_public_deck(deck_id)

    if not deck:
        return redirect(url_for('deck.dashboard'))

    sessions, summary, daily_progress = get_deck_stats(deck_id, session['user_id'])

    valid_progress = [row for row in daily_progress if row.get('score_percent') is not None]
    labels = [row['study_day'] for row in valid_progress]
    scores = [int(row['score_percent']) for row in valid_progress]

    return render_template(
        'stats_deck.html',
        deck=dict(deck),
        sessions=sessions,
        summary=summary,
        labels=labels,
        scores=scores
    )

@stats_bp.route('/api/session/start', methods=['POST'])
@login_required
def api_start_session():
    data = request.get_json()
    sid = create_session(
        session['user_id'],
        data['deck_id'],
        data['cards_total']
    )
    return jsonify({'session_id': sid})

@stats_bp.route('/api/session/finish', methods=['POST'])
@login_required
def api_finish_session():
    data = request.get_json()
    finish_session(
        data['session_id'],
        data['cards_seen'],
        data['cards_correct'],
        data['cards_wrong'],
        data['duration_seconds'],
        data['completed']
    )
    return jsonify({'ok': True})