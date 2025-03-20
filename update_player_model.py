from app import app, db
from models import Player
import sqlite3

with app.app_context():
    # Get the database path from the app config
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # Use SQLite connection directly to add the column
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add the column if it doesn't exist
        cursor.execute("PRAGMA table_info(player)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'starting_elo' not in columns:
            cursor.execute("ALTER TABLE player ADD COLUMN starting_elo FLOAT DEFAULT 1000")
            conn.commit()
            print("Added starting_elo column to player table")
    except Exception as e:
        print(f"Error adding column: {e}")
    finally:
        conn.close()
    
    # Now update the values through SQLAlchemy
    players = Player.query.all()
    for player in players:
        if player.name == "Keagan":
            player.starting_elo = 750
        elif player.name == "Tiffany":
            player.starting_elo = 800
        else:
            player.starting_elo = 1000
    
    db.session.commit()
    print("Updated starting ELOs for all players") 