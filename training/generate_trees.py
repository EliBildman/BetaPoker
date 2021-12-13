from abstraction.decision_tree import build_decision_tree
from abstraction.wr_game_tree import create_game_tree, tree_size, create_cut_gametree
from abstraction.AGameNode import init_all_strats, info_sets
from abstraction.wr_map import create_nature_tree, create_wr_map, train_nature, cut_nature_tree
from abstraction.wr_game_tree import create_game_tree, tree_size, create_cut_gametree

def gen():

    print('Creating WR Map')

    n_map = create_wr_map()

    print('Training WR Map')

    train_nature(1000, n_map)

    print('Creating Nature Tree')

    n_tree = cut_nature_tree(n_map)

    print('Creating Decision Trees')

    d_trees = []

    d_trees.append(build_decision_tree(street_i = 0, starting_pot = 0))

    for i in range(2, 9, 2):
        d_trees.append(build_decision_tree(street_i= 1, starting_pot = i))

    for i in range(2, 17, 2):
        d_trees.append(build_decision_tree(street_i = 2, starting_pot = i))

    for i in range(2, 33, 2):
        d_trees.append(build_decision_tree(street_i = 3, starting_pot = i))


    g_trees = []

    print('Creating Game Trees')

    for d in d_trees:
        g_trees.append(create_cut_gametree(n_tree, d))

    print('Initializing Strategies')

    init_all_strats()

    print('Done')

    return (g_trees, info_sets)