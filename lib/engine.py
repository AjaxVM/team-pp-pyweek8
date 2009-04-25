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
"W...........WW..W",
"W....W.W........W",
"W...............W",
"W...........WW..W",
"W..........WWWWWW",
"W..WW.....WWWWWWW",
"WWWWWWWWWWWWWWWWW",
]

class Engine(object):
    
    def __init__(self):
        self.tiles = []
        self.layout = LAYOUT

    def parse_level(self):
        tiles = []
        for y in range(len(self.layout)):
            tiles.append([])
            for x in range(len(self.layout[0])):
                char = self.layout[y][x]
                if char == "W":
                    tiles[-1].append(Wall(self, (x*16, y*16)))
                else:
                    tiles[-1].append(None)
        self.tiles = tiles
