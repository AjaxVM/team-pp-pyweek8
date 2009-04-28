import pygame
from pygame.locals import *

import states
import time

class GameStateEngine(states.GameState):
    def __init__(self):
        states.GameState.__init__(self, None)
        pygame.init()

        self.screen = pygame.display.set_mode((800,600))
        self.running = True

        self.fps = 1.0 / 60

        self.children = {"menu":states.Menu,
                         None: states.Menu, #this makes sure that if any of the states goback to root the menu always runs!
                         "game": states.Game}
        self.use_child("menu")

    def shutdown(self):
        pygame.quit()
        self.running = False

    def run(self):
        while self.running:
            start = time.time()
            self.do_update()
            while time.time() - start < self.fps:
                time.sleep(0.025)
            pygame.display.set_caption("FPS: %s"%round(self.fps/(time.time()-start)*100, 1))
