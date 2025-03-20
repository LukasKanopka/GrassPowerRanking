from app import app, db
from models import Series, Player, Game
from datetime import datetime, timedelta

def migrate_games():
    with app.app_context():
        # Get or create default series
        default_series = Series.query.filter_by(name="Default Series").first()
        if not default_series:
            default_series = Series(name="Default Series", description="Original ranking series")
            db.session.add(default_series)
            db.session.commit()
            print("Created default series for migration")

        # Get player IDs from the default series
        players = Player.query.filter_by(series_id=default_series.id).all()
        player_ids = {player.name: str(player.id) for player in players}
        
        # Your existing game patterns and dates
        patterns = [
            # Add your game patterns here as before
            # Example:
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

        sequence = 1
        for pattern in patterns:
            teams = pattern["teams"]
            start_date = pattern["start_date"]
            
            # Handle patterns with repeats
            if "repeats" in pattern:
                winner = pattern["winner"]
                for i in range(pattern["repeats"]):
                    # Get player IDs for the current series
                    team1_ids = [player_ids[name] for name in teams[0]]
                    team2_ids = [player_ids[name] for name in teams[1]]
                    
                    game_date = start_date + timedelta(days=sequence)
                    
                    game = Game(
                        team1_players=','.join(team1_ids),
                        team2_players=','.join(team2_ids),
                        winner=winner,
                        sequence=sequence,
                        date=game_date,
                        series_id=default_series.id
                    )
                    db.session.add(game)
                    sequence += 1

        try:
            db.session.commit()
            print(f"Successfully migrated {sequence-1} games to series '{default_series.name}'")
            
            # Print imported games with series context
            games = Game.query.filter_by(series_id=default_series.id).order_by(Game.sequence).all()
            for game in games:
                team1_names = [Player.query.filter_by(id=int(pid), series_id=default_series.id).first().name 
                              for pid in game.team1_players.split(',')]
                team2_names = [Player.query.filter_by(id=int(pid), series_id=default_series.id).first().name 
                              for pid in game.team2_players.split(',')]
                print(f"Game #{game.sequence}: {', '.join(team1_names)} vs {', '.join(team2_names)} - Winner: Team {game.winner}")
            
            # Recalculate ELOs for this series
            from app import recalculate_all_elos
            recalculate_all_elos(default_series.id)
            
            # Print final ELOs for the series
            print(f"\nFinal player ELOs for '{default_series.name}':")
            players = Player.query.filter_by(series_id=default_series.id).order_by(Player.elo.desc()).all()
            for player in players:
                print(f"{player.name}: {player.elo:.2f}")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_games() 