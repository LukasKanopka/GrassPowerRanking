from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    players = db.relationship('Player', backref='series', lazy=True, cascade="all, delete-orphan")
    games = db.relationship('Game', backref='series', lazy=True, cascade="all, delete-orphan")

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    elo = db.Column(db.Float, default=1000)
    starting_elo = db.Column(db.Float, default=1000)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    
    # Make player names unique per series
    __table_args__ = (db.UniqueConstraint('name', 'series_id', name='unique_player_per_series'),)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    team1_players = db.Column(db.String(200))  # Store as comma-separated player IDs
    team2_players = db.Column(db.String(200))
    winner = db.Column(db.Integer)  # 1 or 2
    sequence = db.Column(db.Integer)  # To track game order for recalculation
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False) 