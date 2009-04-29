import pyggel
from pyggel import *

import random

class HouseGrid(object):
    def __init__(self):
        self.make_grid()

    def make_grid(self):
        grid = []
        for x in xrange(20):
            grid.append([])
            for y in xrange(20):
                grid[-1].append(None)
        self.grid = grid

    def set(self, object, pos):
        try:
            self.grid[pos[0]][pos[1]] = object
        except:
            pass

    def get_random_open_spot(self):
        ok = []
        for x in xrange(20):
            for y in xrange(20):
                obj = self.grid[x][y]
                if not obj:
                    ok.append((x, y))

        if ok:
            return random.choice(ok)
        return None

class HouseItem(object):
    """This object will store something to throw!
       It will be added to the scene like a regular pyggel geometry."""
    def __init__(self, grid, modelname, size=(1,1,1)):
        #do model loading stuff here

        self.grid = grid
        self.size = size

        self.modelname = modelname

        self.model = pyggel.geometry.Sphere(1)
        self.model.scale = size
        self.add_to_grid()

        self.visible = True
        self.next_highlight = False

    def add_to_grid(self):
        p = self.grid.get_random_open_spot()
        if p:
            x, y = p
            self.grid.set(self, (x, y))
            self.model.pos = (x-10, 0, y-10)

            self.visible = True
            self.next_highlight = False

    def render(self, camera=None):
        if self.next_highlight:
            self.next_highlight = False
            self.model.colorize = (1,0,0,1)
        else:
            self.model.colorize = (1,1,1,1)
        self.model.render()

    def highlight(self):
        self.next_highlight = True

    def remove(self):
        self.grid.set(None, (self.model.pos[0]+10, self.model.pos[2]+10))
