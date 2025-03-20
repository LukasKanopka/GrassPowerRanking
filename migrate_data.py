from app import app, db
from models import Player, Game
from main import players  # Import your existing players data

def migrate_existing_data():
    with app.app_context():
        # First, make sure the database tables exist
        db.create_all()
        
        # Migrate players and their current ELOs
        for existing_player in players:
            player = Player(
                name=existing_player.name,
                elo=existing_player.elo
            )
            db.session.add(player)
        
        try:
            db.session.commit()
            print("Successfully migrated player data!")
            
            # Print migrated data to verify
            all_players = Player.query.order_by(Player.elo.desc()).all()
            print("\nMigrated players:")
            for player in all_players:
                print(f"{player.name}: {player.elo}")
                
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_existing_data() 