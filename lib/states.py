import pygame
from pygame.locals import *

import data

class GameState(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.children = {}

        self._use_child = None

    def use_child(self, name):
        if name in self.children:
            self._use_child = self.children[name](self)
        else:
            self._use_child = None

    def goback(self):
        if self.parent:
            self.parent.use_child(None)

    def goback_to_root(self):
        if self.parent:
            self.parent.use_child(None)
            self.parent.goback_to_root()

    def get_root(self):
        if self.parent:
            return self.parent.get_root()
        return self

    def do_update(self):
        if self._use_child:
            self._use_child.do_update()
            return
        self.update()

    def update(self):
        pass

class Menu(GameState):
    def __init__(self, parent):
        GameState.__init__(self, parent)

        self.text = data.font(None, 32).render("Test!", 1, [255,0,0])

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.get_root().shutdown()
                return

        screen = self.get_root().screen
        screen.fill((0,0,0))
        screen.blit(self.text, (0,0))
        pygame.display.flip()
