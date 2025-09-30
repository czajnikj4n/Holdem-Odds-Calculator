# test_traverser.py
from action_tree import ActionTreeTraverser

if __name__ == "__main__":
    traverser = ActionTreeTraverser(max_bets=4)

    # Start traversal from the very first action (preflop, SB to act, no facing action)
    traverser.traverse(stage="preflop", player="SB", facing="start")

    # Print the number of unique terminal paths
    print("Total unique action paths:", traverser.count_paths())

    # (Optional) Show a few sample paths to verify structure
    for i, path in enumerate(traverser.paths[:200], start=1):
        print(f"Path {i}:", " → ".join(path))
