from app import app, db
from models import Player, Game, Series
from datetime import datetime

with app.app_context():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    print("Database recreated with new schema")
    
    # Create default series
    default_series = Series(
        name="Default Series", 
        description="Initial ranking series",
        created_at=datetime.utcnow()
    )
    db.session.add(default_series)
    db.session.commit()
    print(f"Created default series with ID: {default_series.id}")
    
    # Add your players with series_id
    players_data = [
        ("Lukas", 1000),
        ("Cade", 1000),
        ("Alex", 1000),
        ("Marshall", 1000),
        ("Arvin", 1000),
        ("Taylor", 1000),
        ("Jenessa", 1000),
        ("Keagan", 750),
        ("Tiffany", 800)
    ]
    
    # Add each player to the database with matching starting_elo and series_id
    for name, elo in players_data:
        player = Player(
            name=name, 
            elo=elo, 
            starting_elo=elo,
            series_id=default_series.id
        )
        db.session.add(player)
    
    db.session.commit()
    print("Players added with correct starting ELOs") 