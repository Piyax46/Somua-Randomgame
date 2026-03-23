import random
from datetime import datetime, timedelta, timezone
from models import Game, PlayHistory, db


def calculate_weight(game, all_history):
    """
    Calculate weight for a game based on play history.
    Games played more often get lower weight.
    Games played recently get additional penalty.
    """
    base_weight = 100.0

    game_history = [h for h in all_history if h.game_id == game.id]
    play_count = len(game_history)

    # Penalty for how many times played overall
    play_count_penalty = play_count * 12

    # Cooldown: penalty if played in last 3 days
    today = datetime.now(timezone(timedelta(hours=7))).date()
    cooldown_penalty = 0
    recency_penalty = 0

    if game_history:
        last_played = max(h.played_at for h in game_history)
        days_since = (today - last_played).days

        if days_since == 0:
            recency_penalty = 60  # played today
        elif days_since == 1:
            recency_penalty = 40  # played yesterday
        elif days_since <= 3:
            cooldown_penalty = 25  # played within 3 days

    # Favorite bonus (slight boost)
    favorite_bonus = 5 if game.is_favorite else 0

    weight = base_weight - play_count_penalty - cooldown_penalty - recency_penalty + favorite_bonus

    return max(3.0, weight)


def pick_random_game(exclude_ids=None):
    """
    Pick a random game using weighted selection.
    Returns (game, weights_info) tuple.
    """
    games = Game.query.filter_by(is_active=True).all()

    if not games:
        return None, []

    if exclude_ids:
        games = [g for g in games if g.id not in exclude_ids]

    if not games:
        return None, []

    all_history = PlayHistory.query.all()

    weights_info = []
    for game in games:
        w = calculate_weight(game, all_history)
        weights_info.append({
            'game': game,
            'weight': w,
            'play_count': len([h for h in all_history if h.game_id == game.id]),
        })

    total_weight = sum(wi['weight'] for wi in weights_info)
    for wi in weights_info:
        wi['percentage'] = round((wi['weight'] / total_weight) * 100, 1) if total_weight > 0 else 0

    weights = [wi['weight'] for wi in weights_info]
    selected = random.choices(games, weights=weights, k=1)[0]

    return selected, weights_info


def get_all_weights():
    """Get weight information for all active games."""
    games = Game.query.filter_by(is_active=True).all()
    all_history = PlayHistory.query.all()

    weights_info = []
    total_weight = 0

    for game in games:
        w = calculate_weight(game, all_history)
        total_weight += w
        weights_info.append({
            'game': game,
            'weight': w,
            'play_count': len([h for h in all_history if h.game_id == game.id]),
        })

    for wi in weights_info:
        wi['percentage'] = round((wi['weight'] / total_weight) * 100, 1) if total_weight > 0 else 0

    weights_info.sort(key=lambda x: x['weight'], reverse=True)
    return weights_info
