class Player:
    def __init__(self, name, stack, position):
        self.name = name
        self.stack = stack
        self.position = position  # "SB" or "BB"
        self.hand = []
        self.current_bet = 0
        self.history = []

    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.history = []

    def post_blind(self, amount):
        to_pay = min(amount, self.stack)
        self.stack -= to_pay
        self.current_bet += to_pay
        return to_pay
