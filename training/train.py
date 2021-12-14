
def prob_history(node, ignore_p = False):
    p = 1.0
    for n in node.get_history():
        # print(n.parent.player, node.player)
        if not (ignore_p and n.parent is not None and n.parent.player == node.player): #ignoring this player, parent belonged to this player as that's when decision was made 
            p *= n.t()
    return p

def cf_value(node, sub_action = None):

    #recursively get EV of node to every possible term, adjusted for transition probs
    def value_to_term(n, p = 1.0):
        if n.is_value:
            return n.inner_node.value * p

        s = 0
        for child in n.get_children():
            s += value_to_term(child, p * child.t())
        return s

    if sub_action is None:
        return prob_history(node, ignore_p= True) * value_to_term(node)

    for child in node.get_children():
        if child.inner_node.last_action == sub_action:
            # *1 here is symbolic to represent this is the subbed strat where this action is always taken
            return prob_history(node, ignore_p= True) * 1.0 * value_to_term(child)
    
    
def cf_regret_node(node, action):
    return cf_value(node, sub_action=action) - cf_value(node)

def cf_regret_iset(iset, action):
    r = 0
    for node in iset.get_nodes():
        r += cf_regret_node(node, action)
    return r


def train_cfr(iterations, info_sets):
    for _ in range(iterations):
        for i_set in info_sets:
            for action in i_set.get_actions():
                regret = cf_regret_iset(i_set, action) * (1 if i_set.player == 0 else -1)
                i_set.update_reret(action, max(regret, 0))