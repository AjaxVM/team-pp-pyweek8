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
                         "game-easy": lambda x:states.Game(x, "easy"),
                         "game-medium": lambda x:states.Game(x, "medium"),
                         "game-hard": lambda x:states.Game(x, "hard"),
                         "lose":states.YouLostMenu,
                         "win":states.YouWonMenu,
                         "tut":states.TutScreen,
                         "tut2":states.TutScreen2,
                         "tut3":states.TutScreen3,
                         "tut4":states.TutScreen4,
                         "tut5":states.TutScreen5,
                         "tut6":states.TutScreen6,
                         "story":states.StoryScreen}
        self.use_child("menu")

        pygame.display.set_caption("Bug Me Not! - Pyweek #8 - April/May 2009 - Team PyedPypers")

    def shutdown(self):
        pygame.quit()
        self.running = False

    def run(self):
        while self.running:
            self.do_update()
            self.clock.tick(60)

##            pygame.display.set_caption("FPS: %0.01f" % (self.clock.get_fps()))
