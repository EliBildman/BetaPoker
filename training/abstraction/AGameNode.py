from .WRNodes import WRNode, WRNatureNode
from .RoundNodes import DecisionNode, ValueNode, WRInfoSet

info_sets = []
info_sets_dic = {}

def init_all_strats():
    for i in info_sets:
        i.init_strat()

#his: [{"type": "N", "wr": int} | {"type": "D", "name": str, "amount": int|None}]
def make_str_rep(player, round_i, curr_pot, his):
        his_s = ""
        for n in his:
            if n['type'] == 'N':
                his_s += f"N:{n['wr']}|"
            if n['type'] == 'D':
                his_s += f"D:{n['name']}|"
        return f"P{player}R{int(round_i)}B{float(curr_pot)}|{his_s}"

def make_strat_dic():
    strat = {}
    for i_rep in info_sets_dic:
        strat[i_rep] = info_sets_dic[i_rep].get_strat_obj()
    return strat


#wrapper class for WRNatureNode and DecisionNode to make the tree to train on
class AGameNode():

    #parent: AGameNode | None, inner_node: WRNatureNode | DecisionNode, wrs: [float] | None, children = [(AGameNode, float)]
    def __init__(self, parent, inner_node, wrs, children = []):

        if type(inner_node) is not WRNatureNode and type(inner_node) is not DecisionNode and type(inner_node) is not ValueNode:
            raise Exception('wrong node type')

        self.is_nature = type(inner_node) is WRNatureNode
        self.is_value = type(inner_node) is ValueNode
        self.is_decision = type(inner_node) is DecisionNode
        
        self.is_root = parent is None
        self.is_round_end = self.is_decision and inner_node.round_over

        self.parent = parent
        self.inner_node = inner_node
        self.children = children[:]
        self.wrs = wrs
        self.player = inner_node.gamestate.player() if self.is_decision else -1
        self.history = []
        self.info_set = None

        if self.is_decision:
            self.get_info_set()

    #get info set containing this node, assumes this is a decision node
    def get_info_set(self):

        if self.info_set:
            return self.info_set

        rep_s = self.get_info_rep()

        if rep_s in info_sets_dic:
            self.info_set = info_sets_dic[rep_s]
            self.info_set.add_node(self)

        else:
            self.info_set = WRInfoSet(self)
            self.info_set.add_node(self)
            info_sets.append(self.info_set)
            info_sets_dic[self.info_set.get_rep()] = self.info_set

        return self.info_set

    def get_children(self, i = None):
        if i is None:
            return self.children
        else:
            return self.children[i]

    def add_child(self, child):
        self.children.append(child)

    #gives transition prob to this node from parent
    def t(self):
        if self.is_nature:
            return self.inner_node.t
        
        else: #deicsion node or value node
            if self.parent.is_nature:
                return 1.0

            info_set = self.parent.get_info_set()
            return info_set.p_action(self.inner_node.last_action)
            #calculate based on strategy profile of player at parent node, or 1.0 if parent is nature

    #gets move history from last nature to here
    #if player_per only gets info for active player
    def get_history(self):
        if self.history:
            return self.history

        curr = self
        while not curr.is_root:
            self.history.insert(0, curr)
            curr = curr.parent
        
        return self.history

    def get_info_rep(self): #creates a string representation for hash lookup, assumes self.is_decision
        his = []
        for n in self.get_history():
            h = {}
            if n.is_nature:
                h['type'] = 'N'
                h['wr'] = n.wrs[self.player]
                his.append(h)
            elif n.is_decision:
                if n.inner_node.last_action is not None:
                    h['type'] = 'D'
                    h['name'] = n.inner_node.last_action.move.name
                    h['amount'] = float(n.inner_node.last_action.move.value)
                    his.append(h)
        pot = sum(self.inner_node.gamestate.pots)
        return make_str_rep(self.player, self.inner_node.gamestate.street_i, pot, his)

    def __str__(self):
        _type = 'nature' if self.is_nature else ('decision' if self.is_decision else 'value')
        return 'AGameNode(wrs: ' + str(self.wrs) + ', type: ' + _type + ', last_action: ' + (str(self.inner_node.last_action) if not self.is_nature else 'N/A') + ')'