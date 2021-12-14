import pickle
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate, gen_cards
from random import choices
from pickle import load, dump

#need to be set by importing file, temp hack
freq = {}
wr_cache = 'caches/wrs.dic' 

class CFRAgent:

    def __init__(self, strat, config):
        self.strat = strat
        self.config = config
        with open(wr_cache, 'rb') as f:
            self.cache = load(f)
        self.num_new = 0

    def algo(self, p, gamestate):

        def get_recent_events(): #gets the events of most recent street in history
            in_st = []
            for ev in reversed(gamestate.his):
                if ev.player != 'nature':
                    in_st.insert(0, ev)
                else:
                    return in_st
        
        def estimate_and_round_wr(): #gets wr, rounds to nearest clump

            hole_s = [str(c)[::-1] for c in p._hole]
            board_s = [str(c)[::-1] for c in gamestate.game._board]

            hole_s.sort()
            board_s.sort()

            str_r = f"{hole_s}|{board_s}"

            if str_r in self.cache:
                wr = self.cache[str_r]
            else:

                hole = gen_cards(hole_s)
                board = gen_cards(board_s)
                wr = estimate_hole_card_win_rate(1000, 2, hole, board)
                self.cache[str_r] = wr

                if self.num_new == 0:
                    with open(wr_cache, 'wb') as f:
                        dump(self.cache, f)
                
                self.num_new = (self.num_new + 1) % 1000


            closest = self.config['wrs'][0]
            for w in self.config['wrs']:
                if abs(w - wr) < abs(closest - wr):
                    closest = w
            return closest

        wr = estimate_and_round_wr()
        street_i = gamestate.street_i
        pot = gamestate.game.pot + sum(p.bet for p in gamestate.game.players)

        his = [{'type': 'N', 'wr': wr}]
        for ev in get_recent_events():
            his.append({'type': 'D', 'name': ev.action})

        s_rep = make_str_rep(p.index, street_i, pot, his)
        if s_rep not in freq:
            freq[s_rep] = 1
        else:
            freq[s_rep] += 1

        actions = self.strat[s_rep]
        choice = choices([a[0] for a in actions], [a[1] for a in actions])[0]

        return choice


#his: [{"type": "N", "wr": int} | {"type": "D", "name": str}]
def make_str_rep(player, round_i, curr_pot, his):
        his_s = ""
        for n in his:
            if n['type'] == 'N':
                his_s += f"N:{n['wr']}|"
            if n['type'] == 'D':
                his_s += f"D:{n['name']}|"
        return f"P{player}R{int(round_i)}B{float(curr_pot)}|{his_s}"