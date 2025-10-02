# deck.py
from card import Card
import random

class Deck:
    def __init__(self):
        self.cards = []
        self.used = []
        self.initialize()

    def initialize(self):
        self.cards = []
        self.used = []
        values = [str(i) for i in range(2, 11)] + ["J", "Q", "K", "A"]
        suits = ["s", "h", "d", "c"]
        for suit in suits:
            for value in values:
                self.cards.append(Card(suit, value))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            raise ValueError("No more cards in the deck")
        card_obj = self.cards.pop(0)
        self.used.append(card_obj)
        return str(card_obj)  # <-- convert to string here
