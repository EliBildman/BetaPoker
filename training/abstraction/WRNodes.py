#connector class between wrnodes
class Conn():
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child
        self.n = 0
        self.total = 1

    def p(self):
        return self.n / self.total

    def inc(self):
        self.n += 1
        self.total += 1

    def dec(self):
        self.total += 1

#nodes to be set in map with N_LEVELS levels of width N_NODES, each level being completely connected to proceeding and succeeding levels
class WRNode():

    #wr: float
    def __init__(self, wr):
        self.wr = wr
        self.conns = []

    def add_child(self, child):
        c = Conn(self, child)
        self.conns.append(c)

    def adjust_for(self, child):
        for c in self.conns:
            if c.child is child:
                c.inc()
            else:
                c.dec()

    #returns if this is the bottom row
    def is_final(self):
        return len(self.conns) == 0

    #get child nodes as list of tuples (WR_Node, p)
    def get_children(self):
        children = []
        for c in self.conns:
            children.append( (c.child, c.p()) )
        return children
        
#combines many (2) WRNodes to represent the full effect of a deal on many (2) players
class WRNatureNode():

    #wr_nodes: [WRNode], children: [WRNatureNode], t: float
    #t is transition prob from last nature state
    def __init__(self, wr_nodes, t, cut = False, is_root = False):
        self.p1_wr, self.p2_wr = wr_nodes
        self.children = []
        self.t = t
        self.is_root = is_root
        self.cut = cut

    #get array of (children, p) where p is combined probability of both nature events
    def get_children(self):
        if self.children or self.cut:
            return self.children

        for p1_c, p1_p in self.p1_wr.get_children():
            for p2_c, p2_p in self.p2_wr.get_children():
                self.children.append( WRNatureNode([p1_c, p2_c], p1_p * p2_p) )

        return self.children

    #is the end of a round
    def is_final(self):
        return self.p1_wr.is_final() and self.p2_wr.is_final() 
