import retrogamelib as rgl

class Object(rgl.gameobject.Object):
    
    def __init__(self, engine):
        rgl.gameobject.Object.__init__(self, self.groups)
        self.engine = engine
    
    def move(self, dx, dy):
        if dx != 0:
            self.move_one_axis(dx, 0)
        if dy != 0:
            self.move_one_axis(0, dy)

    def move_one_axis(self, dx, dy):
        self.rect.move_ip(dx, dy)
        
        #TODO: Add response
        tiles = self.check_collisions()
        
        
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
    def check_collisions(self):
        tiles = self.engine.tiles
        
        #size = 16x16
        pos_tile = int(self.rect.centerx / 16), int(self.rect.bottom/16)
      
       #This causes the top half of the player to not register a hit, if you want that, then
        #do pos_tile +/- 2
        for x in xrange(pos_tile[0]-2, pos_tile[0]+2):
            for y in xrange(pos_tile[1]-2, pos_tile[1]+2):
                if x < 0 or x >= len(tiles[0]) or\
                   y < 0 or y >= len(tiles):
                    continue

                tile = tiles[y][x]
                if not tile:
                    continue
                if tile.rect.colliderect(self.rect):
                    print "collision!", tile.rect

class Player(Object):
    
    def __init__(self, engine):
        Object.__init__(self, engine)
        self.image = rgl.util.load_image("data/spaceman-1.png")
        self.rect = self.image.get_rect(midtop=(128, 32))

class Wall(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.image = rgl.util.load_image("data/wall.png")
        self.rect = self.image.get_rect(topleft=pos)

