from .RoundNodes import DecisionNode, GameState, ValueNode
from .WRNodes import Conn, WRNatureNode
from .AGameNode import AGameNode

#wraps a decision tree with AGameNodes with a given nature state
def wrap_d_tree(p1_wr, p2_wr, d_node, parent, leaf_children):
    
    if type(d_node) is ValueNode:
        return AGameNode(parent, d_node, [p1_wr, p2_wr])

    if not d_node.round_over:
        game_node = AGameNode(parent, d_node, [p1_wr, p2_wr])
        for child in d_node.get_children():
            game_node.add_child( wrap_d_tree(p1_wr, p2_wr, child, game_node, leaf_children) )
        
        game_node.get_info_set() #initilize info_set

    else:
        #send back value
        if p1_wr == p2_wr:
            take = 0
        else:
            take = d_node.gamestate.pots[0] if p1_wr > p2_wr else -d_node.gamestate.pots[1]

        v_node = ValueNode(take, d_node.last_action)
        return AGameNode( parent, v_node, [p1_wr, p2_wr] )

    return game_node

#create a game tree of AGameNodes given a nature tree and deicsion tree
def create_game_tree(n_tree, d_tree_pre, d_tree_post, parent = None, is_preflop = True):

    if n_tree.is_root:
        root = AGameNode(parent, n_tree, None)

        for c in n_tree.get_children():
            root.add_child( create_game_tree(c, d_tree_pre, d_tree_post, parent = root) )
    else:
        root = AGameNode(parent, n_tree, [n_tree.p1_wr.wr, n_tree.p2_wr.wr])
        root.add_child( wrap_d_tree(n_tree.p1_wr.wr, n_tree.p2_wr.wr, (d_tree_pre if is_preflop else d_tree_post), root, n_tree.get_children()) )

        for c in n_tree.get_children():
            create_game_tree(c, d_tree_pre, d_tree_post, parent = root, is_preflop= False)

    return root

def create_cut_gametree(n_tree, d_tree, parent = None): #gametree with only one nature event

    if n_tree.is_root:
        root = AGameNode(parent, n_tree, None)
        for c in n_tree.get_children():
            root.add_child( create_cut_gametree(c, d_tree, parent = root) )
    else:
        root = AGameNode(parent, n_tree, [n_tree.p1_wr.wr, n_tree.p2_wr.wr])
        root.add_child( wrap_d_tree(n_tree.p1_wr.wr, n_tree.p2_wr.wr, d_tree, root, n_tree.get_children()) )

    return root


def create_double_gametree(n_tree, d_tree_a, d_tree_b):
    pass

n_natures = 0

def create_full_gametree(n_tree, d_tree, curr_node = None, parent = None):

    if curr_node is None:
        node = AGameNode(None, n_tree, None)
        for c in n_tree.get_children():
            node.add_child(create_full_gametree(c, d_tree, curr_node = c, parent = node))

    elif type(curr_node) is WRNatureNode:
        node = AGameNode(parent, curr_node, [curr_node.p1_wr.wr, curr_node.p2_wr.wr])
        node.add_child(create_full_gametree(curr_node, d_tree, curr_node = d_tree, parent = node))
    
    elif type(curr_node) is DecisionNode:
        node = AGameNode(parent, curr_node, [n_tree.p1_wr.wr, n_tree.p2_wr.wr])
        if not curr_node.round_over:
            for c in curr_node.get_children():
                node.add_child(create_full_gametree(n_tree, d_tree, curr_node = c, parent = node))
        else:
            old = curr_node.gamestate
            gs = GameState(old.n_players, old.pots, old.stacks, 0, old.street_i + 1, old.raise_amts, old.num_raises)
            next_round_d_tree = DecisionNode(None, gs)
            for c in n_tree.get_children():
                node.add_child(create_full_gametree(n_tree, next_round_d_tree, curr_node = c, parent = node))

    elif type(curr_node) is ValueNode:
        node = AGameNode(parent, curr_node, [n_tree.p1_wr.wr, n_tree.p2_wr.wr])

    return node

def tree_size(n):
    if type(n) is ValueNode:
        return 1
    c = n.get_children()
    num = 1
    for child in c:
        num += tree_size(child)
    return num

