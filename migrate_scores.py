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
            ("Lukas", 1134.19085563341),
            ("Cade", 1005.5149580901099),
            ("Alex", 994.4003280910782),
            ("Marshall", 865.8938581854017),
            ("Arvin", 865.80914436659),
            ("Taylor", 1109.6252534724383),
            ("Jenessa", 890.459460346373),
            ("Keagan", 640.3747465275613)  # This player started with 750 in your main.py
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