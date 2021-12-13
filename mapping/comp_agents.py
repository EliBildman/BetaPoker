from pokerface import FixedLimitTexasHoldEm, Stakes
from random import choice
from copy import deepcopy

class Event:

    def __init__(self, player, action, data = None):
        self.player = player
        self.action = action
        self.data = deepcopy(data)

    def __str__(self):
        return f"{self.player} {self.action}" + (f' {self.data}' if self.data else '')

class GameState:
    def __init__(self, game):
        self.his = []
        self.street_i = -1
        self.street = ''
        self.game = game

    def itt_street(self):
        streets = ['preflop', 'flop', 'turn', 'river']
        self.street_i += 1
        self.street = streets[self.street_i]

    def add_event(self, event):
        self.his.append(event)


class EndState:

    def __init__(self, gamestate, p1, p2, bkwrd = False):
        self.his = gamestate.his
        self.takes = (p1.payoff, p2.payoff) if not bkwrd else (p2.payoff, p1.payoff)
        self.winner = 0 if self.takes[0] > self.takes[1] else 1 if self.takes[1] > self.takes[0] else -1 #-1 for tie


class TestResults:

    def __init__(self, endstates):
        self.endstates = endstates

    def wrs(self):
        p1_dubs = len([e for e in self.endstates if e.winner == 0])
        p2_dubs = len([e for e in self.endstates if e.winner == 1])
        return (p1_dubs / len(self.endstates), p2_dubs / len(self.endstates))

    def avg_take(self):
        return sum([e.takes[0] for e in self.endstates]) / len(self.endstates)


def play_round(config, algo_a, algo_b, verbose = False, bkwrd = False):

    stakes = Stakes(0, config['blinds'])
    starting_stacks = config['starting_stacks']

    game = FixedLimitTexasHoldEm(stakes, starting_stacks)

    gamestate = GameState(game)

    def do_player_turn(player, algo, name): #assumes this player is the actor
        if player.can_showdown():
            player.showdown()
        else:
            move = algo(player, gamestate)
            if verbose:
                print(f"player {name} declares {move}")
            if move == 'fold':
                player.fold()
            elif move == 'call':
                player.check_call()
            elif move == 'raise':
                player.bet_raise()
            else:
                raise Exception(f'bad action {move}')
            gamestate.add_event(Event(name, move))
            gamestate.pot = game.pot

    def do_nature(nature, p1, p2, game): #assume nature is actor
        gamestate.itt_street()
        if nature.can_deal_hole():
            if verbose:
                print(f"deals holes")
            nature.deal_hole()
            gamestate.add_event(Event('nature', 'deal_p1', p1.hole))
            nature.deal_hole()
            gamestate.add_event(Event('nature', 'deal_p2', p2.hole))
        elif nature.can_deal_board():
            if verbose:
                print(f"deals board")
            nature.deal_board()
            gamestate.add_event(Event('nature', 'deal_board', game.board))

    p1, p2 = game.players
    nature = game.nature

    while not game.is_terminal():

        if nature.is_actor():
            do_nature(nature, p1, p2, game)

        elif p1.is_actor():
            do_player_turn(p1, algo_a, 'p1')

        elif p2.is_actor():
            do_player_turn(p2, algo_b, 'p2')

    return EndState(gamestate, p1, p2, bkwrd= bkwrd)


def run_test(config, algo_a, algo_b):

    results = []

    for i in range(config['num_tests']):
        if i % 2 == 0:
            results.append(play_round(config, algo_a, algo_b, bkwrd = False))
        else:
            results.append(play_round(config, algo_b, algo_a, bkwrd = True))

    return TestResults(results)
