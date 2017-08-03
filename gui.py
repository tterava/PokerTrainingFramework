import pygame, sys, os
from player import Agent, Action
from handeval import fast_eval
from threading import Thread
from hugame import HUGame
from time import sleep

PLAYER1 = Agent()
PLAYER2 = Agent()

class GameThread(Thread):
    def __init__(self, observer, observeOnly):
        self.observer = observer
        p1 = PLAYER1 if observeOnly else observer
        self.game = HUGame(p1, PLAYER2, fullSpeed = False)
        super().__init__(daemon = True)

    def run(self):
        self.game.start(observer = self.observer)

class GUI(Agent):
    black = 30, 30, 30
    lightGrey = 180, 180, 180
    white = 255, 255, 255
    yellow = 255, 255, 0
    
    ranks = {0: "Two", 1: "Three", 2: "Four",
             3: "Five", 4: "Six", 5: "Seven",
             6: "Eight", 7: "Nine", 8: "Ten",
             9: "Jack", 10: "Queen", 11: "King", 12: "Ace"}
    
    suits = {0: "hearts", 1: "spades", 2: "diamonds", 3: "clubs"}
    
    def get_file_name(self, card):
        r = self.ranks[card[0]] if card[0] >= 9 else card[0] + 2
        return str.lower(str(r)) + "_of_" + self.suits[card[1]] + ".png"
    
    def update_cards(self, board, hand, enemy, showdown):
        self.pocketImages = []
        self.boardImages = []
        self.enemyImages = []     
         
        for card, rect in zip(hand, self.pocketRects):
            self.pocketImages.append(self.get_scaled_image(self.get_file_name(card), rect))
    
        for card, rect in zip(board, self.boardRects):    
            self.boardImages.append(self.get_scaled_image(self.get_file_name(card), rect))
            
        for card, rect in zip(enemy, self.enemyRects):
            img = self.get_file_name(card) if showdown or self.observeOnly else "back.png"
            self.enemyImages.append(self.get_scaled_image(img, rect))         
    
    def get_scaled_image(self, image, destination):
        img = pygame.image.load(os.path.join('png', image))
        return pygame.transform.scale(img, (destination.width, destination.height))
    
    def update_state(self, myState, eState, boardCards, pot, gotButton, showdown = False):       
        self.update_cards(boardCards, myState.hand, eState.hand, showdown)
        self.texts["pot"][0] = self.myfont.render('{0:.2f}'.format(pot / 100), True, (0, 0, 0))
        self.texts["bet"][0] = self.myfont.render('{0:.2f}'.format(myState.betSize / 100), True, (0, 0, 0))
        self.texts["enemyBet"][0] = self.myfont.render('{0:.2f}'.format(eState.betSize / 100), True, (0, 0, 0))
        self.texts["stack"][0] = self.myfont.render('{0:.2f}'.format(myState.stack / 100), True, (0, 0, 0))
        self.texts["enemyStack"][0] = self.myfont.render('{0:.2f}'.format(eState.stack / 100), True, (0, 0, 0))
        self.gotButton = gotButton
        
    def __init__(self, observeOnly = False):
        super().__init__()
        self.observeOnly = observeOnly
        self.gameThread = GameThread(self, observeOnly)       
        
    def start_gui(self,):
        pygame.init()
        self.myfont = pygame.font.SysFont('System', 30)
        
        size = 800, 600
        self.screen = pygame.display.set_mode(size)
        
        self.rects = {"betButton": (pygame.Rect(493, 525, 125, 50), self.lightGrey),
                      "checkButton": (pygame.Rect(338, 525, 125, 50), self.lightGrey),
                      "foldButton": (pygame.Rect(183, 525, 125, 50), self.lightGrey),
                      "betSize": (pygame.Rect(503, 490, 105, 25), self.white),
                      "pot": (pygame.Rect(20, 200, 100, 60), self.white),
                      "bet": (pygame.Rect(515, 375, 120, 60), self.white),
                      "enemyBet": (pygame.Rect(515, 65, 120, 60), self.white),
                      "stack": (pygame.Rect(650, 500, 120, 60), self.white),
                      "enemyStack": (pygame.Rect(650, 15, 120, 60), self.white),
                      "dealer": (pygame.Rect(225, 400, 50, 50), self.black),
                      "enemyDealer": (pygame.Rect(225, 50, 50, 50), self.black)}
        
        self.backGrounds = [pygame.Rect(488, 520, 135, 60),
                            pygame.Rect(333, 520, 135, 60),
                            pygame.Rect(178, 520, 135, 60)]
        
        self.pocketRects = [pygame.Rect(310, 350, 82, 120),
                            pygame.Rect(408, 350, 82, 120)]
        
        self.enemyRects = [pygame.Rect(310, 10, 82, 120),
                           pygame.Rect(408, 10, 82, 120)]
        self.enemyImages = [self.get_scaled_image('back.png', x) for x in self.enemyRects]
        
        self.boardRects = [pygame.Rect(163, 180, 82, 120),
                           pygame.Rect(261, 180, 82, 120),
                           pygame.Rect(359, 180, 82, 120),
                           pygame.Rect(457, 180, 82, 120),
                           pygame.Rect(555, 180, 82, 120)]
        
        self.texts = {"foldButton": [self.myfont.render('Fold', True, (0, 0, 0)), (42, 16)],
                      "checkButton": [self.myfont.render('Check/Call', True, (0, 0, 0)), (10, 16)],
                      "betButton": [self.myfont.render('Bet/Raise', True, (0, 0, 0)), (15, 16)],
                      "pot": [self.myfont.render("0", True, (0, 0, 0)), (12, 19)],
                      "bet": [self.myfont.render("0", True, (0, 0, 0)), (12, 19)],
                      "enemyBet": [self.myfont.render("0", True, (0, 0, 0)), (12, 19)],
                      "stack": [self.myfont.render("0", True, (0, 0, 0)), (12, 19)],
                      "enemyStack": [self.myfont.render("0", True, (0, 0, 0)), (12, 19)]}
        
        self.pocketImages = []
        self.boardImages = []
        self.enemyImages = []
        
        self.gotButton = False
        self.awaitingAction = False 
        self.gameThread.start()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if self.rects["foldButton"][0].collidepoint(pos):
                        self.action = (Action.CHECKFOLD, 0)
                        self.awaitingAction = False
                    elif self.rects["checkButton"][0].collidepoint(pos):
                        self.action = (Action.CHECKCALL, 0)
                        self.awaitingAction = False
                    elif self.rects["betButton"][0].collidepoint(pos):
                        self.action = (Action.BETRAISE, 1000)
                        self.awaitingAction = False

            self.screen.fill(self.black)
            if self.awaitingAction:
                for r in self.backGrounds:
                    pygame.draw.rect(self.screen, self.yellow, r)
            
            for _, (r, c) in self.rects.items():
                pygame.draw.rect(self.screen, c, r)
            
            for x, y in zip(self.pocketImages, self.pocketRects):
                pygame.draw.rect(self.screen, self.white, y)
                self.screen.blit(x, y)
            
            for x, y in zip(self.enemyImages, self.enemyRects):
                pygame.draw.rect(self.screen, self.white, y)
                self.screen.blit(x, y)
                            
            for x, y in zip(self.boardImages, self.boardRects):
                pygame.draw.rect(self.screen, self.white, y)
                self.screen.blit(x, y)
            
            for k, (text, offSet) in self.texts.items():
                parent = self.rects[k][0]
                self.screen.blit(text, (parent.left + offSet[0], parent.top + offSet[1]))
            
            if self.gotButton:
                self.screen.blit(self.get_scaled_image("dealer.png", self.rects["dealer"][0]), self.rects["dealer"][0])
            else:
                self.screen.blit(self.get_scaled_image("dealer.png", self.rects["enemyDealer"][0]), self.rects["enemyDealer"][0])   
                           
            pygame.display.flip()
            pygame.time.wait(50)
        
    def get_action(self):
        self.awaitingAction = True
        while True:        
            if not self.awaitingAction:
                return self.action
            sleep(0.01)
            
if __name__ == "__main__":
    gui = GUI(observeOnly = True)
    gui.start_gui()
            