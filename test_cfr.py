from cfr import CFRTrainer, CFRNode

root_node = CFRNode(
    sb_hand=['2 of hearts', '7 of spades'],
    bb_hand=['A of diamonds', 'A of clubs'],  # or deal from deck
    community_cards=[],
    stacks=[100, 100],
    current_bets=[0.5, 1],  # small blind / big blind
    pot=1.5,
    street="preflop",
    to_act=0,  # SB acts first
    history=[]
)

trainer = CFRTrainer()

# Run iterations
for i in range(100):
    trainer.run_iteration(root_node)

# Inspect strategy for SB
key = trainer.get_info_set_key(root_node)
print("Average strategy for SB with 2h7s:", trainer.get_average_strategy()[key])
