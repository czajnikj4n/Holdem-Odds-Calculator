# player.py
class Player:
    def __init__(self, name, stack, position):
        self.name = name
        self.stack = stack
        self.position = position  # "SB" or "BB"
        self.hand = []           # Hole cards
        self.current_bet = 0
        self.history = []
        self.best_hand = []      # Best 5-card hand after evaluation
        self.hand_score = 0      # Numeric score from evaluator

    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.history = []
        self.best_hand = []
        self.hand_score = 0

    def post_blind(self, amount):
        to_pay = min(amount, self.stack)
        self.stack -= to_pay
        self.current_bet += to_pay
        return to_pay

    # ✅ Evaluate current hand given community cards
    def evaluate_hand(self, community_cards, evaluator):
        if len(self.hand) == 0:
            raise ValueError("No hole cards to evaluate")
        all_cards = self.hand + community_cards
        self.best_hand, self.hand_score = evaluator.find_best_five_card_hand(all_cards)
        return self.best_hand, self.hand_score
