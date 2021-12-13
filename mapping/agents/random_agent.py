from random import choice

def rand_agent(p, gamestate):
    moves = []
    if p.can_fold():
        moves.append('fold')
    if p.can_check_call():
        moves.append('call')
    if p.can_bet_raise():
        moves.append('raise')
    return choice(moves)