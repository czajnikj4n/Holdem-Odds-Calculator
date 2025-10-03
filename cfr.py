from collections import defaultdict
from gamelogic import GameLogic
from evaluator import HandEvaluator

class CFRTrainer:
    def __init__(self, game: GameLogic, evaluator: HandEvaluator, start_street="river", paths=None, street_map=None):
        self.game = game
        self.evaluator = evaluator
        self.start_street = start_street
        self.node_map = {}
        self.terminal_log = []  # store every terminal outcome
        self.paths = paths
        self.street_map = street_map or {}
        self.first_action_utils = defaultdict(lambda: {"total_util": 0.0, "count": 0})  # NEW

    def train(self, iterations=100):
        for _ in range(iterations):
            if self.paths:
                for path in self.paths:
                    self.cfr(self.game.clone_for_cfr(), path, 1.0, 1.0)
            else:
                self.cfr(self.game.clone_for_cfr(), [], 1.0, 1.0)
        return self.get_average_strategy(), self.first_action_utils  # RETURN BOTH

    def cfr(self, game, path, reach_p1, reach_p2, idx=0, first_action_recorded=False):
        # Terminal condition: either path ended or hand finished
        if idx >= len(path) or game.hand_finished:
            return self.resolve_utility(game)

        token = path[idx]
        player_str, action = token.split(":", 1)
        player_idx = 0 if player_str == "SB" else 1

        # Override street for token
        game.street = self.street_map.get(token, game.street)

        # Setup node
        node_key = f"{game.street}|{player_str}"
        if node_key not in self.node_map:
            self.node_map[node_key] = {"regret_sum": {}, "strategy_sum": {}, "actions": []}
            if self.paths:
                for p in self.paths:
                    for t in p[idx:]:
                        if t.startswith(player_str + ":"):
                            a = t.split(":", 1)[1]
                            self.node_map[node_key]["regret_sum"][a] = 0.0
                            self.node_map[node_key]["strategy_sum"][a] = 0.0
                            if a not in self.node_map[node_key]["actions"]:
                                self.node_map[node_key]["actions"].append(a)

        node = self.node_map[node_key]
        actions = node["actions"]
        strategy = self.get_strategy(node)
        util = {}
        node_util = 0.0

        for a in actions:
            # Clone the game to simulate this action
            evaluator = HandEvaluator()
            game_copy = game.clone_for_cfr(evaluator=evaluator)
            game_copy.street = game.street

            # --- Determine if this is a terminal call ---
            is_terminal_call = idx == len(path) - 1 and a.lower().startswith("call")

            # Apply action with terminal_call signal
            game_copy.apply_action(player_idx, a, terminal_call=is_terminal_call)

            # Immediate utility if terminal
            if game_copy.hand_finished:
                u = self.resolve_utility(game_copy)
            else:
                if player_idx == 0:
                    u = -self.cfr(game_copy, path, reach_p1 * strategy[a], reach_p2, idx + 1, first_action_recorded)
                else:
                    u = -self.cfr(game_copy, path, reach_p1, reach_p2 * strategy[a], idx + 1, first_action_recorded)

            util[a] = u
            node_util += strategy[a] * u

            # --- AGGREGATE FIRST MOVE UTILITY ---
            if not first_action_recorded:
                self.first_action_utils[a]["total_util"] += u
                self.first_action_utils[a]["count"] += 1

        # ---------------- UPDATE REGRETS ----------------
        for a in actions:
            regret = util[a] - node_util
            if player_idx == 0:
                node["regret_sum"][a] += reach_p2 * regret
            else:
                node["regret_sum"][a] += reach_p1 * regret
            node["strategy_sum"][a] += strategy[a]

        return node_util

    def resolve_utility(self, game: GameLogic):
        winners = game.evaluate_showdown(self.evaluator)
        split_pot = game.pot / len(winners)
        for w in winners:
            w.stack += split_pot
        util_p1 = game.players[0].stack - game.players[0].starting_stack
        util_p2 = game.players[1].stack - game.players[1].starting_stack
        self.terminal_log.append({
            "board": game.community_cards[:],
            "pot": game.pot,
            "winner": [w.name for w in winners],
            "utility": util_p1
        })
        return util_p1

    def get_strategy(self, node):
        regrets = node["regret_sum"]
        pos_regrets = {a: max(0, regrets[a]) for a in node["actions"]}
        total = sum(pos_regrets.values())
        if total > 0:
            return {a: pos_regrets[a] / total for a in node["actions"]}
        else:
            return {a: 1 / len(node["actions"]) for a in node["actions"]}

    def get_average_strategy(self):
        avg_strategy = {}
        for node_key, node in self.node_map.items():
            total = sum(node["strategy_sum"].values())
            if total > 0:
                avg_strategy[node_key] = {a: node["strategy_sum"][a] / total for a in node["actions"]}
            else:
                avg_strategy[node_key] = {a: 1 / len(node["actions"]) for a in node["actions"]}
        return avg_strategy
