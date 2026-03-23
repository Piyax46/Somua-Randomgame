from flask import Blueprint, render_template, request, jsonify
from models import Game, Category, PlayHistory, db
from services.randomizer import pick_random_game, get_all_weights
from datetime import datetime, timezone

spin_bp = Blueprint('spin', __name__)


@spin_bp.route('/')
def index():
    games = Game.query.filter_by(is_active=True).all()
    today = datetime.now(timezone(timedelta(hours=7))).date()
    today_play = PlayHistory.query.filter_by(played_at=today).first()
    weights = get_all_weights()
    return render_template('index.html',
                           games=games,
                           today_play=today_play,
                           weights=weights)


@spin_bp.route('/spin', methods=['POST'])
def spin():
    selected, weights = pick_random_game()
    if not selected:
        return '<div class="empty-state"><p>ยังไม่มีเกมในระบบ เพิ่มเกมก่อนนะ!</p></div>'

    return render_template('components/spin_result.html',
                           game=selected,
                           weights=weights)


@spin_bp.route('/spin/wheel', methods=['POST'])
def spin_wheel():
    """JSON endpoint for fortune wheel animation."""
    selected, weights = pick_random_game()
    if not selected:
        return jsonify({'error': 'no_games'}), 400

    segments = []
    selected_index = 0
    for i, w in enumerate(weights):
        game = w['game']
        seg = {
            'name': game.name,
            'image': game.image_url or '',
            'category': game.category.name if game.category else '',
            'color': game.category.color if game.category else '#7c5cfc',
            'weight': w['weight'],
            'percentage': w['percentage'],
        }
        segments.append(seg)
        if game.id == selected.id:
            selected_index = i

    return jsonify({
        'selected_index': selected_index,
        'selected': {
            'id': selected.id,
            'name': selected.name,
            'image_url': selected.image_url or '',
            'category': selected.category.name if selected.category else '',
            'min_players': selected.min_players,
            'max_players': selected.max_players,
            'play_count': selected.play_count,
        },
        'segments': segments,
    })


@spin_bp.route('/spin/accept', methods=['POST'])
def accept_spin():
    game_id = request.form.get('game_id', type=int)
    notes = request.form.get('notes', '')

    if not game_id:
        return '<div class="toast error">ไม่พบเกม</div>', 400

    game = Game.query.get(game_id)
    if not game:
        return '<div class="toast error">ไม่พบเกม</div>', 404

    today = datetime.now(timezone(timedelta(hours=7))).date()

    history = PlayHistory(
        game_id=game_id,
        played_at=today,
        notes=notes,
    )
    db.session.add(history)
    db.session.commit()

    weights = get_all_weights()
    return render_template('components/accepted.html',
                           game=game,
                           history=history,
                           weights=weights)


@spin_bp.route('/weights')
def weights_panel():
    weights = get_all_weights()
    return render_template('components/weights_panel.html', weights=weights)
