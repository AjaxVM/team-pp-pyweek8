import retrogamelib as rgl
from objects import *

class Engine(object):
    
    def __init__(self):
        self.tiles = []
        self.image = rgl.util.load_image("data/world.png")
        self.pos = [0, 0]

    def parse_level(self):
        tiles = []
        self.tiles = []
        for y in range(15):
            tiles.append([])
            for x in range(16):
                wx, wy = (self.pos[0]*16) + x, (self.pos[1]*15) + y
                color = list(self.image.get_at((wx, wy))[:-1])
                if color == [0, 0, 0]:
                    w = Wall(self, (x*16, y*16))
                    if self.get_at(wx, wy-1) != [0, 0, 0]:
                        w.on_end[0] = True
                    if self.get_at(wx, wy+1) != [0, 0, 0]:
                        w.on_end[1] = True
                    if self.get_at(wx-1, wy) != [0, 0, 0]:
                        w.on_end[2] = True
                    if self.get_at(wx+1, wy) != [0, 0, 0]:
                        w.on_end[3] = True
                    tiles[-1].append(w)
                else:
                    tiles[-1].append(None)
                if color == [0, 0, 255]:
                    Rusher(self, (x*16, y*16))
                if color == [0, 255, 0]:
                    Bat(self, (x*16, y*16))
        self.tiles = tiles

    def get_at(self, x, y):
        try:
            return list(self.image.get_at((x, y)))[:-1]
        except:
            pass
