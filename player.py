class player:
    def __init__(self, name):
        self.name = name
        self.elo = 1000  # Starting ELO of 1000

    def __str__(self):
        return f"{self.name}: {self.elo}" 