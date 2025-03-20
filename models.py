from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    elo = db.Column(db.Float, default=1000)
    starting_elo = db.Column(db.Float, default=1000)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    team1_players = db.Column(db.String(200))  # Store as comma-separated player IDs
    team2_players = db.Column(db.String(200))
    winner = db.Column(db.Integer)  # 1 or 2
    sequence = db.Column(db.Integer)  # To track game order for recalculation 