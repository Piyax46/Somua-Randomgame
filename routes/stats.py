from flask import Blueprint, render_template
from services.stats import get_dashboard_stats

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/stats')
def stats():
    data = get_dashboard_stats()
    return render_template('stats.html', **data)
