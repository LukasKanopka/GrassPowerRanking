from app import app, db
from models import Player, Game
from datetime import datetime, timedelta

def migrate_games():
    with app.app_context():
        # First, make sure tables exist
        db.create_all()
        
        # Import games from main.py
        game_patterns = [
            {
                "teams": [
                    ["Lukas", "Alex", "Taylor"],  # Team 1
                    ["Cade", "Marshall", "Arvin", "Jenessa"]  # Team 2
                ],
                "winner": 1,  # Team 1 won
                "repeats": 3  # This game pattern repeats 3 times
            },
            {
                "teams": [
                    ["Lukas", "Marshall", "Taylor", "Jenessa"],  # Team 1
                    ["Cade", "Alex", "Arvin"]  # Team 2
                ],
                "winners": [1, 2, 1, 2, 1]  # Alternating winners for 5 games
            },
            {
                "teams": [
                    ["Alex", "Marshall", "Taylor", "Arvin"],  # Team 1
                    ["Lukas", "Cade", "Jenessa", "Keagan"]  # Team 2
                ],
                "winners": [2, 2]  # Pattern of winners for 3 games
            },
            {
                "teams": [
                    ["Alex", "Lukas", "Jenessa", "Keagan"],  # Team 1
                    ["Cade", "Marshall", "Taylor", "Arvin"]  # Team 2
                ],
                "winners": [2, 1, 2]  # Pattern of winners for 3 games
            },
            {
                "teams": [
                    ["Alex", "Lukas"],  # Team 1
                    ["Cade", "Marshall"]  # Team 2
                ],
                "winners": [1, 1]  # Pattern of winners for 1 game
            },
            {
                "teams": [
                    ["Jenessa", "Lukas", "Tiffany", "Cade"],  # Team 1
                    ["Alex", "Marshall", "Taylor", "Arvin"]  # Team 2
                ],
                "winners": [1, 1]  # Pattern of winners for 1 game
            },
                        {
                "teams": [
                    ["Taylor", "Lukas", "Tiffany", "Marshall"],  # Team 1
                    ["Alex", "Cade", "Jenessa", "Arvin"]  # Team 2
                ],
                "winners": [1, 1]  # Pattern of winners for 1 game
            }
        ]
        
        # Delete existing games
        Game.query.delete()
        db.session.commit()
        
        # Player names to IDs mapping
        player_ids = {p.name: str(p.id) for p in Player.query.all()}
        
        # Start date (we'll space the games out over several days)
        start_date = datetime.now() - timedelta(days=14)
        
        sequence = 1
        for pattern in game_patterns:
            teams = pattern["teams"]
            
            # Handle patterns with multiple winners
            if "winners" in pattern:
                winners = pattern["winners"]
                for i, winner in enumerate(winners):
                    team1_ids = [player_ids[name] for name in teams[0]]
                    team2_ids = [player_ids[name] for name in teams[1]]
                    
                    game_date = start_date + timedelta(days=sequence)
                    
                    game = Game(
                        team1_players=','.join(team1_ids),
                        team2_players=','.join(team2_ids),
                        winner=winner,
                        sequence=sequence,
                        date=game_date
                    )
                    db.session.add(game)
                    sequence += 1
            
            # Handle patterns with repeats
            elif "repeats" in pattern:
                winner = pattern["winner"]
                for i in range(pattern["repeats"]):
                    team1_ids = [player_ids[name] for name in teams[0]]
                    team2_ids = [player_ids[name] for name in teams[1]]
                    
                    game_date = start_date + timedelta(days=sequence)
                    
                    game = Game(
                        team1_players=','.join(team1_ids),
                        team2_players=','.join(team2_ids),
                        winner=winner,
                        sequence=sequence,
                        date=game_date
                    )
                    db.session.add(game)
                    sequence += 1
        
        # Commit all games
        try:
            db.session.commit()
            print(f"Successfully migrated {sequence-1} games!")
            
            # Print info about the imported games
            games = Game.query.order_by(Game.sequence).all()
            for game in games:
                team1_names = [Player.query.get(int(pid)).name for pid in game.team1_players.split(',')]
                team2_names = [Player.query.get(int(pid)).name for pid in game.team2_players.split(',')]
                print(f"Game #{game.sequence}: {', '.join(team1_names)} vs {', '.join(team2_names)} - Winner: Team {game.winner}")
            
            # Now recalculate all player ELOs based on these games
            from app import recalculate_all_elos
            recalculate_all_elos()
            
            # Print final ELOs
            print("\nFinal player ELOs:")
            players = Player.query.order_by(Player.elo.desc()).all()
            for player in players:
                print(f"{player.name}: {player.elo:.2f}")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_games() 