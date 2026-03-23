import os
from flask import Flask
from models import db, Category


def create_app():
    app = Flask(__name__)

    # Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Check for Railway PostgreSQL Database URL
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        # SQLAlchemy 1.4+ requires postgresql:// instead of postgres://
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or f'sqlite:///{os.path.join(basedir, "gamedb.sqlite")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'somua-secret-key-2024')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes.spin import spin_bp
    from routes.games import games_bp
    from routes.history import history_bp
    from routes.stats import stats_bp
    from routes.heroes import heroes_bp

    app.register_blueprint(spin_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(heroes_bp)

    # Create tables and seed defaults
    with app.app_context():
        db.create_all()
        seed_default_categories()

    return app


def seed_default_categories():
    """Add default categories if none exist."""
    if Category.query.count() == 0:
        defaults = [
            Category(name='FPS', color='#ef4444', icon='crosshair'),
            Category(name='MOBA', color='#8b5cf6', icon='swords'),
            Category(name='RPG', color='#06b6d4', icon='shield'),
            Category(name='Party', color='#f59e0b', icon='party-popper'),
            Category(name='Strategy', color='#22c55e', icon='brain'),
            Category(name='Horror', color='#6b7280', icon='ghost'),
            Category(name='Racing', color='#ec4899', icon='car'),
            Category(name='Sports', color='#14b8a6', icon='trophy'),
        ]
        for cat in defaults:
            db.session.add(cat)
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
