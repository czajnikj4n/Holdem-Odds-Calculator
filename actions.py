# actions.py

ACTIONS = {
    "preflop": {
        "SB": {
            "start": ["fold", "call_0.5bb", "raise_1.5bb", "raise_3.5bb", "allin"]
        },
        "BB": {
            "facing_call": ["check", "raise_1bb", "raise_3bb", "allin"],
            "facing_raise": ["fold", "call", "raise_2x", "raise_4x", "allin"],
            "start": ["check"]  # needed if you want to handle cases where BB checks after SB folds (edge case)
        },
    },

    # POSTFLOP STAGES
    "flop": {
        "first": {
            "start": ["check", "bet_1bb", "bet_3bb", "allin"],
        },
        "second": {
            "facing_check": ["check", "bet_1bb", "bet_3bb", "allin"],
            "facing_bet": ["fold", "call", "raise_2x", "raise_4x", "allin"],
        },
    },
    "turn": {
        "first": {
            "start": ["check", "bet_1bb", "bet_3bb", "allin"],
        },
        "second": {
            "facing_check": ["check", "bet_1bb", "bet_3bb", "allin"],
            "facing_bet": ["fold", "call", "raise_2x", "raise_4x", "allin"],
        },
    },
    "river": {
        "first": {
            "start": ["check", "bet_1bb", "bet_3bb", "allin"],
        },
        "second": {
            "facing_check": ["check", "bet_1bb", "bet_3bb", "allin"],
            "facing_bet": ["fold", "call", "raise_2x", "raise_4x", "allin"],
        },
    },
}
