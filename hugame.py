'''
Created on Jul 25, 2017

@author: tommi
'''

from handeval import fasteval, gethand, pcg_brand

from player import Action, Street, Agent

from time import sleep


AGENT1 = Agent()
AGENT2 = Agent()

class HUGame():
    SMALL_BLIND = 50
    BIG_BLIND = 100
    HANDS_PER_ROUND = 200
    
    def __init__(self, agent1, agent2, fullSpeed = False):
        self.player1 = agent1
        self.player2 = agent2
        
        self.player1.set_enemy_state(self.player2.state)
        self.player2.set_enemy_state(self.player1.state)
        
        self.fullSpeed = fullSpeed
    
        self.player1.state.hasButton = bool(pcg_brand(2))
        self.player2.state.hasButton = not self.player1.state.hasButton
        
    def start(self, observer = None):
        if observer:
            observer.state = self.player1.state
            observer.set_enemy_state(self.player2.state)
        for _ in range(self.HANDS_PER_ROUND):
            self.player1.state.hasButton = not self.player1.state.hasButton
            self.player2.state.hasButton = not self.player2.state.hasButton
        
            pCurrent, pEnemy = (self.player1, self.player2) if self.player1.state.hasButton else \
                               (self.player2, self.player1)
            
            hasMoney = pCurrent.state.reset() and pEnemy.state.reset()
            if not hasMoney:
                break          
            
            pCurrent.state.hand, pEnemy.state.hand, boardCards = gethand()
            
            pCurrent.state.boardCards = pEnemy.state.boardCards = boardCards
            
            pCurrent.state.bet(self.SMALL_BLIND)
            pEnemy.state.bet(self.BIG_BLIND)
            pot = 0
            
            for street in Street:
                if street == Street.SHOWDOWN:
                    stateS = fasteval(pCurrent.state.hand + boardCards, 7)
                    enemyS = fasteval(pEnemy.state.hand + boardCards, 7)
                    
                    if stateS != enemyS:
                        winner = pCurrent.state if stateS > enemyS else pEnemy.state
                        winner.add_money(pot)
                    else:
                        pCurrent.state.add_money(int(pot/2))
                        pEnemy.state.add_money(int(pot/2))
                        
                    self.player1.update(street, pot)
                    self.player2.update(street, pot)
                    
                    if observer:
                        observer.update(street, pot)               
                    if not self.fullSpeed:
                        sleep(9)
                    break
                                    
                if observer:
                    observer.update(street, pot)
                if not self.fullSpeed:
                    sleep(1)
                    
                minRaise = self.SMALL_BLIND
                
                if street != Street.PREFLOP:
                    pCurrent, pEnemy = (self.player2, self.player1) if self.player1.state.hasButton else \
                                       (self.player1, self.player2)
                    
                while (not pCurrent.state.isAllIn) and not (pEnemy.state.isAllIn and pEnemy.state.betSize <= pCurrent.state.betSize) \
                        and (pEnemy.state.betSize > pCurrent.state.betSize or not pCurrent.state.hasActed):
                    if observer:
                        observer.update(street, pot)      
                    
                    pCurrent.update(street, pot)                 
                    action, betsize = pCurrent.get_action()
                    
                    if not self.fullSpeed:
                        sleep(0.5)
                    
                    if action == Action.CHECKFOLD:
                        if pEnemy.state.betSize <= pCurrent.state.betSize:
                            action = Action.CHECKCALL
                        else:
                            pEnemy.state.add_money(pEnemy.state.betSize + pCurrent.state.betSize + pot)
                            pCurrent.state.hasFolded = True
                            break
                    if action == Action.CHECKCALL:
                        pCurrent.state.bet(pEnemy.state.betSize)        
                    elif action == Action.BETRAISE:
                        betAttempt = min(max(pEnemy.state.betSize + minRaise, betsize), pEnemy.state.betSize + pEnemy.state.stack)
                        minRaise = max(betAttempt - pEnemy.state.betSize, self.SMALL_BLIND)
                        pCurrent.state.bet(betAttempt)
                    
                    pCurrent.state.hasActed = True
                    pCurrent, pEnemy = pEnemy, pCurrent
                    
                if pCurrent.state.hasFolded or pEnemy.state.hasFolded:
                    break
                else: # Round over
                    pot += pCurrent.state.betSize + pEnemy.state.betSize
                    pCurrent.state.betSize = pEnemy.state.betSize = 0
                    pCurrent.state.hasActed = pEnemy.state.hasActed = False
                
        
if __name__ == "__main__":
    game = HUGame(AGENT1, AGENT2, fullSpeed=True)
    game.start()
                
        
    