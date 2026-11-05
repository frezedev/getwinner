import random
from models import Member


class Raffle:
    pool: list[Member]
    history: list[Member]
    randomizer: random.Random


    def __init__(self, members: list[Member], **kwargs):
        

        self.pool = members
        self.history = []
        random.shuffle(self.pool)


    def next_winner(self) -> Member|None:
        if not self.pool:
            return None
        winner = self.pool.pop()
        self.history.append(winner)
        return winner

    
    def get_history(self) -> list[Member]:
        return self.history

    def remaining(self) -> int:
        return len(self.pool)