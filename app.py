from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Player, Game
from datetime import datetime
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Needed for flash messages

db.init_app(app)

@app.route('/')
def index():
    players = Player.query.order_by(Player.elo.desc()).all()
    return render_template('leaderboard.html', players=players)

@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    if request.method == 'POST':
        # Get selected players for each team
        team1 = request.form.getlist('team1')
        team2 = request.form.getlist('team2')
        winner = int(request.form['winner'])
        
        # Get the next sequence number
        last_game = Game.query.order_by(Game.sequence.desc()).first()
        next_seq = 1 if not last_game else last_game.sequence + 1
        
        # Create and save game
        game = Game(
            team1_players=','.join(team1),
            team2_players=','.join(team2),
            winner=winner,
            sequence=next_seq
        )
        db.session.add(game)
        
        # Update ELOs
        update_elos(team1, team2, winner)
        
        db.session.commit()
        return redirect(url_for('index'))
    
    players = Player.query.all()
    return render_template('new_game.html', players=players)

@app.route('/games')
def games():
    games_list = Game.query.order_by(Game.sequence).all()
    players = Player.query.all()
    
    # Create a dict for quick lookup
    players_dict = {str(p.id): p.name for p in players}
    
    formatted_games = []
    for game in games_list:
        team1_names = [players_dict[pid] for pid in game.team1_players.split(',')]
        team2_names = [players_dict[pid] for pid in game.team2_players.split(',')]
        
        formatted_games.append({
            'id': game.id,
            'date': game.date.strftime('%Y-%m-%d %H:%M'),
            'team1': ', '.join(team1_names),
            'team2': ', '.join(team2_names),
            'winner': 'Team 1' if game.winner == 1 else 'Team 2',
            'sequence': game.sequence
        })
    
    return render_template('games.html', games=formatted_games)

@app.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    game = Game.query.get_or_404(game_id)
    players = Player.query.all()
    
    if request.method == 'POST':
        # Get updated data
        team1 = request.form.getlist('team1')
        team2 = request.form.getlist('team2')
        winner = int(request.form['winner'])
        
        # Update game
        game.team1_players = ','.join(team1)
        game.team2_players = ','.join(team2)
        game.winner = winner
        
        db.session.commit()
        
        # Recalculate all ELOs
        recalculate_all_elos()
        
        flash('Game updated successfully!')
        return redirect(url_for('games'))
    
    # Pre-select existing teams
    team1_ids = game.team1_players.split(',')
    team2_ids = game.team2_players.split(',')
    
    return render_template('edit_game.html', 
                          game=game, 
                          players=players,
                          team1_ids=team1_ids,
                          team2_ids=team2_ids)

@app.route('/delete_game/<int:game_id>', methods=['POST'])
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    
    # Recalculate ELOs for all players
    recalculate_all_elos()
    
    flash('Game deleted successfully!')
    return redirect(url_for('games'))

def recalculate_all_elos():
    # Reset all player ELOs to starting values
    for player in Player.query.all():
        if player.name == "Keagan":
            player.elo = 750  # Special case for Keagan
        else:
            player.elo = 1000
    
    # Get all games ordered by sequence
    games = Game.query.order_by(Game.sequence).all()
    
    # Replay all games to recalculate ELOs
    for game in games:
        team1_ids = game.team1_players.split(',')
        team2_ids = game.team2_players.split(',')
        update_elos(team1_ids, team2_ids, game.winner)
    
    db.session.commit()

def update_elos(team1_ids, team2_ids, winner):
    # Get player objects
    team1 = [Player.query.get(int(id)) for id in team1_ids]
    team2 = [Player.query.get(int(id)) for id in team2_ids]
    
    # Calculate average ELOs
    team1_avg = sum(p.elo for p in team1) / len(team1)
    team2_avg = sum(p.elo for p in team2) / len(team2)
    
    # Calculate ELO changes
    base_change = 50
    if winner == 1:
        ratio = team2_avg / team1_avg
        team1_change = base_change * ratio
        team2_change = -base_change * ratio
    else:
        ratio = team1_avg / team2_avg
        team1_change = -base_change * ratio
        team2_change = base_change * ratio
    
    # Update ELOs
    for player in team1:
        player.elo += team1_change
    for player in team2:
        player.elo += team2_change

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 