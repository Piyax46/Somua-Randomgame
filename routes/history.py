from flask import Blueprint, render_template, request
from models import PlayHistory, Game, db
from services.stats import get_monthly_history
from datetime import datetime, timezone

history_bp = Blueprint('history', __name__)


@history_bp.route('/history')
def history():
    today = datetime.now(timezone.utc).date()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    days, start_date, end_date = get_monthly_history(year, month)

    # Navigation
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    games = Game.query.filter_by(is_active=True).order_by(Game.name).all()

    return render_template('history.html',
                           days=days,
                           year=year,
                           month=month,
                           start_date=start_date,
                           end_date=end_date,
                           prev_month=prev_month,
                           prev_year=prev_year,
                           next_month=next_month,
                           next_year=next_year,
                           today=today,
                           games=games)


@history_bp.route('/history/calendar')
def history_calendar():
    today = datetime.now(timezone.utc).date()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    days, start_date, end_date = get_monthly_history(year, month)

    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    return render_template('components/calendar.html',
                           days=days,
                           year=year,
                           month=month,
                           start_date=start_date,
                           end_date=end_date,
                           prev_month=prev_month,
                           prev_year=prev_year,
                           next_month=next_month,
                           next_year=next_year,
                           today=today)


@history_bp.route('/history', methods=['POST'])
def add_history():
    game_id = request.form.get('game_id', type=int)
    date_str = request.form.get('played_at', '')
    notes = request.form.get('notes', '')

    if not game_id or not date_str:
        return '<div class="toast error">กรุณาเลือกเกมและวันที่</div>', 400

    played_at = datetime.strptime(date_str, '%Y-%m-%d').date()

    history = PlayHistory(
        game_id=game_id,
        played_at=played_at,
        notes=notes,
    )
    db.session.add(history)
    db.session.commit()

    today = datetime.now(timezone.utc).date()
    year = played_at.year
    month = played_at.month
    days, start_date, end_date = get_monthly_history(year, month)

    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    return render_template('components/calendar.html',
                           days=days,
                           year=year,
                           month=month,
                           start_date=start_date,
                           end_date=end_date,
                           prev_month=prev_month,
                           prev_year=prev_year,
                           next_month=next_month,
                           next_year=next_year,
                           today=today)


@history_bp.route('/history/<int:history_id>', methods=['DELETE'])
def delete_history(history_id):
    h = PlayHistory.query.get_or_404(history_id)
    year = h.played_at.year
    month = h.played_at.month
    db.session.delete(h)
    db.session.commit()

    today = datetime.now(timezone.utc).date()
    days, start_date, end_date = get_monthly_history(year, month)

    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    return render_template('components/calendar.html',
                           days=days,
                           year=year,
                           month=month,
                           start_date=start_date,
                           end_date=end_date,
                           prev_month=prev_month,
                           prev_year=prev_year,
                           next_month=next_month,
                           next_year=next_year,
                           today=today)
