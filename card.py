class Card:
    suit_names = {
        "s": "spades",
        "h": "hearts",
        "d": "diamonds",
        "c": "clubs",
    }
    value_names = {
        "j": "jack",
        "q": "queen",
        "k": "king",
        "a": "ace",
    }
    value_map = {str(i): i for i in range(2, 11)}
    value_map.update({"j": 11, "q": 12, "k": 13, "a": 14})

    def __init__(self, suit, value):
        self.suit = suit  # "s","h","d","c"
        self.value = value  # "2"-"10","j","q","k","a"

    def __str__(self):
        value_str = self.value_names.get(self.value, self.value)
        suit_str = self.suit_names[self.suit]
        return f"{value_str} of {suit_str}"

    def rank(self):
        return self.value_map[self.value]
