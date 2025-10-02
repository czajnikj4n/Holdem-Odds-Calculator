# test_game_logic_bets.py
from gamelogic import GameLogic
from evaluator import HandEvaluator  # your evaluator

def main():
    # Init game
    game = GameLogic(sb_amount=0.5, bb_amount=1, stack_size=100)
    evaluator = HandEvaluator()

    print("=== Initial State ===")
    for p in game.players:
        print(f"{p.name} ({p.position}): Stack={p.stack}, Current Bet={p.current_bet}")
    print(f"Pot: {game.pot}\n")
    print(f"Hole Cards: {[p.hand for p in game.players]}\n")

    # Actions per street
    action_sequence = {
        "preflop": [(0, "bet 3.5"), (1, "call")],
        "flop": [(0, "check"), (1, "bet 0.25"), (0, "call")],
        "turn": [(0, "check"), (1, "bet 0.5"), (0, "call")],
        "river": [(0, "bet 1"), (1, "fold")]
    }

    # Play street by street
    for street, actions in action_sequence.items():
        print(f"=== {street.upper()} ===")
        if street != "preflop":
            # Deal community cards
            if street == "flop":
                game.community_cards = [game.deck.deal() for _ in range(3)]
            else:
                game.community_cards.append(game.deck.deal())
            print(f"Community Cards: {game.community_cards}")

        for idx, action in actions:
            bet_amount = game.compute_bet_amount(idx, action)
            game.apply_action(idx, action)
            print(f"{game.players[idx].name} ({game.players[idx].position}) -> {action} (Bet Amount: {bet_amount})")
            print(f"Stacks: {[p.stack for p in game.players]}, Pot: {game.pot}\n")

        # Reset current bets at end of street
        for p in game.players:
            p.current_bet = 0

    # Showdown
    game.street = "showdown"
    winners = game.evaluate_showdown(evaluator)
    print("=== SHOWDOWN ===")
    for w in winners:
        print(f"Winner: {w.name} with hand score {w.hand_score}")
        w.stack += game.pot / len(winners)
    print(f"Final Stacks: {[p.stack for p in game.players]}")
    print(f"Pot: {game.pot}")

if __name__ == "__main__":
    main()
