from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(7), default='#e94560')
    icon = db.Column(db.String(50), default='gamepad-2')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    games = db.relationship('Game', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'icon': self.icon,
        }


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    min_players = db.Column(db.Integer, default=1)
    max_players = db.Column(db.Integer, default=10)
    image_url = db.Column(db.String(500), default='')
    is_favorite = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    play_history = db.relationship('PlayHistory', backref='game', lazy=True,
                                   cascade='all, delete-orphan')

    @property
    def play_count(self):
        return len(self.play_history)

    @property
    def last_played(self):
        if self.play_history:
            return max(h.played_at for h in self.play_history)
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else None,
            'min_players': self.min_players,
            'max_players': self.max_players,
            'image_url': self.image_url,
            'is_favorite': self.is_favorite,
            'is_active': self.is_active,
            'play_count': self.play_count,
            'last_played': self.last_played.isoformat() if self.last_played else None,
        }


class PlayHistory(db.Model):
    __tablename__ = 'play_history'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    played_at = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    notes = db.Column(db.Text, default='')
    rating = db.Column(db.Integer, default=0)  # 0-5 stars
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'game_name': self.game.name if self.game else '',
            'played_at': self.played_at.isoformat(),
            'notes': self.notes,
            'rating': self.rating,
        }
