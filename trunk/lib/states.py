import pygame
from pygame.locals import *

import data, ui, objects

class GameState(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.children = {}

        self._use_child = None

    def use_child(self, name):
        if name in self.children:
            self._use_child = self.children[name](self)
        else:
            self.use_child(None)

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

        self.app = ui.App(self.get_root().screen)
        ui.Label(self.app, "Testing,\n123", text_color=(255,0,0), pos=(0,0), anchor="topleft")

        ui.Button(self.app, "Play!", text_color=(0,255,0), pos=(0,75),
                  callback=lambda: self.parent.use_child("game"))

    def update(self):
        for event in pygame.event.get():
            if self.app.update(event):
                continue
            if event.type == QUIT:
                self.get_root().shutdown()
                return

        self.get_root().screen.fill((0,0,0))
        self.app.render()
        pygame.display.flip()

class Game(GameState):
    def __init__(self, parent):
        GameState.__init__(self, parent)

        self.screen = self.get_root().screen

        self.background = data.image("data/background1.png")
        self.build_active = None

        self.app = ui.App(self.screen)
        ui.Button(self.app, "GoBack!", pos=(0,500), callback=self.goback)
        ui.Button(self.app, "Build Tower!", pos=(150,500), callback=lambda: setattr(self, "build_active", True))
        ui.Button(self.app, "Build Worker!", pos=(300, 500), callback=self.make_worker)

        self.main_group = objects.GameGroup()
        self.hero_group = objects.GameGroup()
        self.hive_group = objects.GameGroup()
        self.build_tower_group = objects.GameGroup()
        self.worker_group = objects.GameGroup()

        self.hero = objects.Hero(self)
        self.hero_group.add(self.hero)
        self.main_group.add(self.hero)

        self.hive = objects.Hive(self)
        self.hive_group.add(self.hive)
        self.main_group.add(self.hive)

    def make_worker(self):
        w = objects.Worker(self)
        self.worker_group.add(w)
        self.main_group.add(w)

    def update(self):
        for event in pygame.event.get():
            if self.app.update(event):
                continue
            if event.type == QUIT:
                self.get_root().shutdown()
                return

            if event.type == MOUSEBUTTONUP:
                if event.pos[1] <= 500: #this is for us!
                    if event.button == 1:
                        if self.build_active:
                            x, y = event.pos
                            x = (int(x/20) if x else 0) + 1
                            y = (int(y/20) if y else 0) + 1
                            bt = objects.BuildTower(self, (x*20-10, y*20))
                            self.build_tower_group.add(bt)
                            self.main_group.add(bt)
                    if event.button == 3: #left
                        self.build_active = False

        self.hero_group.update()
        self.hive_group.update()
        self.build_tower_group.update()
        self.worker_group.update()
        self.main_group.sort()

        self.screen.blit(self.background, (0,0))
        self.main_group.render()
        pygame.draw.rect(self.screen, (125,125,125), (0,500,800,600))
        self.app.render()
        pygame.display.flip()
