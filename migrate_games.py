from app import app, db
from models import Series, Player, Game
from datetime import datetime, timedelta
import sqlite3

def migrate_games():
    with app.app_context():
        # First ensure database structure
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Make sure series_id column exists
            cursor.execute("PRAGMA table_info(player)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'series_id' not in columns:
                cursor.execute("ALTER TABLE player ADD COLUMN series_id INTEGER")
                print("Added series_id column to player table")
            
            cursor.execute("PRAGMA table_info(game)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'series_id' not in columns:
                cursor.execute("ALTER TABLE game ADD COLUMN series_id INTEGER")
                print("Added series_id column to game table")
            
            conn.commit()
        except Exception as e:
            print(f"Schema update error: {e}")
        finally:
            conn.close()
        
        # Get or create default series
        default_series = Series.query.filter_by(name="Default Series").first()
        if not default_series:
            default_series = Series(name="Default Series", description="Original ranking series")
            db.session.add(default_series)
            db.session.commit()
            print("Created default series for migration")
        
        # Associate existing players with the default series if not already
        players_to_update = Player.query.filter(Player.series_id.is_(None)).all()
        for player in players_to_update:
            player.series_id = default_series.id
        if players_to_update:
            db.session.commit()
            print(f"Associated {len(players_to_update)} existing players with the default series")
        
        # Clean existing games in this series to avoid duplicates
        Game.query.filter_by(series_id=default_series.id).delete()
        db.session.commit()
        print("Cleared existing games from default series")
        
        # Get player IDs from the default series
        players = Player.query.filter_by(series_id=default_series.id).all()
        player_ids = {player.name: str(player.id) for player in players}
        print(f"Found {len(player_ids)} players in default series")
        
        # Define game patterns
        patterns = [
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
        
        # Default start date if none specified
        default_start_date = datetime.now() - timedelta(days=30)
        
        sequence = 1
        games_created = 0
        
        for pattern in patterns:
            teams = pattern["teams"]
            start_date = pattern.get("start_date", default_start_date)
            
            # Make sure all players exist in the database
            team1_ids = []
            for name in teams[0]:
                if name in player_ids:
                    team1_ids.append(player_ids[name])
                else:
                    print(f"Creating missing player '{name}' in default series")
                    new_player = Player(
                        name=name,
                        elo=1000,
                        starting_elo=1000,
                        series_id=default_series.id
                    )
                    db.session.add(new_player)
                    db.session.flush()  # Get the ID without committing
                    player_ids[name] = str(new_player.id)
                    team1_ids.append(player_ids[name])
            
            team2_ids = []
            for name in teams[1]:
                if name in player_ids:
                    team2_ids.append(player_ids[name])
                else:
                    print(f"Creating missing player '{name}' in default series")
                    new_player = Player(
                        name=name,
                        elo=1000,
                        starting_elo=1000,
                        series_id=default_series.id
                    )
                    db.session.add(new_player)
                    db.session.flush()  # Get the ID without committing
                    player_ids[name] = str(new_player.id)
                    team2_ids.append(player_ids[name])
            
            # Handle different pattern formats
            if "winners" in pattern:
                # Multiple games with different winners
                winners = pattern["winners"]
                for winner in winners:
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
                    games_created += 1
            
            elif "winner" in pattern:
                # Single winner possibly repeated
                winner = pattern["winner"]
                repeats = pattern.get("repeats", 1)
                
                for i in range(repeats):
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
                    games_created += 1
            
            else:
                print(f"Warning: Pattern skipped, no winner information")

        try:
            db.session.commit()
            print(f"Successfully migrated {games_created} games to series '{default_series.name}'")
            
            # Print imported games with series context
            games = Game.query.filter_by(series_id=default_series.id).order_by(Game.sequence).all()
            print(f"\nGames imported to '{default_series.name}':")
            for game in games:
                team1_names = []
                team2_names = []
                
                for pid in game.team1_players.split(','):
                    player = Player.query.filter_by(id=int(pid), series_id=default_series.id).first()
                    if player:
                        team1_names.append(player.name)
                
                for pid in game.team2_players.split(','):
                    player = Player.query.filter_by(id=int(pid), series_id=default_series.id).first()
                    if player:
                        team2_names.append(player.name)
                
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