class game:
    def __init__(self):
        self.team1 = []
        self.team2 = []
        self.team1elo = 0
        self.team2elo = 0
        self.winner = None  # 1 for team1, 2 for team2

    def set_teams(self, team1, team2):
        """Set the teams for the game"""
        self.team1 = team1
        self.team2 = team2
        self.team1elo = sum(player.elo for player in team1) / len(team1)
        self.team2elo = sum(player.elo for player in team2) / len(team2)

    def set_winner(self, winning_team):
        """Set the winner (1 for team1, 2 for team2)"""
        self.winner = winning_team

    def update_elos(self):
        """Update ELO ratings based on the game result"""
        if self.winner is None:
            return

        base_elo_change = 50
        elo_multiplier = 1.5
        if self.winner == 1:
            # Team 1 won
            ratio = (self.team2elo / self.team1elo)**elo_multiplier
            team1_change = base_elo_change * ratio
            team2_change = -base_elo_change * ratio
        else:
            # Team 2 won
            ratio = (self.team1elo / self.team2elo)**elo_multiplier
            team1_change = -base_elo_change * ratio
            team2_change = base_elo_change * ratio

        # Update each player's ELO
        for player in self.team1:
            player.elo += team1_change
        for player in self.team2:
            player.elo += team2_change 

    def print_player_elo(self):
        print("\nTeam 1 scores: ")
        for player in self.team1:
            print(f"{player.name}: {player.elo}")

        print("\nTeam 2 scores: ")
        for player in self.team2:
            print(f"{player.name}: {player.elo}")