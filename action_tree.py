# action_tree.py
from actions import ACTIONS

class ActionTreeTraverser:
    def __init__(self, max_bets=4):
        self.max_bets = max_bets
        self.paths = []

    def traverse(self, stage="preflop", player="SB", facing="start", history=None, bet_count=0):
        if history is None:
            history = []

        # Defensive: ensure keys exist
        try:
            options = ACTIONS[stage][player][facing]
        except KeyError:
            raise KeyError(f"ACTIONS missing key for stage={stage}, player={player}, facing={facing}")

        for action in options:
            new_history = history + [f"{player}:{action}"]

            # FOLD ends immediately
            if action == "fold":
                self.paths.append(new_history + ["TERMINAL_FOLD"])
                continue

            # ALL-IN special handling: opponent can fold or call -> if call, run out remaining streets
            if action == "all-in":
                opp = self._next_player(player)
                # Opp folds
                self.paths.append(new_history + [f"{opp}:fold", "TERMINAL_FOLD"])
                # Opp calls -> runout board then showdown
                runout = self._remaining_board(stage)
                self.paths.append(new_history + [f"{opp}:call"] + runout + ["SHOWDOWN"])
                continue

            # Raise cap enforcement: if next raise would exceed cap, treat as all-in endpoint
            is_raise = action.startswith("raise") or action.startswith("bet")
            if is_raise and bet_count + 1 >= self.max_bets:
                opp = self._next_player(player)
                # Opp folds
                self.paths.append(new_history + [f"{opp}:fold", "TERMINAL_FOLD"])
                # Opp calls -> runout board then showdown (force all-in)
                runout = self._remaining_board(stage)
                self.paths.append(new_history + [f"{opp}:call"] + runout + ["SHOWDOWN"])
                continue

            # Normal continuation
            next_stage, next_player, next_facing = self._next_state(stage, player, action, facing)
            if next_stage == "showdown":
                self.paths.append(new_history + ["SHOWDOWN"])
            elif next_stage == "terminal":
                self.paths.append(new_history + ["TERMINAL"])
            else:
                self.traverse(
                    next_stage,
                    next_player,
                    next_facing,
                    new_history,
                    bet_count + (1 if is_raise else 0),
                )

    def _next_player(self, player):
        return "BB" if player == "SB" else "SB"

    def _next_state(self, stage, player, action, facing):
        """
        Decide next (stage, player, facing) using:
          - facing == "start"  -> current player is first to act this street
          - facing == "after_opponent" -> current player is responding
        Rules respected:
          - SB acts first preflop, BB acts first postflop (flop/turn/river)
          - A betting round closes (advance stage) only when the responder calls/checks
        """
        # immediate fold handled prior
        # preflop handling
        if stage == "preflop":
            # SB opened (first-to-act)
            if facing == "start" and player == "SB":
                # After SB acts, BB must respond
                return "preflop", "BB", "after_opponent"

            # BB is responding to SB
            if facing == "after_opponent" and player == "BB":
                # If BB checks or calls (including "call 0.5"), preflop closes -> flop
                if action == "check" or action.startswith("call"):
                    # Move to flop; BB acts first on flop (per your rule)
                    return "flop", "BB", "start"
                # else BB raised -> SB must respond
                return "preflop", "SB", "after_opponent"

            # Fallback: if somehow SB is responding (rare), route to BB
            return "preflop", self._next_player(player), "after_opponent"

        # postflop handling (BB acts first)
        if stage in ["flop", "turn", "river"]:
            # If current player is first to act on the street (facing == "start")
            if facing == "start":
                # On postflop, BB should be the starter (we assume caller passed player correctly)
                # After the starter acts, the opponent responds
                return stage, self._next_player(player), "after_opponent"

            # If current player is responding (facing == "after_opponent")
            if facing == "after_opponent":
                # If responder calls or checks -> betting round closes -> advance street (or showdown)
                if action == "check" or action.startswith("call"):
                    if stage == "flop":
                        # advance to turn, BB acts first on turn
                        return "turn", "BB", "start"
                    elif stage == "turn":
                        return "river", "BB", "start"
                    elif stage == "river":
                        return "showdown", None, None
                # If responder raises/bets -> other player must respond
                return stage, self._next_player(player), "after_opponent"

        # fallback to showdown
        return "showdown", None, None

    def _remaining_board(self, stage):
        if stage == "preflop":
            return ["FLOP", "TURN", "RIVER"]
        elif stage == "flop":
            return ["TURN", "RIVER"]
        elif stage == "turn":
            return ["RIVER"]
        else:
            return []

    def count_paths(self):
        return len(self.paths)
