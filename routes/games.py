import json
from flask import Blueprint, render_template, request, jsonify, Response
from models import Game, Category, PlayHistory, db
from datetime import datetime, timezone

games_bp = Blueprint('games', __name__)


@games_bp.route('/games')
def games_list():
    categories = Category.query.order_by(Category.name).all()
    category_filter = request.args.get('category', type=int)

    query = Game.query.filter_by(is_active=True)
    if category_filter:
        query = query.filter_by(category_id=category_filter)

    games = query.order_by(Game.name).all()
    return render_template('games.html',
                           games=games,
                           categories=categories,
                           selected_category=category_filter)


@games_bp.route('/games', methods=['POST'])
def add_game():
    name = request.form.get('name', '').strip()
    category_id = request.form.get('category_id', type=int)
    min_players = request.form.get('min_players', 1, type=int)
    max_players = request.form.get('max_players', 10, type=int)
    image_url = request.form.get('image_url', '').strip()

    if not name:
        return '<div class="toast error">กรุณาใส่ชื่อเกม</div>', 400

    existing = Game.query.filter_by(name=name, is_active=True).first()
    if existing:
        return '<div class="toast error">มีเกมนี้อยู่แล้ว</div>', 400

    game = Game(
        name=name,
        category_id=category_id if category_id else None,
        min_players=min_players,
        max_players=max_players,
        image_url=image_url,
    )
    db.session.add(game)
    db.session.commit()

    games = Game.query.filter_by(is_active=True).order_by(Game.name).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('components/game_list.html', games=games, categories=categories)


@games_bp.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    game = Game.query.get_or_404(game_id)

    game.name = request.form.get('name', game.name).strip()
    game.category_id = request.form.get('category_id', type=int) or None
    game.min_players = request.form.get('min_players', game.min_players, type=int)
    game.max_players = request.form.get('max_players', game.max_players, type=int)
    game.image_url = request.form.get('image_url', game.image_url).strip()

    db.session.commit()

    games = Game.query.filter_by(is_active=True).order_by(Game.name).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('components/game_list.html', games=games, categories=categories)


@games_bp.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    game.is_active = False
    db.session.commit()

    games = Game.query.filter_by(is_active=True).order_by(Game.name).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('components/game_list.html', games=games, categories=categories)


@games_bp.route('/games/<int:game_id>/favorite', methods=['POST'])
def toggle_favorite(game_id):
    game = Game.query.get_or_404(game_id)
    game.is_favorite = not game.is_favorite
    db.session.commit()

    games = Game.query.filter_by(is_active=True).order_by(Game.name).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('components/game_list.html', games=games, categories=categories)


@games_bp.route('/categories', methods=['POST'])
def add_category():
    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#e94560')
    icon = request.form.get('icon', 'gamepad-2')

    if not name:
        return '<div class="toast error">กรุณาใส่ชื่อหมวดหมู่</div>', 400

    existing = Category.query.filter_by(name=name).first()
    if existing:
        return '<div class="toast error">มีหมวดหมู่นี้อยู่แล้ว</div>', 400

    cat = Category(name=name, color=color, icon=icon)
    db.session.add(cat)
    db.session.commit()

    categories = Category.query.order_by(Category.name).all()
    return render_template('components/category_options.html', categories=categories)


@games_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    # Unlink games from this category
    Game.query.filter_by(category_id=cat_id).update({'category_id': None})
    db.session.delete(cat)
    db.session.commit()

    categories = Category.query.order_by(Category.name).all()
    return render_template('components/category_options.html', categories=categories)


@games_bp.route('/export')
def export_data():
    games = Game.query.all()
    categories = Category.query.all()
    history = PlayHistory.query.all()

    data = {
        'version': '1.0',
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'categories': [c.to_dict() for c in categories],
        'games': [g.to_dict() for g in games],
        'history': [h.to_dict() for h in history],
    }

    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    return Response(
        json_str,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=somua_backup.json'}
    )


@games_bp.route('/import', methods=['POST'])
def import_data():
    file = request.files.get('file')
    if not file:
        return '<div class="toast error">กรุณาเลือกไฟล์</div>', 400

    try:
        data = json.loads(file.read().decode('utf-8'))

        # Import categories
        for cat_data in data.get('categories', []):
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                cat = Category(name=cat_data['name'],
                             color=cat_data.get('color', '#e94560'),
                             icon=cat_data.get('icon', 'gamepad-2'))
                db.session.add(cat)

        db.session.flush()

        # Import games
        for game_data in data.get('games', []):
            existing = Game.query.filter_by(name=game_data['name']).first()
            if not existing:
                cat = None
                if game_data.get('category'):
                    cat = Category.query.filter_by(
                        name=game_data['category']['name']
                    ).first()

                game = Game(
                    name=game_data['name'],
                    category_id=cat.id if cat else None,
                    min_players=game_data.get('min_players', 1),
                    max_players=game_data.get('max_players', 10),
                    image_url=game_data.get('image_url', ''),
                    is_favorite=game_data.get('is_favorite', False),
                    is_active=game_data.get('is_active', True),
                )
                db.session.add(game)

        db.session.commit()
        return '<div class="toast success">นำเข้าข้อมูลสำเร็จ!</div>'

    except Exception as e:
        db.session.rollback()
        return f'<div class="toast error">เกิดข้อผิดพลาด: {str(e)}</div>', 400


@games_bp.route('/games/<int:game_id>/edit')
def edit_game_form(game_id):
    game = Game.query.get_or_404(game_id)
    categories = Category.query.order_by(Category.name).all()
    return render_template('components/edit_game_form.html',
                           game=game,
                           categories=categories)
