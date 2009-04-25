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
                    tiles[-1].append(Wall(self, (x*16, y*16)))
                else:
                    tiles[-1].append(None)
        self.tiles = tiles
