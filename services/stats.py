from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from models import Game, PlayHistory, Category, db


def get_dashboard_stats():
    """Get overview stats for dashboard."""
    total_games = Game.query.filter_by(is_active=True).count()
    total_plays = PlayHistory.query.count()
    total_categories = Category.query.count()

    today = datetime.now(timezone.utc).date()
    today_play = PlayHistory.query.filter_by(played_at=today).first()

    # Most played games
    most_played = db.session.query(
        Game.name,
        Game.id,
        func.count(PlayHistory.id).label('count')
    ).join(PlayHistory).group_by(Game.id).order_by(
        func.count(PlayHistory.id).desc()
    ).limit(5).all()

    # Least played active games
    least_played_games = db.session.query(
        Game,
        func.coalesce(func.count(PlayHistory.id), 0).label('count')
    ).outerjoin(PlayHistory).filter(
        Game.is_active == True
    ).group_by(Game.id).order_by('count').limit(5).all()

    # Play streak (consecutive days)
    streak = calculate_streak()

    # Recent history
    recent = PlayHistory.query.order_by(
        PlayHistory.played_at.desc()
    ).limit(10).all()

    # Category distribution
    category_dist = db.session.query(
        Category.name,
        Category.color,
        func.count(PlayHistory.id).label('count')
    ).join(Game, Game.category_id == Category.id).join(
        PlayHistory, PlayHistory.game_id == Game.id
    ).group_by(Category.id).order_by(
        func.count(PlayHistory.id).desc()
    ).all()

    # Monthly play counts (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly_plays = db.session.query(
        func.strftime('%Y-%m', PlayHistory.played_at).label('month'),
        func.count(PlayHistory.id).label('count')
    ).filter(
        PlayHistory.played_at >= six_months_ago
    ).group_by('month').order_by('month').all()

    return {
        'total_games': total_games,
        'total_plays': total_plays,
        'total_categories': total_categories,
        'today_play': today_play,
        'most_played': most_played,
        'least_played': least_played_games,
        'streak': streak,
        'recent': recent,
        'category_dist': category_dist,
        'monthly_plays': monthly_plays,
    }


def calculate_streak():
    """Calculate current consecutive days played."""
    today = datetime.now(timezone.utc).date()
    streak = 0
    current_date = today

    while True:
        has_play = PlayHistory.query.filter_by(played_at=current_date).first()
        if has_play:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break

    return streak


def get_monthly_history(year, month):
    """Get play history grouped by day for a given month."""
    from calendar import monthrange

    _, last_day = monthrange(year, month)
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, last_day).date()

    history = PlayHistory.query.filter(
        PlayHistory.played_at >= start_date,
        PlayHistory.played_at <= end_date
    ).order_by(PlayHistory.played_at).all()

    days = {}
    for h in history:
        day_key = h.played_at.isoformat()
        if day_key not in days:
            days[day_key] = []
        days[day_key].append(h)

    return days, start_date, end_date
