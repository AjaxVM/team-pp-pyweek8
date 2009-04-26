import pygame
from pygame.locals import *

import data

class GameGroup(object):
    def __init__(self):
        self.objects = []

    def add(self, obj):
        self.objects.append(obj)
        obj._groups.append(self)

    def remove(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    def _ds(self, a, b):
        if a.rect.bottom < b.rect.bottom:
            return -1
        elif a.rect.bottom == b.rect.bottom and\
             a.rect.centerx < b.rect.centerx:
            return -1
        else:
            return 1

    def sort(self):
        self.objects.sort(self._ds)

    def update(self):
        for i in self.objects:
            i.update()

    def render(self):
        for i in self.objects:
            i.render()

class GameObject(object):
    def __init__(self, game):
        self.game = game
        self.image = None
        self.rect = None

        self._groups = []

    def kill(self):
        for i in self._groups:
            i.remove(self)

    def update(self):
        pass

    def render(self):
        if self.image and self.rect:
            self.game.screen.blit(self.image, self.rect)

class Hero(GameObject):
    def __init__(self, game):
        GameObject.__init__(self, game)

        self.image = pygame.Surface((50,50)).convert_alpha()
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (255,0,0), (25,25), 25)
        pygame.draw.circle(self.image, (0,0,255), (30,20), 7, 2)

        self.rect = self.image.get_rect()
        self.rect.bottomright = (800,500) #bottom 100 is the ui bar!

class Hive(GameObject):
    def __init__(self, game):
        GameObject.__init__(self, game)

        self.image = pygame.Surface((45, 45))
        self.image.fill((100,0,100))
        pygame.draw.circle(self.image, (255,0,0), (23,22), 25, 3)
        self.rect = self.image.get_rect()
        self.rect.topleft = (5,5)
