from copy import copy, deepcopy
import uuid

class DecisionNode():

    def __init__(self, parent, gamestate, last_action = None, children = []):
        self.parent = parent
        self.gamestate = gamestate
        self.children = children[:]
        self.last_action = last_action
        self.is_preflop = gamestate.preflop
        self.late_round = gamestate.late_round

        self.round_over = self.check_round_over()


    def check_round_over(self):

        if self.gamestate.turn <= 1:
            return False

        for p in self.gamestate.pots:    
            if p != self.gamestate.pots[0]:
                return False

        return True


    def _get_call(self):
        
        new_state = deepcopy(self.gamestate)
        opp = self.gamestate.opp_player()
        player = self.gamestate.player()

        call_amount = self.gamestate.pots[opp] - self.gamestate.pots[player]

        new_state.pots[player] += call_amount
        new_state.stacks[player] -= call_amount
        new_state.turn += 1

        # ends_round = new_state.turn >= new_state.n_players

        act = Action(player, Move('call', amount = call_amount, value=new_state.pots[player])) #value has to be stored with the amount your calling TO

        return DecisionNode(self, new_state, last_action= act)


    def _get_fold(self):

        v = -self.gamestate.pots[0] if self.gamestate.player() == 0 else self.gamestate.pots[1]
        act = Action(self.gamestate.player(), Move('fold'))
        return ValueNode(v, act)


    def _get_raise(self):
        
        new_state = deepcopy(self.gamestate)
        opp = self.gamestate.opp_player()
        player = self.gamestate.player()

        raise_amount = self.gamestate.curr_raise
        call_amount = self.gamestate.pots[opp] - self.gamestate.pots[player]

        new_state.pots[player] += call_amount + raise_amount
        new_state.stacks[player] -= call_amount + raise_amount

        new_state.turn += 1

        act = Action(player, Move('raise', amount= raise_amount, value= new_state.pots[player]))

        return DecisionNode(self, new_state, last_action= act)


    def get_children(self, ind = None):
        
        if self.children:
            if ind is not None:
                return self.children[ind]
            else:
                return self.children

        if self.round_over:
            return []
            # raise Exception('round over')
        
        self.children.append(self._get_call())

        if self.gamestate.pots[self.gamestate.player()] != self.gamestate.pots[self.gamestate.opp_player()]: #cant fold if there's no bet on the table
            self.children.append(self._get_fold())

        if self.gamestate.pots[self.gamestate.opp_player()] + self.gamestate.curr_raise <= self.gamestate.bet_max:
            self.children.append(self._get_raise())

        if ind is not None:
            return self.children[ind]
        else:
            return self.children

    def __str__(self):
        return f"DecisionNode(n_children: {len(self.children)}, player: {self.gamestate.player()}, last_action: {str(self.last_action)})"


class GameState():

    def __init__(self, n_players, pots, stacks, turn, street_i, raise_amts, num_raises): #late round if turn or river
        self.n_players = n_players
        self.pots = pots
        self.stacks = stacks
        self.turn = turn
        self.street_i = street_i
        self.preflop = street_i == 0
        self.late_round = street_i > 1
        self.raise_amts = raise_amts
        self.num_raises = num_raises

        self.curr_raise = raise_amts[0 if not self.late_round else 1]
        if street_i == 0:
            self.bet_max = self.pots[0] + self.curr_raise * (num_raises - 1)
        else:
            self.bet_max = self.pots[0] + self.curr_raise * num_raises

    def player(self):
        return ( self.turn + (1 if self.preflop else 0) ) % self.n_players

    def opp_player(self):
        return 1 if self.player() == 0 else 0

    def __str__(self):
        return f"GameState(pots: {self.pots}, turn: {self.turn}, player: {self.player()}, preflop: {self.preflop})"

#contains all nodes included in iset
#also has strategy for this iset
class WRInfoSet():
    
    #example node is a history that this info set contains
    #hand_wr: float, example_node: AGameNode
    def __init__(self, example_node):
        self.player = example_node.player
        self.hand_wr = example_node.wrs[example_node.player]
        self.his = example_node.get_history()
        self.preflop = example_node.inner_node.is_preflop
        self.rep = example_node.get_info_rep()
        self.id = uuid.uuid1()
        self.strat = []
        self.nodes = []
        self.regrets = []
        self.regret_sum = 0
        self.breif_his = True
        self.example_node = example_node

        # print(example_node.pots)
        # self._init_strat(example_node)

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def get_nodes(self):
        return self.nodes

    def matches_node(self, node):

        if node.wrs[node.player] != self.hand_wr:
            return False

        n_his = node.get_history()

        if len(n_his) != len(self.his):
            return False

        # for i in range(len(self.his)):
        for self_node, n_node in zip(self.his, n_his):
            # self_node = self.his[i]
            # n_node = n_his[i]

            if type(self_node.inner_node) is not type(n_node.inner_node):
                return False

            if self_node.wrs[self.player] != n_node.wrs[self.player]:
                return False

            if self_node.is_decision:                
                if self_node.inner_node.last_action != n_node.inner_node.last_action:
                    return False

        return True

    #get prob for action in strategy
    def p_action(self, action):
        for s in self.strat:
            if s[0] == action:
                return s[1]

        # print(action)
        # print([str(s[0]) for s in self.strat])
        # print(self)

        raise Exception(f'bad action -- {str(action)} not in {[str(a) for a in self.get_actions()]}')
    
    #get all possible actions from this infoset
    def get_actions(self):
        acts = []
        for s in self.strat:
            acts.append(s[0])
        return acts

    #add to regret total and total for this action
    def update_reret(self, action, regret):
        if regret == 0:
            return
        for c_regret in self.regrets:
            if c_regret[0] == action:
                c_regret[1] += regret
                self.regret_sum += regret
                self._calc_strat()
                return
        raise Exception('bad action')

    def disp_strat(self):
        disp = []
        for s in self.strat:
            disp.append((str(s[0].move), s[1]))
        return disp 

    #assumes regret_sum is non-zero
    def _calc_strat(self):
        for i in range(len(self.strat)):
            self.strat[i][1] = self.regrets[i][1] / self.regret_sum

    def init_strat(self):
        children = self.example_node.get_children()
        for child in children:
            self.strat.append( [child.inner_node.last_action, 1 / len(children)] ) #store strategy as touple with (Action, likelihood)
            self.regrets.append( [child.inner_node.last_action, 0] )

    def get_rep(self): #string representation for hashing
        return self.rep

    def get_strat_obj(self): #get strat as [(action_name, p)]
        return [(s[0].move.name, s[1]) for s in self.strat]

    def __str__(self):
        history_str = '['
        for n in self.his:
            if self.breif_his:
                if n.is_decision:
                    if n.inner_node.last_action is not None:
                        history_str += n.inner_node.last_action.move.name
                    else:
                        history_str += 'none'
            else:
                history_str += str(n)
            history_str += ' '
        history_str += ']'
            

        history_str = '[ '
        for h in self.his:
            history_str += str(h) + ' '
        history_str += ']'
        
        return 'WRInfoSet(player: ' + str(self.player) + ', hand_wr: ' + str(self.hand_wr) + ', his: ' + history_str + ')'




#the leaf nodes of the decision tree, wiht deterministic value
class ValueNode():

    def __init__(self, value, last_action):
        self.last_action = last_action
        self.value = value

    def __str__(self):
        return f"ValueNode(value: {self.value}, last_action: {str(self.last_action)})"

    def get_children(self):
        return []

#a move made with name and amount info
class Move():

    def __init__(self, name, amount = None, value = None): #do action [name] by [amount] to [value]
        self.name = name
        self.amount = amount
        self.value = value

    def __str__(self):
        return f'Move(name: {self.name}, amount: {str(self.amount)}, value: {self.value})' 

#a move made by a player
class Action():

    #player: int, move: int
    def __init__(self, player, move):
        self.player = player
        self.move = move

    def __eq__(self, other):
        return self.player == other.player and self.move.name == other.move.name and self.move.amount == other.move.amount

    def __str__(self):
        return 'Action(player: ' + str(self.player) + ', move: ' + str(self.move) + ')'