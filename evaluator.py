# evaluator.py
from itertools import combinations
from collections import Counter

class HandEvaluator:
    HAND_RANKS = {
        "High Card": 0,
        "One Pair": 20000,
        "Two Pair": 30000,
        "Three of a Kind": 40000,
        "Straight": 50000,
        "Flush": 60000,
        "Full House": 70000,
        "Four of a Kind": 80000,
        "Straight Flush": 90000,
        "Royal Flush": 100000
    }

    FACE_VALUES = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
        "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 11, "Q": 12, "K": 13, "A": 14
    }

    def card_value(self, card):
        """Convert 'Value of Suit' string to integer value."""
        value = card.split(" ")[0]
        return self.FACE_VALUES[value.upper()]

    def get_suit(self, card):
        """Extract suit from card string."""
        return card.split(" ")[-1].lower()

    def evaluate_hand(self, hand):
        """
        Returns a numeric score for a 5-card hand.
        Follows the same weighting as Java code, including kickers.
        """
        values = sorted([self.card_value(c) for c in hand], reverse=True)
        suits = [self.get_suit(c) for c in hand]
        rank_count = Counter(values)

        is_flush = len(set(suits)) == 1
        is_straight, top_straight = self.is_straight(values)

        score = 0
        # Royal Flush / Straight Flush
        if is_flush and is_straight and top_straight == 14:
            score = self.HAND_RANKS["Royal Flush"]
        elif is_flush and is_straight:
            score = self.HAND_RANKS["Straight Flush"] + top_straight
        # Four of a Kind
        elif 4 in rank_count.values():
            quad = self.get_highest_of_a_kind(rank_count, 4)
            kicker = self.get_kickers(rank_count, values, 1)
            score = self.HAND_RANKS["Four of a Kind"] + quad * 100 + kicker
        # Full House
        elif 3 in rank_count.values() and 2 in rank_count.values():
            trip = self.get_highest_of_a_kind(rank_count, 3)
            pair = self.get_highest_of_a_kind(rank_count, 2)
            score = self.HAND_RANKS["Full House"] + trip * 10 + pair
        # Flush
        elif is_flush:
            score = self.HAND_RANKS["Flush"] + self.flush_score(values)
        # Straight
        elif is_straight:
            score = self.HAND_RANKS["Straight"] + top_straight
        # Three of a Kind
        elif 3 in rank_count.values():
            trip = self.get_highest_of_a_kind(rank_count, 3)
            kicker = self.get_kickers(rank_count, values, 2)
            score = self.HAND_RANKS["Three of a Kind"] + trip * 100 + kicker
        # Two Pair
        elif list(rank_count.values()).count(2) == 2:
            pairs = self.get_top_pairs(rank_count)
            kicker = self.get_kickers(rank_count, values, 1)
            score = self.HAND_RANKS["Two Pair"] + pairs[0] * 100 + pairs[1] * 10 + kicker
        # One Pair
        elif 2 in rank_count.values():
            pair = self.get_highest_of_a_kind(rank_count, 2)
            kicker = self.get_kickers(rank_count, values, 3)
            score = self.HAND_RANKS["One Pair"] + pair * 100 + kicker
        # High Card
        else:
            score = self.HAND_RANKS["High Card"] + values[0]

        return score

    def find_best_five_card_hand(self, all_cards):
        """
        Given 5-7 cards, finds the best 5-card hand and returns (best_hand, score)
        """
        best_score = 0
        best_hand = []
        for combo in combinations(all_cards, 5):
            score = self.evaluate_hand(combo)
            if score > best_score:
                best_score = score
                best_hand = combo
        return list(best_hand), best_score

    # ----------- Utility Methods -----------

    def is_straight(self, values):
        """Returns (is_straight: bool, high_card: int)"""
        v = sorted(set(values))
        # Ace-low straight
        if set([14, 2, 3, 4, 5]).issubset(v):
            return True, 5
        # Normal straight
        for i in range(len(v) - 4):
            if v[i+4] - v[i] == 4:
                return True, v[i+4]
        return False, 0

    def get_highest_of_a_kind(self, rank_count, n):
        """Return the highest card value appearing exactly n times"""
        candidates = [val for val, count in rank_count.items() if count == n]
        return max(candidates)

    def get_top_pairs(self, rank_count):
        """Return two highest pairs"""
        pairs = sorted([val for val, count in rank_count.items() if count == 2], reverse=True)
        return pairs[:2]

    def get_kickers(self, rank_count, values, num_needed):
        """Return numeric kicker score for the top `num_needed` kickers"""
        kickers = [v for v in values if rank_count[v] == 1]
        score = 0
        multiplier = 10
        for i in range(min(num_needed, len(kickers))):
            score += kickers[i] * multiplier
            multiplier //= 10
        return score

    def flush_score(self, values):
        """Weighted flush score"""
        multipliers = [100, 50, 20, 10, 5]
        return sum(v * m for v, m in zip(values, multipliers))
