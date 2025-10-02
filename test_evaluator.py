# test_evaluator_fixed.py
from gamelogic import GameLogic
from evaluator import HandEvaluator

def main():
    evaluator = HandEvaluator()
    game = GameLogic()

    print("Hole Cards:")
    for p in game.players:
        print(f"{p.name}: {p.hand}")

    # ✅ Automatically match bets for testing
    max_bet = max(p.current_bet for p in game.players)
    for p in game.players:
        p.current_bet = max_bet

    # Proceed through streets
    for street in ["flop", "turn", "river"]:
        game.proceed_to_next_street()
        print(f"{street.capitalize()} cards: {game.community_cards}")

        # Optional: reset bets after each street (since we are not simulating real betting)
        max_bet = max(p.current_bet for p in game.players)
        for p in game.players:
            p.current_bet = max_bet

    # ✅ Evaluate showdown
    winners = game.evaluate_showdown(evaluator)
    print("\n--- Showdown ---")
    for p in game.players:
        print(f"{p.name}: Best Hand: {p.best_hand}, Score: {p.hand_score}")
    print("Winner(s):", [p.name for p in winners])

if __name__ == "__main__":
    main()
