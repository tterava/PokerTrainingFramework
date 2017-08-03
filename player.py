'''
Created on Jan 26, 2017

@author: Prutkis
'''
from enum import Enum
from random import SystemRandom
import random

class Action(Enum):
    CHECKFOLD = 1
    CHECKCALL = 2
    BETRAISE = 3
    
class Street(Enum):
    PREFLOP = 0
    FLOP = 3
    TURN = 4
    RIVER = 5

class PlayerState:
    STACK_SIZE = 10000
    MONEY_BEHIND = 900000000   
    
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
        
class Agent: # Base class for all AI and human players. Plays random moves
    _rng = random
    
    def get_action(self): # AI implementation
        return Action(self._rng.randint(1, 3)), self._rng.randint(1, 10000)
    
    def update_state(self, myState, eState, boardCards, pot, gotButton, showdown = False):
        pass
    
        