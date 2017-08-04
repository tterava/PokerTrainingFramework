'''
Created on Jul 25, 2017

@author: tommi
'''

import random
from random import SystemRandom
from handeval import fast_eval

from player import PlayerState, Action, Street, Agent

from time import sleep


AGENT1 = Agent()
AGENT2 = Agent()

class HUGame():
    SMALL_BLIND = 50
    BIG_BLIND = 100
    HANDS_PER_ROUND = 200
    _rng = random
    
    def __init__(self, agent1, agent2, fullSpeed = False):
        self.player1 = (PlayerState(), agent1)
        self.player2 = (PlayerState(), agent2)
        self.fullSpeed = fullSpeed
    
        self.p1HasButton = self._rng.choice([True, False])
        
    def start(self, observer = None):
        for _ in range(self.HANDS_PER_ROUND):
            self.p1HasButton = not self.p1HasButton
        
            (pState, pAgent), (pEnemy, pEnemyAgent) = (self.player1, self.player2) if self.p1HasButton \
                                                      else (self.player2, self.player1)
            
            hasMoney = pState.reset()
            hasMoney = hasMoney and pEnemy.reset()
            if not hasMoney:
                break          
            
            allCards = [(x % 13, int(x / 13)) for x in self._rng.sample(range(52), 9)] # Creates cards in format (Rank, Suit)        
            pState.hand = allCards[:2]
            pEnemy.hand = allCards[2:4]
            boardCards = allCards[4:]
            
            pState.bet(self.SMALL_BLIND)
            pEnemy.bet(self.BIG_BLIND)
            pot = 0
            
            for street in Street:
                if observer:
                    observer.update_state(self.player1[0], self.player2[0], boardCards[:street.value],
                                          pot, self.p1HasButton)
                if not self.fullSpeed:
                    sleep(1)
                    
                minRaise = self.SMALL_BLIND
                
                if street != Street.PREFLOP:
                    (pState, pAgent), (pEnemy, pEnemyAgent) = (self.player2, self.player1) if self.p1HasButton \
                                                              else (self.player1, self.player2)
                    
                while (not pState.isAllIn) and not (pEnemy.isAllIn and pEnemy.betSize <= pState.betSize) \
                        and (pEnemy.betSize > pState.betSize or not pState.hasActed):
                    if observer:
                        observer.update_state(self.player1[0], self.player2[0], boardCards[:street.value],
                                              pot, self.p1HasButton)      
                    
                    pAgent.update_state(pState, pEnemy, boardCards[:street.value], pot,
                                        (self.p1HasButton and pState == self.player1[0]) or
                                        (not self.p1HasButton and pState == self.player2[0]))
                    
                    action, betsize = pAgent.get_action()
                    
                    if not self.fullSpeed:
                        sleep(0.5)
                    
                    if action == Action.CHECKFOLD:
                        if pEnemy.betSize <= pState.betSize:
                            action = Action.CHECKCALL
                        else:
                            pEnemy.add_money(pEnemy.betSize + pState.betSize + pot)
                            pState.hasFolded = True
                            break
                    if action == Action.CHECKCALL:
                        pState.bet(pEnemy.betSize)        
                    elif action == Action.BETRAISE:
                        betAttempt = min(max(pEnemy.betSize + minRaise, betsize), pEnemy.betSize + pEnemy.stack)
                        minRaise = max(betAttempt - pEnemy.betSize, self.SMALL_BLIND)
                        pState.bet(betAttempt)
                    
                    pState.hasActed = True
                    pState, pAgent, pEnemy, pEnemyAgent = pEnemy, pEnemyAgent, pState, pAgent
                    
                if pState.hasFolded or pEnemy.hasFolded:
                    break
                else: # Round over
                    pot += pState.betSize + pEnemy.betSize
                    pState.betSize = pEnemy.betSize = 0
                    pState.hasActed = pEnemy.hasActed = False
                                      
            else: # Showdown was reached
                p1Strenght = fast_eval(pState.hand + boardCards)
                p2Strength = fast_eval(pEnemy.hand + boardCards)
                for s1, s2 in zip(p1Strenght, p2Strength):
                    if s1 != s2:
                        winner = pState if s1 > s2 else pEnemy
                        winner.add_money(pot)
                        break
                else:
                    pState.add_money(int(pot/2))
                    pEnemy.add_money(int(pot/2))
                self.player1[1].update_state(self.player1[0], self.player2[0], boardCards, pot, self.p1HasButton, True)
                self.player2[1].update_state(self.player2[0], self.player1[0], boardCards, pot, not self.p1HasButton, True)
                if observer:
                    observer.update_state(self.player1[0], self.player2[0], boardCards[:street.value],
                                          pot, self.p1HasButton, True)               
                if not self.fullSpeed:
                    sleep(9)                    
        
if __name__ == "__main__":
    game = HUGame(AGENT1, AGENT2)
    game.start()
                
        
    