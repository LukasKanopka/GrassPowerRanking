from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from models import db, Player, Game, Series
from datetime import datetime
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Needed for flash messages

db.init_app(app)

# Add this before_request handler to ensure a series is selected
@app.before_request
def ensure_series_selected():
    if request.endpoint in ['static']:
        return
    
    # Create default series if none exists
    if Series.query.count() == 0:
        default_series = Series(name="Default Series", description="Initial ranking series")
        db.session.add(default_series)
        db.session.commit()
    
    # Set current series in session if not already set
    if 'current_series_id' not in session:
        default_series = Series.query.first()
        session['current_series_id'] = default_series.id

# Series management routes
@app.route('/manage_series')
def manage_series():
    series_list = Series.query.order_by(Series.name).all()
    return render_template('manage_series.html', series_list=series_list)

@app.route('/series/select/<int:series_id>')
def select_series(series_id):
    series = Series.query.get_or_404(series_id)
    session['current_series_id'] = series_id
    flash(f'Switched to "{series.name}" series', 'success')
    return redirect(url_for('index'))

@app.route('/series/create', methods=['GET', 'POST'])
def create_series():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Series name is required', 'danger')
            return render_template('create_series.html')
        
        # Check if series with this name already exists
        existing = Series.query.filter(Series.name == name).first()
        if existing:
            flash('A series with this name already exists', 'danger')
            return render_template('create_series.html')
        
        new_series = Series(name=name, description=description)
        db.session.add(new_series)
        db.session.commit()
        
        flash(f'Series "{name}" created successfully', 'success')
        return redirect(url_for('manage_series'))
    
    return render_template('create_series.html')

@app.route('/series/edit/<int:series_id>', methods=['GET', 'POST'])
def edit_series(series_id):
    series = Series.query.get_or_404(series_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Series name is required', 'danger')
            return render_template('edit_series.html', series=series)
        
        # Check for name conflict only if name changed
        if name != series.name:
            existing = Series.query.filter(Series.name == name).first()
            if existing:
                flash('A series with this name already exists', 'danger')
                return render_template('edit_series.html', series=series)
        
        series.name = name
        series.description = description
        db.session.commit()
        
        flash(f'Series "{name}" updated successfully', 'success')
        return redirect(url_for('manage_series'))
    
    return render_template('edit_series.html', series=series)

@app.route('/series/delete/<int:series_id>', methods=['POST'])
def delete_series(series_id):
    if Series.query.count() <= 1:
        flash('Cannot delete the only series. Create another series first.', 'danger')
        return redirect(url_for('manage_series'))
    
    series = Series.query.get_or_404(series_id)
    
    # If we're deleting the current series, select another one
    if session.get('current_series_id') == series_id:
        another_series = Series.query.filter(Series.id != series_id).first()
        session['current_series_id'] = another_series.id
    
    db.session.delete(series)
    db.session.commit()
    
    flash(f'Series "{series.name}" deleted with all its data', 'success')
    return redirect(url_for('manage_series'))

@app.route('/')
def index():
    series_id = session.get('current_series_id')
    current_series = Series.query.get(series_id)
    
    players = Player.query.filter_by(series_id=series_id).order_by(Player.elo.desc()).all()
    
    # Calculate player stats
    player_stats = {}
    games = Game.query.filter_by(series_id=series_id).all()
    
    for player in players:
        player_stats[player.id] = {'wins': 0, 'losses': 0, 'win_pct': 0}
    
    # Calculate wins and losses
    for game in games:
        team1_ids = [int(pid) for pid in game.team1_players.split(',')]
        team2_ids = [int(pid) for pid in game.team2_players.split(',')]
        
        if game.winner == 1:
            for player_id in team1_ids:
                if player_id in player_stats:
                    player_stats[player_id]['wins'] += 1
            for player_id in team2_ids:
                if player_id in player_stats:
                    player_stats[player_id]['losses'] += 1
        
        elif game.winner == 2:
            for player_id in team1_ids:
                if player_id in player_stats:
                    player_stats[player_id]['losses'] += 1
            for player_id in team2_ids:
                if player_id in player_stats:
                    player_stats[player_id]['wins'] += 1
    
    # Calculate win percentages
    for player_id, stats in player_stats.items():
        total_games = stats['wins'] + stats['losses']
        if total_games > 0:
            stats['win_pct'] = (stats['wins'] / total_games) * 100
        else:
            stats['win_pct'] = 0
        stats['win_pct'] = round(stats['win_pct'], 1)
    
    # Get all series for dropdown
    all_series = Series.query.all()
    
    return render_template('leaderboard.html', 
                           players=players, 
                           player_stats=player_stats, 
                           current_series=current_series,
                           all_series=all_series)

@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    series_id = session.get('current_series_id')
    current_series = Series.query.get(series_id)
    
    if request.method == 'POST':
        # Get selected players for each team
        team1 = request.form.getlist('team1')
        team2 = request.form.getlist('team2')
        game_count = int(request.form.get('game_count', 1))
        
        # Validate
        if not team1 or not team2:
            flash('Please select players for both teams', 'danger')
            players = Player.query.filter_by(series_id=series_id).all()
            return render_template('new_game.html', players=players, current_series=current_series)
        
        # Process each game
        for i in range(1, game_count + 1):
            winner = int(request.form.get(f'winner_{i}'))
            
            # Get the next sequence number within this series
            last_game = Game.query.filter_by(series_id=series_id).order_by(Game.sequence.desc()).first()
            next_seq = 1 if not last_game else last_game.sequence + 1
            
            # Create and save game with series_id
            game = Game(
                team1_players=','.join(team1),
                team2_players=','.join(team2),
                winner=winner,
                sequence=next_seq,
                series_id=series_id
            )
            db.session.add(game)
            
            # Update ELOs
            update_elos(team1, team2, winner, series_id)
            
        db.session.commit()
        flash(f'Successfully saved {game_count} games!', 'success')
        return redirect(url_for('index'))
    
    players = Player.query.filter_by(series_id=series_id).all()
    all_series = Series.query.all()
    
    return render_template('new_game.html', 
                          players=players,
                          current_series=current_series,
                          all_series=all_series)

@app.route('/games')
def games():
    series_id = session.get('current_series_id')
    current_series = Series.query.get(series_id)
    
    games_list = Game.query.filter_by(series_id=series_id).order_by(Game.sequence.desc()).all()
    players = Player.query.filter_by(series_id=series_id).all()
    
    # Create a dict for quick lookup
    players_dict = {str(p.id): p.name for p in players}
    
    formatted_games = []
    for game in games_list:
        team1_names = [players_dict.get(pid, "Unknown") for pid in game.team1_players.split(',')]
        team2_names = [players_dict.get(pid, "Unknown") for pid in game.team2_players.split(',')]
        
        formatted_games.append({
            'id': game.id,
            'date': game.date.strftime('%Y-%m-%d %H:%M') if game.date else "Unknown",
            'team1': ', '.join(team1_names),
            'team2': ', '.join(team2_names),
            'winner': game.winner,
            'sequence': game.sequence
        })
    
    all_series = Series.query.all()
    
    return render_template('games.html', 
                          games=formatted_games,
                          current_series=current_series,
                          all_series=all_series)

@app.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    series_id = session.get('current_series_id')
    
    # Get the game and verify it belongs to the current series
    game = Game.query.filter_by(id=game_id, series_id=series_id).first_or_404()
    players = Player.query.filter_by(series_id=series_id).all()
    
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
        recalculate_all_elos(series_id)
        
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
    series_id = session.get('current_series_id')
    
    # Get the game and verify it belongs to the current series
    game = Game.query.filter_by(id=game_id, series_id=series_id).first_or_404()
    
    # Delete the game
    db.session.delete(game)
    db.session.commit()
    
    # Recalculate ELOs for all players in this series
    recalculate_all_elos(series_id)
    
    flash('Game deleted successfully!')
    return redirect(url_for('games'))

@app.route('/update_game_order', methods=['POST'])
def update_game_order():
    data = request.json
    game_ids = data.get('games', [])
    
    if not game_ids:
        return jsonify({'error': 'No game order provided'}), 400
    
    try:
        # Update sequences based on the new order
        for index, game_id in enumerate(game_ids):
            # Sequence numbers start from 1
            new_sequence = index + 1
            game = Game.query.get(game_id)
            if game:
                game.sequence = new_sequence
        
        db.session.commit()
        
        # Recalculate ELOs based on the new game order
        recalculate_all_elos(session.get('current_series_id'))
        
        return jsonify({'message': 'Game order updated successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def recalculate_all_elos(series_id):
    # Reset all player ELOs to their starting values
    players = Player.query.filter_by(series_id=series_id).all()
    for player in players:
        player.elo = player.starting_elo
    
    # Get all games in this series, ordered by sequence
    games = Game.query.filter_by(series_id=series_id).order_by(Game.sequence).all()
    
    # Replay all games to recalculate ELOs
    for game in games:
        team1_ids = [id for id in game.team1_players.split(',')]
        team2_ids = [id for id in game.team2_players.split(',')]
        update_elos(team1_ids, team2_ids, game.winner, series_id)
    
    db.session.commit()

def update_elos(team1_ids, team2_ids, winner, series_id):
    # Helper to fetch player by id and series
    def get_player(player_id):
        return Player.query.filter_by(id=player_id, series_id=series_id).first()
    
    # Get player objects
    team1 = [get_player(int(id)) for id in team1_ids]
    team2 = [get_player(int(id)) for id in team2_ids]
    
    # Calculate average ELOs
    team1_avg = sum(p.elo for p in team1) / len(team1)
    team2_avg = sum(p.elo for p in team2) / len(team2)
    
    # Calculate ELO changes
    base_change = 50
    exponent = 1.5
    if winner == 1:
        ratio = (team2_avg / team1_avg)**exponent
        team1_change = base_change * ratio
        team2_change = -base_change * ratio
    else:
        ratio = (team1_avg / team2_avg)**exponent
        team1_change = -base_change * ratio
        team2_change = base_change * ratio
    
    # Update ELOs
    for player in team1:
        player.elo += team1_change
    for player in team2:
        player.elo += team2_change

@app.route('/manage_players', methods=['GET', 'POST'])
def manage_players():
    series_id = session.get('current_series_id')
    current_series = Series.query.get(series_id)
    error_message = None
    success_message = None
    
    if request.method == 'POST':
        if 'add_player' in request.form:
            # Handle add player
            player_name = request.form.get('player_name')
            starting_elo = request.form.get('starting_elo', 1000)
            
            # Validate input
            if not player_name:
                error_message = "Player name is required"
            else:
                # Check if player with this name already exists in this series
                existing_player = Player.query.filter_by(
                    name=player_name, 
                    series_id=series_id
                ).first()
                
                if existing_player:
                    error_message = f"Player '{player_name}' already exists in this series"
                else:
                    # Create new player
                    try:
                        starting_elo = float(starting_elo)
                        new_player = Player(
                            name=player_name, 
                            elo=starting_elo, 
                            starting_elo=starting_elo,
                            series_id=series_id
                        )
                        db.session.add(new_player)
                        db.session.commit()
                        success_message = f"Player '{player_name}' added successfully"
                    except ValueError:
                        error_message = "ELO must be a valid number"
        
        elif 'remove_player' in request.form:
            # Handle remove player
            player_id = request.form.get('player_id')
            
            if player_id:
                player = Player.query.filter_by(id=player_id, series_id=series_id).first()
                if player:
                    # Check if player is in any games in this series
                    games = Game.query.filter_by(series_id=series_id).all()
                    player_in_game = False
                    
                    for game in games:
                        team1_ids = game.team1_players.split(',')
                        team2_ids = game.team2_players.split(',')
                        
                        if str(player.id) in team1_ids or str(player.id) in team2_ids:
                            player_in_game = True
                            break
                    
                    if player_in_game:
                        error_message = f"Cannot remove player '{player.name}' as they are part of existing games"
                    else:
                        player_name = player.name
                        db.session.delete(player)
                        db.session.commit()
                        success_message = f"Player '{player_name}' removed successfully"
                else:
                    error_message = "Player not found"
        
        elif 'edit_starting_elo' in request.form:
            # Handle edit starting ELO
            player_id = request.form.get('player_id')
            new_starting_elo = request.form.get('new_starting_elo')
            
            if player_id and new_starting_elo:
                player = Player.query.filter_by(id=player_id, series_id=series_id).first()
                if player:
                    try:
                        new_starting_elo = float(new_starting_elo)
                        player.starting_elo = new_starting_elo
                        
                        # Remember the old ELO for messaging
                        old_elo = player.elo
                        
                        # Recalculate ELOs to update current ELO values
                        db.session.commit()
                        recalculate_all_elos(series_id)
                        
                        success_message = f"Updated {player.name}'s starting ELO to {new_starting_elo}. Current ELO changed from {old_elo:.2f} to {player.elo:.2f}"
                    except ValueError:
                        error_message = "Starting ELO must be a valid number"
                else:
                    error_message = "Player not found"
    
    # Get all players in this series
    players = Player.query.filter_by(series_id=series_id).order_by(Player.name).all()
    
    # For each player, check if they're in any games in this series
    player_in_games = {}
    games = Game.query.filter_by(series_id=series_id).all()
    
    for player in players:
        player_in_games[player.id] = False
        for game in games:
            team1_ids = game.team1_players.split(',')
            team2_ids = game.team2_players.split(',')
            
            if str(player.id) in team1_ids or str(player.id) in team2_ids:
                player_in_games[player.id] = True
                break
    
    all_series = Series.query.all()
    
    return render_template('manage_players.html', 
                          players=players, 
                          player_in_games=player_in_games,
                          error_message=error_message,
                          success_message=success_message,
                          current_series=current_series,
                          all_series=all_series)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 