# action_tree.py
from actions import ACTIONS

class ActionTreeTraverser:
    def __init__(self, max_bets=4):
        self.max_bets = max_bets
        self.paths = []

    def traverse(self, stage="preflop", player="SB", facing="start", history=None, bet_count=0):
        if history is None:
            history = []

        options = ACTIONS[stage][player][facing]

        for action in options:
            new_history = history + [f"{player}:{action}"]

            # --- FOLD ends immediately ---
            if action == "fold":
                self.paths.append(new_history + ["TERMINAL_FOLD"])
                continue

            # --- ALL-IN special handling ---
            if action == "allin":
                next_player = self._next_player(stage, player)
                # Opponent can fold
                self.paths.append(new_history + [f"{next_player}:fold", "TERMINAL_FOLD"])
                # Opponent calls -> run out remaining streets, then showdown
                runout = self._remaining_board(stage)
                self.paths.append(new_history + [f"{next_player}:call"] + runout + ["SHOWDOWN"])
                continue

            # --- RAISE cap enforcement ---
            if "raise" in action and bet_count + 1 >= self.max_bets:
                next_player = self._next_player(stage, player)
                # Opponent folds
                self.paths.append(new_history + [f"{next_player}:fold", "TERMINAL_FOLD"])
                # Opponent calls -> forced all-in → run out board
                runout = self._remaining_board(stage)
                self.paths.append(new_history + [f"{next_player}:call"] + runout + ["SHOWDOWN"])
                continue

            # --- Continue recursively ---
            next_stage, next_player, next_facing = self._next_state(stage, player, action)
            if next_stage == "showdown":
                self.paths.append(new_history + ["SHOWDOWN"])
            elif next_stage == "terminal":
                self.paths.append(new_history + ["TERMINAL"])
            else:
                self.traverse(next_stage, next_player, next_facing, new_history, bet_count + ("raise" in action))

    def _next_player(self, stage, player):
        if stage == "preflop":
            return "BB" if player == "SB" else "SB"
        else:
            return "second" if player == "first" else "first"

    def _next_state(self, stage, player, action):
        """
        Transition between betting rounds.
        """
        if stage == "preflop":
            if player == "SB":
                if action == "fold":
                    return "terminal", None, None
                return stage, "BB", "facing_call" if action == "call_0.5bb" else "facing_raise"
            elif player == "BB":
                if action in ["fold"]:
                    return "terminal", None, None
                # matched → flop
                return "flop", "first", "start"

        elif stage in ["flop", "turn", "river"]:
            if player == "first":
                if action == "check":
                    return stage, "second", "facing_check"
                else:
                    return stage, "second", "facing_bet"
            elif player == "second":
                if action in ["fold"]:
                    return "terminal", None, None
                # matched → advance street
                if stage == "flop":
                    return "turn", "first", "start"
                elif stage == "turn":
                    return "river", "first", "start"
                elif stage == "river":
                    return "showdown", None, None

        return "showdown", None, None

    def _remaining_board(self, stage):
        """
        Return the board runout given current stage.
        """
        if stage == "preflop":
            return ["FLOP", "TURN", "RIVER"]
        elif stage == "flop":
            return ["TURN", "RIVER"]
        elif stage == "turn":
            return ["RIVER"]
        else:  # river
            return []
    
    def count_paths(self):
        return len(self.paths)
