from objects import *

LAYOUT = [
"WWWWWWWWWWWWWWWWW",
"W...............W",
"W...............W",
"W...............W",
"W...............W",
"W....W.W........W",
"W...............W",
"W...WWWWW.......W",
"W...............W",
"W....W.W........W",
"W...............W",
"W...............W",
"W...............W",
"W...............W",
"WWWWWWWWWWWWWWWWW",
]

class Engine(object):
    
    def __init__(self):
        self.tiles = LAYOUT

    def parse_level(self):
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                char = self.tiles[y][x]
                if char == "W":
                    Wall(self, (x*16, y*16))
