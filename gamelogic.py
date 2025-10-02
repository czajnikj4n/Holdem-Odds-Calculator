# holdembot.py (or gamelogic.py)
from deck import Deck
from player import Player

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
        self.pot = 0
        self.community_cards = []
        self.street = "preflop"
        self.action_history = []
        self.to_act = 0  # SB acts first preflop in heads-up

        # blinds
        self.pot += self.players[0].post_blind(self.sb_amount)
        self.pot += self.players[1].post_blind(self.bb_amount)

        # deal hole cards
        for _ in range(2):
            for player in self.players:
                player.hand.append(self.deck.deal())

    def proceed_to_next_street(self):
        # bets must be equal to continue
        if self.players[0].current_bet != self.players[1].current_bet:
            raise ValueError("Bets are not matched yet")

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

    def record_action(self, player_idx, action):
        self.action_history.append((self.street, self.players[player_idx].name, action))
        self.players[player_idx].history.append((self.street, action))
        # Here you’ll later integrate chip accounting (bet/raise/fold/call)
