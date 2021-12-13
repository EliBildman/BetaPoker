from .RoundNodes import DecisionNode, ValueNode, GameState

RAISE_AMOUNTS = [1, 2] #early and late round fixed raise amounts
NUM_RAISES = 4 
PLAYERS = 2
BB = 1


def build_decision_tree(street_i = 0, starting_pot = 0):

    blinds = [BB, BB / 2] if street_i == 0 else [0, 0]
    pots = blinds if street_i == 0 else [starting_pot / 2, starting_pot / 2]

    init_state = GameState(PLAYERS, pots, [0, 0], 0, street_i, RAISE_AMOUNTS, NUM_RAISES)
    root = DecisionNode(None, init_state)

    def build_children(node):
        for n in node.get_children():
            if type(n) != ValueNode and not n.round_over:
                build_children(n)

    build_children(root)
    return root


