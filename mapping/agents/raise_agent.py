def raise_agent(p, gamestate):
    if p.can_bet_raise():
        return 'raise'
    return 'call'