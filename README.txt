# ELO Tracker

A Flask-based web application to track player ELO rankings for team-based games.

## Features

- Player Management
  - Each player starts with 1000 ELO (750 for Keagan)
  - Players are ranked on the leaderboard by their current ELO score

- Game Management
  - Create new games with two teams
  - View game history
  - Edit existing games (adjust teams or winners)
  - Delete games

- ELO System
  - ELO changes are calculated based on the relative strength of teams
  - Winning a game against a stronger team gives more ELO points
  - Formula: Base change (50) * (loser_avg_elo / winner_avg_elo)
  - The entire history of games is maintained for recalculating ELOs

## Setup

1. Install required packages: 

pip install flask flask-sqlalchemy


2. Initialize the database:

python migrate_scores.py  # Add players
python migrate_games.py   # Add game history (optional)

3. Run the application:
```
python app.py
```

4. Access the application at http://localhost:5000

## File Structure

- `app.py` - Main Flask application
- `models.py` - Database models for Player and Game
- `migrate_scores.py` - Script to initialize players
- `migrate_games.py` - Script to import game history
- `game.py` - Original game logic (not used by the web app)
- `player.py` - Original player class (not used by the web app)
- `templates/` - HTML templates
  - `base.html` - Base template with navigation
  - `leaderboard.html` - Player rankings
  - `new_game.html` - Create new games
  - `games.html` - Game history
  - `edit_game.html` - Edit existing games

## Usage

1. Leaderboard - View current player rankings
2. New Game - Create a new game:
   - Select players for each team
   - Choose the winner
   - Save to update ELOs
3. Games History - View and manage past games:
   - See all recorded games
   - Edit team composition or winners
   - Delete games (will recalculate all ELOs)

## Notes

- When editing or deleting games, all player ELOs are recalculated from scratch
- Games are processed in sequence order to maintain the correct ELO progression
- The database is stored in a SQLite file (`elo.db`)