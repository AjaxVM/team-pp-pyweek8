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
        self.clock = pygame.time.Clock()

        self.children = {"menu":states.Menu,
                         None: states.Menu, #this makes sure that if any of the states goback to root the menu always runs!
                         "game": states.Game}
        self.use_child("menu")

    def shutdown(self):
        pygame.quit()
        self.running = False

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.do_update()
            pygame.display.set_caption("FPS: %0.02f" % self.clock.get_fps())
