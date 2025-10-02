# actions.py

# -----------------------------
# PRE-FLOP ACTIONS (Heads-up)
# -----------------------------
# SB acts first preflop, BB acts second
PRE_FLOP_ACTIONS = {
    "SB": {
        "start": ["fold", "call 0.5", "raise 1.5", "raise 3.5", "all-in"],
        "after_opponent": ["call 0.5", "raise 1.5", "raise 3.5", "all-in", "fold"],
    },
    "BB": {
        "start": ["check", "raise 1", "raise 3", "all-in", "fold"],
        "after_opponent": ["call", "raise 2x", "raise 4x", "all-in", "fold"],
    }
}

# -----------------------------
# POST-FLOP ACTIONS (Flop/Turn/River)
# -----------------------------
POST_FLOP_ACTIONS = {
    "SB": {
        "start": ["check", "bet 0.25", "bet 0.5", "bet 1", "all-in", "fold"],
        "after_opponent": ["call", "raise 0.25", "raise 0.5", "raise 1", "all-in", "fold"],
    },
    "BB": {
        "start": ["check", "bet 0.25", "bet 0.5", "bet 1", "all-in", "fold"],
        "after_opponent": ["call", "raise 0.25", "raise 0.5", "raise 1", "all-in", "fold"],
    }
}

# -----------------------------
# MERGED ACTIONS FOR EASY ACCESS
# -----------------------------
ACTIONS = {
    "preflop": PRE_FLOP_ACTIONS,
    "flop": POST_FLOP_ACTIONS,
    "turn": POST_FLOP_ACTIONS,
    "river": POST_FLOP_ACTIONS
}
