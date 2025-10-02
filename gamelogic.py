# gamelogic.py
from deck import Deck
from player import Player
from evaluator import HandEvaluator

class GameLogic:
    def __init__(self, sb_amount=1, bb_amount=2, stack_size=100):
        self.sb_amount = sb_amount
        self.bb_amount = bb_amount
        self.stack_size = stack_size
        self.reset()

    def reset(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.players = [
            Player("P1", self.stack_size, "SB"),
            Player("P2", self.stack_size, "BB"),
        ]
        self.pot = 0.0
        self.community_cards = []
        self.street = "preflop"
        self.action_history = []
        self.to_act = 0  # SB acts first
        self.street_complete = False
        self.hand_finished = False
        self.terminal_type = None  # "fold" or "showdown"
        self.winner_idx = None

        # blinds
        self.pot += self.players[0].post_blind(self.sb_amount)
        self.pot += self.players[1].post_blind(self.bb_amount)

        # deal hole cards
        for _ in range(2):
            for p in self.players:
                p.hand.append(self.deck.deal())

    def record_action(self, player_idx, action):
        self.action_history.append((self.street, self.players[player_idx].name, action))
        self.players[player_idx].history.append((self.street, action))

    def proceed_to_next_street(self):
        if self.street == "preflop":
            self.street = "flop"
            self.community_cards = [self.deck.deal() for _ in range(3)]
        elif self.street == "flop":
            self.street = "turn"
            self.community_cards.append(self.deck.deal())
        elif self.street == "turn":
            self.street = "river"
            self.community_cards.append(self.deck.deal())
        elif self.street == "river":
            self.street = "showdown"
        else:
            raise ValueError("Game already finished")
        self.street_complete = True
        for p in self.players:
            p.current_bet = 0

    def get_available_actions(self, player_idx):
        from actions import ACTIONS
        player = self.players[player_idx]
        if not self.action_history:
            facing = "start"
        else:
            last_street, last_player, last_action = self.action_history[-1]
            facing = "after_opponent" if last_player != player.name else "start"
        actions = ACTIONS[self.street][player.position][facing]
        filtered = []
        for a in actions:
            if player.stack <= 0 and a not in ("fold", "call", "check", "all-in"):
                continue
            filtered.append(a)
        return filtered

    def simulate_action(self, player_idx, action):
        new = GameLogic(self.sb_amount, self.bb_amount, self.stack_size)
        new.deck = self.deck
        new.players = [
            Player(self.players[0].name, self.players[0].stack, self.players[0].position),
            Player(self.players[1].name, self.players[1].stack, self.players[1].position)
        ]
        for i in [0, 1]:
            new.players[i].hand = list(self.players[i].hand)
            new.players[i].current_bet = self.players[i].current_bet
            new.players[i].history = list(self.players[i].history)
        new.pot = self.pot
        new.community_cards = list(self.community_cards)
        new.street = self.street
        new.action_history = list(self.action_history)
        new.to_act = self.to_act
        new.street_complete = self.street_complete
        new.hand_finished = self.hand_finished
        new.terminal_type = self.terminal_type
        new.winner_idx = self.winner_idx
        new.apply_action(player_idx, action)
        return new

    def apply_action(self, player_idx, action):
        if self.hand_finished:
            return
        player = self.players[player_idx]
        opponent = self.players[1 - player_idx]
        action = action.strip().lower()

        # --- FOLD ---
        if action.startswith("fold"):
            self.winner_idx = 1 - player_idx
            opponent.stack += self.pot
            self.pot = 0.0
            self.record_action(player_idx, action)
            self.hand_finished = True
            self.terminal_type = "fold"
            self.street = "showdown"
            return

        # --- BET/CALL/RAISE/ALL-IN ---
        bet_amount = self.compute_bet_amount(player_idx, action)
        if action.startswith("call") or action.startswith("check"):
            paid = min(bet_amount, player.stack)
            player.stack -= paid
            player.current_bet += paid
            self.pot += paid
        elif action.startswith("bet") or action.startswith("raise"):
            paid = min(bet_amount, player.stack)
            player.stack -= paid
            player.current_bet += paid
            self.pot += paid
        elif action == "all-in":
            paid = player.stack
            player.stack = 0.0
            player.current_bet += paid
            self.pot += paid

        self.record_action(player_idx, action)

        # --- Handle all-in runout ---
        if player.stack <= 0 or opponent.stack <= 0:
            while len(self.community_cards) < 5:
                try:
                    self.community_cards.append(self.deck.deal())
                except Exception:
                    break
            self.hand_finished = True
            self.terminal_type = "showdown"
            self.street = "showdown"
            return

        # --- Advance street if bets matched ---
        if self.players[0].current_bet == self.players[1].current_bet and not self.street_complete:
            self.proceed_to_next_street()
            if self.street == "showdown":
                self.hand_finished = True
                self.terminal_type = "showdown"

    def compute_bet_amount(self, player_idx, action: str):
        player = self.players[player_idx]
        opponent = self.players[1 - player_idx]
        tok = action.strip().lower()
        parts = tok.split()

        if "all-in" in tok:
            return player.stack
        if tok.startswith("check") or tok.startswith("fold"):
            return 0.0
        if tok.startswith("call"):
            needed = max(0.0, opponent.current_bet - player.current_bet)
            return min(needed, player.stack)
        if parts and parts[0] in ("bet", "raise") and len(parts) >= 2:
            size_token = parts[1]
            if self.street == "preflop":
                if size_token.endswith("x"):
                    mult = float(size_token[:-1])
                    base = opponent.current_bet if opponent.current_bet > 0 else self.bb_amount
                    target_total = mult * base
                    return min(max(0.0, target_total - player.current_bet), player.stack)
                else:
                    bb_mult = float(size_token)
                    target_total = bb_mult * self.bb_amount
                    return min(max(0.0, target_total - player.current_bet), player.stack)
            else:
                frac = float(size_token)
                if parts[0] == "bet" and opponent.current_bet == 0:
                    return min(frac * max(1.0, self.pot), player.stack)
                else:
                    raise_to = opponent.current_bet + frac * max(1.0, self.pot)
                    return min(max(0.0, raise_to - player.current_bet), player.stack)
        return 0.0

    def is_terminal(self):
        return self.hand_finished or self.street == "showdown"

    def get_utility(self, player_idx):
        if self.terminal_type == "fold":
            return self.pot if player_idx == self.winner_idx else -self.pot
        elif self.terminal_type == "showdown":
            scores = [p.hand_score for p in self.players]
            max_score = max(scores)
            winners = [i for i, s in enumerate(scores) if s == max_score]
            if player_idx in winners:
                return self.pot / len(winners)
            else:
                return -self.pot
        return 0.0

    def evaluate_showdown(self, evaluator: HandEvaluator):
        for p in self.players:
            p.evaluate_hand(self.community_cards, evaluator)
        scores = [p.hand_score for p in self.players]
        max_score = max(scores)
        winners = [p for p, s in zip(self.players, scores) if s == max_score]
        return winners
