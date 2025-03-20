from app import app, db
from models import Player, Game

with app.app_context():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    print("Database recreated with new schema")
    
    # Add your players
    players_data = [
        ("Lukas", 1000),
        ("Cade", 1000),
        ("Alex", 1000),
        ("Marshall", 1000),
        ("Arvin", 1000),
        ("Taylor", 1000),
        ("Jenessa", 1000),
        ("Keagan", 750),
        ("Tiffany", 800)  # Add Tiffany with 800 ELO
    ]
    
    # Add each player to the database with matching starting_elo
    for name, elo in players_data:
        player = Player(name=name, elo=elo, starting_elo=elo)
        db.session.add(player)
    
    db.session.commit()
    print("Players added with correct starting ELOs") 