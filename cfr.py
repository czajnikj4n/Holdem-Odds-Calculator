# cfr.py
import random
from typing import List, Dict, Tuple
from deck import Deck
from evaluator import HandEvaluator
from player import Player
from actions import ACTIONS

# Monte Carlo samples at showdown (you asked for 30)
MC_SAMPLES_DEFAULT = 30
MAX_RAISES_PER_STREET_DEFAULT = 4


class CFRNode:
    """
    Lightweight node used by CFR. Keeps only the minimal state needed:
      - hole cards (strings), community cards (strings)
      - stacks, current bets, pot
      - street ("preflop","flop","turn","river","showdown")
      - to_act: 0 (SB) or 1 (BB)
      - history: list of tuples (street, actor_idx, action_str)
      - raise_count: number of raises that happened on current street
    """
    def __init__(
        self,
        sb_hand: List[str],
        bb_hand: List[str],
        community_cards: List[str],
        stacks: List[float],
        current_bets: List[float],
        pot: float,
        street: str,
        to_act: int,
        history: List[Tuple[str, int, str]],
        raise_count: int = 0,
        max_raises_per_street: int = MAX_RAISES_PER_STREET_DEFAULT,
        bb_amount: float | None = None
    ):
        self.sb_hand = list(sb_hand)
        self.bb_hand = list(bb_hand)
        self.community_cards = list(community_cards)
        self.stacks = list(stacks)
        self.current_bets = list(current_bets)
        self.pot = pot
        self.street = street
        self.to_act = to_act  # 0 -> SB, 1 -> BB
        # history entries: (street, actor_idx, action_string)
        self.history = list(history)
        self.raise_count = raise_count
        self.max_raises_per_street = max_raises_per_street
        # optional: used to interpret "raise X" multipliers in preflop (bb units)
        # If not supplied, we'll derive a reasonable bb_amount from current_bets.
        self.bb_amount = bb_amount

    # -----------------
    # Helpers
    # -----------------
    def _position(self, actor_idx: int) -> str:
        return "SB" if actor_idx == 0 else "BB"

    def _facing_key(self) -> str:
        """Return 'start' or 'after_opponent' for ACTIONS lookups."""
        if not self.history:
            return "start"
        last_street, last_actor, last_action = self.history[-1]
        # If the last action was made by the same player who would act next,
        # that means it's that player's turn to act first (rare), treat as 'start'.
        return "after_opponent" if last_actor != self.to_act else "start"

    def get_legal_actions(self) -> List[str]:
        """Return legal ACTIONS from actions.py filtered for raise cap and stack constraints."""
        pos = self._position(self.to_act)
        facing = self._facing_key()
        # Defensive: if ACTIONS doesn't have key, return conservative list
        try:
            actions = list(ACTIONS[self.street][pos][facing])
        except KeyError:
            # fallback
            actions = ["fold", "call", "check", "all-in"]

        # If raise cap reached, remove raises/bets
        if self.raise_count >= self.max_raises_per_street:
            actions = [a for a in actions if not (a.startswith("raise") or a.startswith("bet"))]

        # Remove actions impossible because of stack sizes (e.g., bet fractions larger than stack)
        filtered = []
        for a in actions:
            amt = self._compute_bet_amount(a)
            # allow actions that require 0 chips (check/call with 0)
            if a.startswith("call") or a.startswith("check") or a.startswith("fold"):
                filtered.append(a)
            else:
                # if player stack insufficient, keep 'all-in' only; otherwise keep action
                if amt <= self.stacks[self.to_act] and self.stacks[self.to_act] > 0:
                    filtered.append(a)
                else:
                    # if action would exceed stack, offer all-in as alternative (but don't auto-insert)
                    # keep only all-in if present; otherwise skip
                    if a == "all-in":
                        filtered.append(a)
        return filtered

    def _infer_bb_amount(self) -> float:
        """Try to infer big-blind size from current bets if bb_amount not supplied."""
        if self.bb_amount is not None:
            return self.bb_amount
        # If current_bets show big blind (common test start [0.5,1]), use max(current_bets)
        bb = max(max(self.current_bets), 1.0)
        # avoid zero
        return bb if bb > 0 else 1.0

    def _compute_bet_amount(self, action: str) -> float:
        """
        Mimic GameLogic.compute_bet_amount semantics.
        Works for:
          - 'call' / 'call X' (returns difference opponent-current)
          - 'raise X' where X may be "1.5" or "2x"
          - 'bet X' (postflop fractional pot)
          - 'all-in'
        """
        player_idx = self.to_act
        opp = 1 - player_idx
        player_curr = self.current_bets[player_idx]
        opp_curr = self.current_bets[opp]

        # Normalize action words: sometimes "call 0.5" or plain "call"
        if action.startswith("call"):
            return max(0.0, opp_curr - player_curr)

        if action == "check":
            return 0.0

        if action == "all-in":
            return float(self.stacks[player_idx])

        # Preflop semantics: treat raise X as X * bb_amount (unless 'x' multiplier)
        if self.street == "preflop":
            if action.startswith("raise"):
                parts = action.split()
                if len(parts) >= 2:
                    amt_str = parts[1]
                    if amt_str.endswith("x"):
                        # multiplier of opponent current bet (e.g. "2x")
                        try:
                            mul = float(amt_str[:-1])
                            target = mul * max(opp_curr, self._infer_bb_amount())
                            return max(0.0, target - player_curr)
                        except Exception:
                            return 0.0
                    else:
                        try:
                            bb_mult = float(amt_str)
                            bb_amount = self._infer_bb_amount()
                            target = bb_mult * bb_amount
                            return max(0.0, target - player_curr)
                        except Exception:
                            return 0.0
        # Postflop: 'bet fraction' or 'raise fraction' -> fraction * pot
        if action.startswith("bet") or action.startswith("raise"):
            parts = action.split()
            if len(parts) >= 2:
                try:
                    fraction = float(parts[1])
                    return min(self.stacks[player_idx], fraction * self.pot)
                except Exception:
                    # fallback: treat as 0
                    return 0.0

        # fallback 0
        return 0.0

    # -----------------
    # Core: apply action -> new node
    # -----------------
    def apply_action(self, action: str) -> "CFRNode":
        """
        Apply `action` to this node and return a new CFRNode (manual copy, no deepcopy).
        We will:
          - parse amount with _compute_bet_amount
          - update stacks/current_bets/pot
          - update raise_count (if raise/bet occurred)
          - append history (street, actor_idx, action)
          - advance street when bets are matched (and deal real cards using Deck)
        """
        # shallow copies of lists (manual copy)
        sb_hand = list(self.sb_hand)
        bb_hand = list(self.bb_hand)
        community = list(self.community_cards)
        stacks = list(self.stacks)
        current_bets = list(self.current_bets)
        pot = float(self.pot)
        street = self.street
        to_act = self.to_act
        history = list(self.history)
        raise_count = int(self.raise_count)

        actor = to_act
        opp = 1 - actor

        # parse action amount
        amount = self._compute_bet_amount(action)

        # apply action effects
        if action.startswith("fold"):
            # Represent fold by setting current_bets[actor] = -1 (marker)
            current_bets[actor] = -1
            history.append((street, actor, action))
            # Terminal node (fold) — we still return node; terminal detection elsewhere
            # pot and stacks remain as-is (we assume amounts already posted are in pot)
            new_node = CFRNode(
                sb_hand, bb_hand, community, stacks, current_bets, pot, street, actor, history,
                raise_count=raise_count, max_raises_per_street=self.max_raises_per_street,
                bb_amount=self.bb_amount
            )
            return new_node

        if action == "check":
            # no chips moved; just record and maybe advance if last action was opponent check/call
            history.append((street, actor, action))
        elif action.startswith("call"):
            # move chips from stack to match opponent's bet
            amt = min(amount, stacks[actor])
            stacks[actor] -= amt
            current_bets[actor] += amt
            pot += amt
            history.append((street, actor, action))
        elif action.startswith("raise") or action.startswith("bet"):
            amt = min(amount, stacks[actor])
            stacks[actor] -= amt
            current_bets[actor] += amt
            pot += amt
            raise_count += 1
            history.append((street, actor, action))
        elif action == "all-in":
            amt = stacks[actor]
            stacks[actor] = 0.0
            current_bets[actor] += amt
            pot += amt
            # all-in counts as a raise for raise cap purposes
            raise_count += 1
            history.append((street, actor, action))
        else:
            # unknown action: treat as check
            history.append((street, actor, action))

        # Determine whether betting round has closed:
        # Betting round considered closed when both active players have equal non-negative current_bet
        def bets_matched(cb):
            # if a player folded (cb < 0), not matched
            if any(x < 0 for x in cb):
                return True  # terminal fold handled elsewhere
            return abs(cb[0] - cb[1]) < 1e-9

        # Advance to next street and deal real cards using Deck if appropriate
        # We will only advance if bets matched and last action was a call/check that closed the round
        advanced = False
        if bets_matched(current_bets):
            # reset current bets for next street (move chips already to pot)
            current_bets = [0.0, 0.0]
            # Advance street in order
            if street == "preflop":
                street = "flop"
                # deal 3 community cards from a deck excluding known cards
                deck = Deck()
                # remove known: hole cards + any already in community
                known = set(sb_hand + bb_hand + community)
                # deck.cards contains Card objects; Deck.deal() returns string(str(card))
                # We recreate deck.cards so that deal() will return distinct strings
                deck.cards = [c for c in deck.cards if str(c) not in known]
                deck.shuffle()
                # draw 3
                for _ in range(3):
                    community.append(str(deck.deal()))
                # reset raise_count for new street
                raise_count = 0
            elif street == "flop":
                street = "turn"
                deck = Deck()
                known = set(sb_hand + bb_hand + community)
                deck.cards = [c for c in deck.cards if str(c) not in known]
                deck.shuffle()
                community.append(str(deck.deal()))
                raise_count = 0
            elif street == "turn":
                street = "river"
                deck = Deck()
                known = set(sb_hand + bb_hand + community)
                deck.cards = [c for c in deck.cards if str(c) not in known]
                deck.shuffle()
                community.append(str(deck.deal()))
                raise_count = 0
            elif street == "river":
                street = "showdown"
                raise_count = 0
            advanced = True

        # Next to act normally alternates, but if we advanced street, per heads-up rules BB acts first on postflop.
        if advanced:
            # per your rules earlier: BB acts first on flop/turn/river
            next_to_act = 1  # BB
        else:
            next_to_act = opp

        new_node = CFRNode(
            sb_hand, bb_hand, community, stacks, current_bets, pot, street, next_to_act, history,
            raise_count=raise_count, max_raises_per_street=self.max_raises_per_street,
            bb_amount=self.bb_amount
        )
        return new_node

    # -----------------
    # Terminal & utility
    # -----------------
    def is_terminal(self) -> bool:
        # fold marker: any current_bets < 0
        if any(cb < 0 for cb in self.current_bets):
            return True
        if self.street == "showdown":
            return True
        # If someone has 0 stack and other called -> showdown (we handle all-ins by runout MC)
        return False

    def utility_for_player0(self, mc_samples: int = MC_SAMPLES_DEFAULT) -> float:
        """
        Returns utility (EV) for player 0 (SB) at this terminal state.
        If fold terminal, return +/- pot.
        If showdown: Monte Carlo additional runouts if community cards incomplete.
        """
        # Fold detection
        if any(cb < 0 for cb in self.current_bets):
            # which player folded?
            folded_idx = 0 if self.current_bets[0] < 0 else 1
            winner = 1 - folded_idx
            return self.pot if winner == 0 else -self.pot

        # Showdown / all-in resolved -> we need to compute expected value of pot for SB
        evaluator = HandEvaluator()
        utility_acc = 0.0

        # For Monte Carlo runs we use Deck, remove known cards (hole + any community)
        for _ in range(mc_samples):
            deck = Deck()
            # remove known cards
            known = set(self.sb_hand + self.bb_hand + self.community_cards)
            deck.cards = [c for c in deck.cards if str(c) not in known]
            deck.shuffle()

            # fill missing community cards
            board = list(self.community_cards)
            while len(board) < 5:
                board.append(str(deck.deal()))

            # evaluate both players
            sb_player = Player("P1", self.stacks[0], "SB")
            bb_player = Player("P2", self.stacks[1], "BB")
            sb_player.hand = list(self.sb_hand)
            bb_player.hand = list(self.bb_hand)
            sb_player.evaluate_hand(board, evaluator)
            bb_player.evaluate_hand(board, evaluator)
            s0, s1 = sb_player.hand_score, bb_player.hand_score
            if s0 > s1:
                utility_acc += self.pot
            elif s0 < s1:
                utility_acc -= self.pot
            else:
                # split pot
                utility_acc += 0.0  # zero-sum: tie gives zero utility to player0 if we consider pot distributed equally
                # but to be consistent, assign half pot to player 0, half negative? We'll treat tie as zero overall
                # alternative would be utility_acc += (self.pot/2) - (self.pot/2) == 0
        return utility_acc / mc_samples


# ---------------------------
# CFR Trainer
# ---------------------------
class CFRTrainer:
    def __init__(self, mc_samples: int = MC_SAMPLES_DEFAULT):
        # info_sets: key -> {'regret_sum': {a:0}, 'strategy_sum': {a:0}}
        self.info_sets: Dict[str, Dict] = {}
        self.mc_samples = mc_samples

    def get_info_set_key(self, node: CFRNode) -> str:
        """
        Key: holecards of the acting player + street + public history
        history entries are (street, actor_idx, action)
        """
        acting_hand = node.sb_hand if node.to_act == 0 else node.bb_hand
        hole = "|".join(acting_hand)
        hist = "|".join([f"{s}:{i}:{a}" for s, i, a in node.history])
        return f"{hole}|{node.street}|{hist}"

    def _regret_matching(self, regret_sum: Dict[str, float]) -> Dict[str, float]:
        positive = {a: max(r, 0.0) for a, r in regret_sum.items()}
        total = sum(positive.values())
        if total > 0:
            return {a: (positive[a] / total) for a in regret_sum}
        else:
            n = len(regret_sum)
            return {a: 1.0 / n for a in regret_sum}

    def run_iteration(self, node: CFRNode, pi: float = 1.0, pi_opponent: float = 1.0) -> float:
        """
        Recursively traverse the game tree, update regrets.
        pi: product of strategy probs for player who will act at nodes where that same player acts (reach prob of node.to_act)
        pi_opponent: product of strategy probs for the opponent (counterfactual reach prob)
        Values returned are from perspective of player0 (SB).
        """

        # Terminal
        if node.is_terminal():
            return node.utility_for_player0(mc_samples=self.mc_samples)

        acting_player = node.to_act  # 0 or 1
        info_key = self.get_info_set_key(node)

        # Get legal actions for this node
        legal_actions = node.get_legal_actions()
        if not legal_actions:
            # fallback
            legal_actions = ["fold", "call", "all-in"]

        # Ensure info set exists
        if info_key not in self.info_sets:
            self.info_sets[info_key] = {
                'regret_sum': {a: 0.0 for a in legal_actions},
                'strategy_sum': {a: 0.0 for a in legal_actions}
            }
        # Ensure actions in info set match legal actions (if new actions appear, expand)
        for a in legal_actions:
            if a not in self.info_sets[info_key]['regret_sum']:
                self.info_sets[info_key]['regret_sum'][a] = 0.0
                self.info_sets[info_key]['strategy_sum'][a] = 0.0

        regret_sum = self.info_sets[info_key]['regret_sum']
        strategy_sum = self.info_sets[info_key]['strategy_sum']

        # Current strategy at this info set
        strategy = self._regret_matching(regret_sum)

        # Accumulate strategy sum (for average strategy later)
        # Note: multiply by reach probability of player who is acting
        for a, prob in strategy.items():
            strategy_sum[a] += (pi * prob) if acting_player == 0 else (pi_opponent * prob)

        # Traverse children
        action_values: Dict[str, float] = {}
        node_value = 0.0

        for a in legal_actions:
            next_node = node.apply_action(a)

            # If acting_player is 0 (SB), multiply pi for chosen action; opponent prob remains same
            if acting_player == 0:
                v = self.run_iteration(next_node, pi * strategy[a], pi_opponent)
            else:
                # acting_player == 1 (BB)
                v = self.run_iteration(next_node, pi, pi_opponent * strategy[a])

            action_values[a] = v
            node_value += strategy[a] * v

        # Update regrets for this info set
        # For player i (acting_player), regret update uses opponent reach prob
        for a in legal_actions:
            regret = action_values[a] - node_value
            if acting_player == 0:
                self.info_sets[info_key]['regret_sum'][a] += pi_opponent * regret
            else:
                self.info_sets[info_key]['regret_sum'][a] += pi * regret

        return node_value

    def get_average_strategy(self) -> Dict[str, Dict[str, float]]:
        avg = {}
        for key, data in self.info_sets.items():
            total = sum(data['strategy_sum'].values())
            if total > 0:
                avg[key] = {a: s / total for a, s in data['strategy_sum'].items()}
            else:
                n = len(data['strategy_sum'])
                avg[key] = {a: 1.0 / n for a in data['strategy_sum']}
        return avg
