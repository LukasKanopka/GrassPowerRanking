from app import app, db
from models import Player

def migrate_scores():
    with app.app_context():
        # First, delete all existing players
        Player.query.delete()
        db.session.commit()  # Commit the deletion
        
        # Then add new players...
        # Current players and their ELOs from your main.py
        players_data = [
            ("Lukas", 1000),
            ("Cade", 1000),
            ("Alex", 1000),
            ("Marshall", 1000),
            ("Arvin", 1000),
            ("Taylor", 1000),
            ("Jenessa", 1000),
            ("Keagan", 750)
        ]
        
        # Add each player to the database
        for name, elo in players_data:
            player = Player(name=name, elo=elo)
            db.session.add(player)
        
        # Commit the changes
        try:
            db.session.commit()
            print("Successfully added all players!")
            
            # Print the results
            all_players = Player.query.order_by(Player.elo.desc()).all()
            print("\nCurrent players:")
            for player in all_players:
                print(f"{player.name}: {player.elo}")
                
        except Exception as e:
            print(f"Error adding players: {e}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_scores() 