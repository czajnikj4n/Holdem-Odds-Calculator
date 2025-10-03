from gamelogic import GameLogic
from evaluator import HandEvaluator
from cfr import CFRTrainer
from action_tree import ActionTreeTraverser

def main():
    # --- INIT GAME ---
    game = GameLogic(sb_amount=0.5, bb_amount=1, stack_size=10000)

    evaluator = HandEvaluator()

    # Predefine hole cards
    game.players[0].hand = ["A of spades", "K of spades"]  # SB
    game.players[1].hand = ["Q of hearts", "Q of clubs"]   # BB

    # Predefine full 5-card board
    predetermined_board = ['A of hearts', '5 of hearts', 'Q of diamonds', 'J of spades', '5 of spades']
    game.community_cards = predetermined_board.copy()
    game.street = "preflop"  # start at river

    # Define action sequence up to river
    action_sequence = {
        "preflop": [(0, "raise 1.5"), (1, "call")],
        "flop": [(0, "check"), (1, "bet 0.25"), (0, "call")],
        "turn": [(0, "check"), (1, "bet 1"), (0, "call")],
        "river": []  # CFR will explore river
    }

    # --- REPLAY PRE-RIVER ACTIONS ---
    print("=== INITIAL STATE ===")
    for p in game.players:
        print(f"{p.name} ({p.position}): Stack={p.stack}, Current Bet={p.current_bet}")
    print(f"Pot: {game.pot}")
    print(f"Hole Cards: {[p.hand for p in game.players]}\n")

    for street, actions in action_sequence.items():
        if street != "river":
            # Apply actions
            for idx, action in actions:
                bet_amount = game.compute_bet_amount(idx, action)
                game.apply_action(idx, action)
                print(f"{game.players[idx].name} ({game.players[idx].position}) -> {action} (Bet Amount: {bet_amount})")
                print(f"Stacks: {[p.stack for p in game.players]}, Pot: {game.pot}\n")

            # Reset current bets
            for p in game.players:
                p.current_bet = 0.0

    # --- GENERATE ALL RIVER PATHS ---
    traverser = ActionTreeTraverser(max_bets=5)
    traverser.traverse(stage="river", player="SB", facing="start")  # SB acts first on river
    print(f"\nTotal unique river paths: {traverser.count_paths()}\n")

    # --- CFR TRAINING ---
    # Minimal addition: map tokens to streets for correct pre/postflop grouping
    # build the street_map from action_sequence
    # --- BUILD CFR STREET MAP ---
    street_map = {}
    for street, actions in action_sequence.items():
        for idx, action in actions:
            player_str = "SB" if idx == 0 else "BB"
            token = f"{player_str}:{action}"
            street_map[token] = street



    trainer = CFRTrainer(game, evaluator, street_map=street_map)
    avg_strategy, first_action_utils = trainer.train(500)

    # --- PRINT all RIVER PATHS WITH OUTCOME ---
    print("\n=== SAMPLE RIVER PATHS WITH OUTCOME ===")
    for i, path in enumerate(traverser.paths[:227], 1):
        game_copy = game.clone_for_cfr()
        print(f"\n--- Path {i} ---")
        for token in path:
            if token in ["TERMINAL_FOLD", "TERMINAL", "SHOWDOWN"]:
                continue
            player_str, action = token.split(":")
            player_idx = 0 if player_str == "SB" else 1
            game_copy.apply_action(player_idx, action)
            print(f"{player_str} -> {action} | Stacks: {[p.stack for p in game_copy.players]}, Pot: {game_copy.pot}")

        # Evaluate outcome
        winners = game_copy.evaluate_showdown(evaluator)
        pot_won = game_copy.pot
        utility_sb = game_copy.get_utility(0)
        utility_bb = game_copy.get_utility(1)
        winner_names = [p.name for p in winners]
        print(f"Winner(s): {winner_names}, Pot: {pot_won}, Utility: SB={utility_sb}, BB={utility_bb}")

    # --- PRINT CFR AVERAGE STRATEGY ---
    print("\n=== CFR AVERAGE STRATEGY (RIVER) ===")
    for node, strat in avg_strategy.items():
        print(f"Node: {node}")
        for action, prob in strat.items():
            print(f"  {action}: {prob:.3f}")

if __name__ == "__main__":
    main()
