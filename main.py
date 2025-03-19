# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from player import player
import random
from game import game

# Create 8 players
# players = [player(f"Player{i+1}") for i in range(8)]

names = ["Lukas", "Cade", "Alex", "Marshall", "Arvin" ,"Taylor", "Jenessa", "Keagan"]
elos = []

# namesDict = list(zip(names, elos))

players = [player(names[i]) for i in range(len(names))]
for p in players:
    if p.name == "Keagan":
        p.elo = 750


# Randomly split players into two teams
team1 = [p for p in players if p.name in ["Lukas", "Alex", "Taylor"]]
team2 = [p for p in players if p not in team1]

# Create a new game
game1 = game()

for i in range(3):
    # Set the teams
    game1.set_teams(team1, team2)
    # Set the winner (1 for team1, 2 for team2)
    game1.set_winner(1)  # Assuming team1 won
    # Update ELOs
    game1.update_elos()


team1 = [p for p in players if p.name in ["Lukas", "Marshall", "Taylor", "Jenessa"]]
team2 = [p for p in players if p not in team1]

game2 = game()

game2.set_teams(team1, team2)
game2.set_winner(1)
game2.update_elos()

game2.set_teams(team1, team2)
game2.set_winner(2)
game2.update_elos()

game2.set_teams(team1, team2)
game2.set_winner(1)
game2.update_elos()

game2.set_teams(team1, team2)
game2.set_winner(2)
game2.update_elos()

game2.set_teams(team1, team2)
game2.set_winner(1)
game2.update_elos()

game3 = game()

team1 = [p for p in players if p.name in ["Alex", "Marshall", "Taylor", "Arvin"]]
team2 = [p for p in players if p not in team1]

game3.set_teams(team1, team2)
game3.set_winner(2)
game3.update_elos()

game3.set_teams(team1, team2)
game3.set_winner(1)
game3.update_elos()

game3.set_teams(team1, team2)
game3.set_winner(2)
game3.update_elos()

game4 = game()

team1 = [p for p in players if p.name in ["Alex", "Lukas", "Jenessa", "Keagan"]]
team2 = [p for p in players if p not in team1]

game4.set_teams(team1, team2)
game4.set_winner(2)
game4.update_elos()

game4.set_teams(team1, team2)
game4.set_winner(1)
game4.update_elos()

game4.set_teams(team1, team2)
game4.set_winner(2)
game4.update_elos()

# print(game4.team2elo)
# print(game4.team1elo)

# game4.print_player_elo()

# Sort and print all players by ELO
print("\nAll players sorted by ELO:\n")
sorted_elo = sorted(players, key=lambda x: x.elo, reverse=True)
for elo in sorted_elo:
    print(elo)
print("\n")