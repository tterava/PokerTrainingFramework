'''
Created on Jan 26, 2017

@author: tommi
'''
from enum import Enum
from handeval import pcg_brand

class Action(Enum):
    CHECKFOLD = 1
    CHECKCALL = 2
    BETRAISE = 3
    
class Street(Enum):
    PREFLOP = 0
    FLOP = 3
    TURN = 4
    RIVER = 5
    SHOWDOWN = 6

class PlayerState:
    STACK_SIZE = 10000
    MONEY_BEHIND = 90000  
    
    def __init__(self):
        self.stack = self.STACK_SIZE
        self.moneyLeft = self.MONEY_BEHIND
        self.reset()
    
    def bet(self, amount):
        diff = amount - self.betSize
        if diff >= self.stack:
            self.betSize += self.stack
            self.stack = 0
            self.isAllIn = True
        else:
            self.betSize += diff
            self.stack -= diff
            
    def add_money(self, amount):
        if amount > 0:
            self.stack += amount
            
    def reset(self):
        self.betSize = 0
        self.isAllIn = False
        self.hasActed = False
        self.hasFolded = False
        self.cards = []
        self.boardCards = []
        return self.reload_stack()
        
    def reload_stack(self):
        if self.stack == 0:
            if self.moneyLeft <= 0:
                return False
            else:
                self.stack += min(self.STACK_SIZE, self.moneyLeft)
                self.moneyLeft -= self.stack
                return True
        return True        
        
class Agent: # Base class for all AI and human players. Plays random moves. Agent never modifies PlayerStates.
    def __init__(self):
        self.state = PlayerState()
        
    def set_enemy_state(self, state):
        self.enemyState = state
      
    def get_action(self): # AI implementation
        return Action(pcg_brand(3) + 1), pcg_brand(10000)
    
    def update(self, street, pot):
        pass
    
        