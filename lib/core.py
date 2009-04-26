import pygame
from pygame.locals import *

import states

class GameStateEngine(states.GameState):
    def __init__(self):
        states.GameState.__init__(self, None)
        pygame.init()

        self.screen = pygame.display.set_mode((800,600))
        self.running = True

        self.children = {"menu":states.Menu,
                         None: states.Menu, #this makes sure that if any of the states goback to root the menu always runs!
                         "game": states.Game}
        self.use_child("menu")

        self.clock = pygame.time.Clock()

    def shutdown(self):
        pygame.quit()
        self.running = False

    def run(self):
        while self.running:
            self.clock.tick(60)
            pygame.display.set_caption("FPS: %s"%round(self.clock.get_fps(), 1))
            self.do_update()
