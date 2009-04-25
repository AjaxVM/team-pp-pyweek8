import retrogamelib as rgl

class Object(rgl.gameobject.Object):
    
    def __init__(self, engine):
        rgl.gameobject.Object.__init__(self, self.groups)
        self.engine = engine
        self.offset = (0, 0)
    
    def move(self, dx, dy):
        if dx != 0:
            self.move_one_axis(dx, 0)
        if dy != 0:
            self.move_one_axis(0, dy)

    # Move one axis and check for collisions
    def move_one_axis(self, dx, dy):
        
        # Raise an error if you try to move both the axes
        if dx != 0 and dy != 0:
            raise SystemExit, "You may only move one axis at a time."
        
        # Move the rect
        self.rect.move_ip(dx, dy)
        
        # Get all the tiles you're colliding with
        tiles = self.check_collisions()
        
        # Collision response
        for t in tiles:
            if t.rect.colliderect(self.rect):
                if dx > 0:
                    self.rect.right = t.rect.left
                if dx < 0:
                    self.rect.left = t.rect.right
                if dy > 0:
                    self.rect.bottom = t.rect.top
                if dy < 0:
                    self.rect.top = t.rect.bottom
                self.on_collision(dx, dy, t)
    
    # Called when a collision occurs
    def on_collision(self, dx, dy, tile):
        pass
    
    def draw(self, surface):
        surface.blit(self.image, self.rect.move(*self.offset))
        
    def check_collisions(self):
        tiles = self.engine.tiles
        collide_tiles = []
        
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
                    collide_tiles.append(tile)
        
        return collide_tiles

class Player(Object):
    
    def __init__(self, engine):
        Object.__init__(self, engine)
        self.image = rgl.util.load_image("data/spaceman-1.png")
        self.rect = self.image.get_rect(midtop=(128, 32))
        self.rect.w = 12
        self.rect.h = 28
        self.offset = (-10, -4)
        
        self.jump_speed = 0.0
        self.jump_accel_slow = 0.35
        self.jump_accel_fast = 0.9
        self.jump_accel = self.jump_accel_slow
        self.max_fall = 8.0
        self.jump_force = 8.0
        self.jumping = True
        
    def update(self):
        if self.jump_speed < self.max_fall:
            self.jump_speed += self.jump_accel
        self.move(0, self.jump_speed)
    
    def on_collision(self, dx, dy, tile):
        if dy > 0:
            self.jump_speed = 0
            self.jumping = False
        if dy < 0:
            self.jump_speed = 0

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_speed = -self.jump_force

class Wall(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.image = rgl.util.load_image("data/wall.png")
        self.rect = self.image.get_rect(topleft=pos)

