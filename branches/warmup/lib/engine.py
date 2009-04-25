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
        self.tiles = []

    def parse_level(self):
        tiles = []
        for y in range(len(LAYOUT)):
            tiles.append([])
            for x in range(len(LAYOUT[0])):
                char = LAYOUT[y][x]
                if char == "W":
                    tiles[-1].append(Wall(self, (x*16, y*16)))
                else:
                    tiles[-1].append(None)
        self.tiles = tiles
