import pygame
from pygame.locals import *

import data, misc

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

class BuildTower(GameObject):
    def __init__(self, game, pos):
        GameObject.__init__(self, game)

        self.image = pygame.Surface((20,20)) #tile size...
        pygame.draw.rect(self.image, (255,0,0), (0,0,20,20), 3)

        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

class Worker(GameObject):
    def __init__(self, game):
        GameObject.__init__(self, game)

        self.image = pygame.Surface((10,10))
        self.image.fill((100,100,255))

        self.rect = self.image.get_rect()
        self.rect.center = self.game.hero.rect.topleft

        self.target = None

    def update(self):
        if not self.target:
            diso = None
            for i in self.game.build_tower_group.objects: #will need to add scraps and whatnot later...
                if not diso:
                    diso = (i, misc.distance(self.rect.center, i.rect.center))
                    continue
                x = misc.distance(self.rect.center, i.rect.center)
                if x < diso[1]:
                    diso = (i, x)

            if diso:
                self.target = diso[0]
            else:
                self.kill()
                return

        if not self.rect.colliderect(self.target.rect):
            #TODO: replace with pathfinding!
            if self.target.rect.centerx < self.rect.centerx:
                self.rect.move_ip(-1, 0)
            else:
                self.rect.move_ip(1, 0)

            if self.target.rect.centery < self.rect.centery:
                self.rect.move_ip(0, -1)
            else:
                self.rect.move_ip(0, 1)
        else:
            print "built!"
            self.target.kill()
            self.target = None
