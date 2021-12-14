from pypokerengine.utils.card_utils import gen_deck, estimate_hole_card_win_rate
import matplotlib.pyplot as plt
from .WRNodes import WRNode, WRNatureNode


NODE_WRS = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
N_LEVELS = 4
N_TESTS = 100


def create_wr_map():
    nodes = [[WRNode(0.5)]]
    for level in range(1, N_LEVELS + 1):
        nodes.append([])
        
        for node_wr in NODE_WRS:
            nodes[level].append( WRNode(node_wr) )

        for node_p in nodes[level - 1]:
            for node_c in nodes[level]:
                node_p.add_child(node_c)

    return nodes 


def get_node(wr, level):
    last = None
    for i, _wr in enumerate(NODE_WRS):
        if last != None:
            if abs(wr - _wr) > abs(wr - last):
                return level[i - 1]
        last = _wr
    return level[-1]


def sim_nature(nodes):
    root = nodes[0][0]
    deck = gen_deck()
    deck.shuffle()

    #deal
    hole = deck.draw_cards(2)
    wr = estimate_hole_card_win_rate(nb_simulation=N_TESTS, nb_player=2, hole_card=hole)
    deal_node = get_node(wr, nodes[1])
    root.adjust_for(deal_node)

    comm = []
    curr = deal_node
    i = 2
    for comm_deal in [3, 1, 1]:
        comm = comm + deck.draw_cards(comm_deal)
        wr = estimate_hole_card_win_rate(nb_simulation=N_TESTS, nb_player=2, hole_card=hole, community_card=comm)
        _next = get_node(wr, nodes[i])
        curr.adjust_for(_next)
        curr = _next
        i += 1

#creates 2-player tree out of map, with two maps
def create_nature_tree(wr_map):

    def rec_build_tree(node):
        for child in node.get_children():
            rec_build_tree(child)

    map_s = wr_map[0][0]
    root = WRNatureNode([map_s, map_s], 1, is_root= True)
    rec_build_tree(root)
    return root


def cut_nature_tree(wr_map):

    n_tree = create_nature_tree(wr_map)

    for c in n_tree.get_children():
        c.cut = True
        c.children = []

    return n_tree


def train_nature(n_itterations, nodes, dump_nodes = False):
    for i in range(n_itterations):
        if i % 100 == 0:
            print(f'\r{i / n_itterations}', end='')
        sim_nature(nodes)
    print()
    return nodes


def plot(node):
    wrs = [ str(int(conn.child.wr * 100)) for conn in node.conns ]
    ps = [ conn.n for conn in node.conns ]
    plt.bar(wrs, ps)
    plt.show()
