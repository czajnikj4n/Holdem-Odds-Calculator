from card import Card
import random

class Deck:
    def __init__(self):
        self.initialize()

    def initialize(self):
        self.cards = []
        self.used = []
        values = [str(i) for i in range(2, 11)] + ["j", "q", "k", "a"]
        for suit in ["s", "h", "d", "c"]:
            for value in values:
                self.cards.append(Card(suit, value))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            raise ValueError("No cards left to deal")
        card = self.cards.pop()
        self.used.append(card)
        return card
