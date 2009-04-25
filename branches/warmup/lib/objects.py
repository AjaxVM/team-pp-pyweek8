import pygame, random
import retrogamelib as rgl

def flip_images(images):
    new = []
    for i in images:
        new.append(pygame.transform.flip(i, 1, 0))
    return new

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
        li = rgl.util.load_image
        
        self.right_legs = [li("data/spaceman-legs-%d.png" % i) for i in range(1, 6)]
        self.left_legs = flip_images(self.right_legs)
        self.right_tops = [li("data/spaceman-top-%d.png" % i) for i in range(1, 3)]
        self.left_tops = flip_images(self.right_tops)
        self.legs = self.right_legs
        self.tops = self.right_tops
        
        self.top_image = self.tops[0]
        self.legs_image = self.legs[0]
        self.rect = pygame.Rect(0, 0, 10, 28)
        self.rect.midtop = (128, 16)
        self.offset = (-11, -4)
        self.z = 1
        
        self.jump_speed = 0.0
        self.jump_accel_slow = 0.35
        self.jump_accel_fast = 0.9
        self.jump_accel = self.jump_accel_slow
        self.max_fall = 8.0
        self.jump_force = 8.0
        self.jumping = True
        
        self.facing = 1
        self.frame = 0
        self.moving = False
        self.lookup = False
        
    def draw(self, surface):
        surface.blit(self.legs_image, self.rect.move(self.offset))
        surface.blit(self.top_image, self.rect.move(self.offset[0], self.offset[1]-14))
        
    def update(self):
        
        # Increase the animation frame
        self.frame += 1
        
        # Move the Y axis by the jump speed, and apply gravity
        if self.jump_speed < self.max_fall:
            self.jump_speed += self.jump_accel
        self.move(0, self.jump_speed)
        
        # If our jump velocity is greater than a certain amount, we must
        # have fallen off a cliff - so set the jumping value to true.
        if self.jump_speed > self.jump_accel:
            self.jumping = True
        
        # Set the images value to left or right depending on which way we're facing
        if self.facing > 0:
            self.legs = self.right_legs
            self.tops = self.right_tops
        else:
            self.legs = self.left_legs
            self.tops = self.left_tops
        
        # Set the default frame to zero
        frame = 0
        
        # If we're moving, set the frame to the moving animation frame
        if self.moving:
            frame = self.frame/2%3 + 1
        
        # If we're jumping, override the previous moving animation and set 
        # the frame to the jump one.
        if self.jumping:
            frame = 4
        
        # Set the image to the animation frame
        self.legs_image = self.legs[frame]
        self.top_image = self.tops[0]
        if self.lookup:
            self.top_image = self.tops[1]
    
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
    
    def shoot(self):
        if self.lookup:
            Shot(self.engine, self.rect.midtop, 0)
        else:
            y = self.rect.top + 7
            if self.facing > 0:
                Shot(self.engine, (self.rect.centerx, y), 90)
            else:
                Shot(self.engine, (self.rect.centerx, y), 270)
    
    def move(self, dx, dy):
        Object.move(self, dx, dy)
        if dx != 0:
            self.moving = True
        if dx < 0:
            self.facing = -1
        elif dx > 0:
            self.facing = 1

class Wall(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.image = rgl.util.load_image("data/wall.png")
        self.rect = self.image.get_rect(topleft=pos)
        self.on_end = [False, False, False, False]
   
    '''def draw(self, surface):
        image = pygame.Surface((16, 16))
        if self.on_end[0]:
            pygame.draw.line(image, (255, 255, 255), (0, 0), (15, 0))
        if self.on_end[1]:
            pygame.draw.line(image, (255, 255, 255), (0, 15), (15, 15))
        if self.on_end[2]:
            pygame.draw.line(image, (255, 255, 255), (0, 0), (0, 15))
        if self.on_end[3]:
            pygame.draw.line(image, (255, 255, 255), (15, 0), (15, 15))
        surface.blit(image, self.rect)'''

class Shot(Object):
    
    def __init__(self, engine, pos, angle):
        Object.__init__(self, engine)
        self.image = rgl.util.load_image("data/shot.png")
        self.rect = self.image.get_rect(center=pos)
        self.dx = self.dy = 0
        if angle == 0:
            self.dy = -1
        elif angle == 90:
            self.dx = 1
        elif angle == 270:
            self.dx = -1
        self.rect.x += 16*self.dx
        self.rect.y += 16*self.dy
        self.speed = 8
        self.life = 10
        self.move(0.1, 0)
    
    def update(self):
        self.move(self.dx*self.speed, self.dy*self.speed)
        self.life -= 1
        if self.life <= 0:
            self.kill()
    
    def on_collision(self, dx, dy, tile):
        self.kill()

class Rusher(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.left_images = [rgl.util.load_image("data/rusher-%d.png" % i) for i in range(1, 4)]
        self.right_images = flip_images(self.left_images)
        self.images = self.left_images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.dx = random.choice([-1, 1])
        if self.dx > 0:
            self.images = flip_images(self.images)
        self.speed = 1
        self.frame = 0
        self.hitframe = 0
        self.hp = 3
    
    def update(self):
        self.hitframe -= 1
        if self.hitframe <= 0:
            self.move(self.dx*self.speed, 4)
        self.image = self.images[self.frame/4%2]
        if self.hitframe > 0:
            self.image = self.images[2]
        if self.dx > 0:
            self.images = self.right_images
        else:
            self.images = self.left_images
        self.frame += 1
    
    def on_collision(self, dx, dy, tile):
        start_dx = self.dx
        if self.rect.bottom >= tile.rect.top and dy > 0:
            if tile.on_end[2] == True and self.rect.left <= tile.rect.left:
                self.dx = abs(start_dx)
            elif tile.on_end[3] == True and self.rect.right >= tile.rect.right:
                self.dx = -abs(start_dx)
        else:
            if tile.on_end[2] or tile.on_end[3] and dx != 0:
                if self.rect.centerx < tile.rect.centerx:
                    self.dx = -abs(start_dx)
                    self.rect.right = tile.rect.left
                elif self.rect.centerx > tile.rect.centerx:
                    self.dx = abs(start_dx)
                    self.rect.left = tile.rect.right

    def hit(self):
        if self.hitframe <= 0:
            self.hitframe = 3
            self.hp -= 1
            if self.hp <= 0:
                self.kill()
    
    def do_ai(self, player):
        pass

class Bat(Object):
    
    def __init__(self, engine, pos):
        Object.__init__(self, engine)
        self.images = [rgl.util.load_image("data/bat-%d.png" % i) for i in range(1, 5)]
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.frame = 0
        self.hitframe = 0
        self.hp = 3
        self.dy = 0
    
    def update(self):
        self.hitframe -= 1
        if self.hitframe <= 0:
            self.move(0, self.dy)
        self.image = self.images[self.frame/4%2 + 1]
        if self.dy == 0:
            self.image = self.images[0]
        if self.hitframe > 0:
            self.image = self.images[3]
        self.frame += 1
    
    def on_collision(self, dx, dy, tile):
        self.dy = 0

    def hit(self):
        if self.hitframe <= 0:
            self.hitframe = 3
            self.hp -= 1
            if self.hp <= 0:
                self.kill()

    def do_ai(self, player):
        if player.rect.left < self.rect.right and player.rect.right > self.rect.left:
            self.dy = 5

class Crawly(Object):
    
    def __init__(self, engine, pos, side):
        Object.__init__(self, engine)
        self.left_images = [rgl.util.load_image("data/crawly-%d.png" % i) for i in range(1, 4)]
        self.right_images = flip_images(self.left_images)
        self.images = self.left_images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.dy = random.choice([-1, 1])
        self.speed = 1
        self.frame = 0
        self.hitframe = 0
        self.hp = 3
        self.side = side
    
    def update(self):
        self.hitframe -= 1
        if self.hitframe <= 0:
            self.move(1*self.side, self.dy*self.speed)
        self.image = self.images[self.frame/4%2]
        if self.hitframe > 0:
            self.image = self.images[2]
        if self.side > 0:
            self.images = self.right_images
        else:
            self.images = self.left_images
        self.frame += 1
    
    def on_collision(self, dx, dy, tile):
        start_dy = self.dy
        if dx != 0:
            if tile.on_end[0] and self.rect.top <= tile.rect.top+1:
                self.dy = abs(start_dy)
            elif tile.on_end[1]:
                self.dy = -abs(start_dy)
        else:
            if tile.on_end[0] or tile.on_end[1] and dy != 0:
                if self.rect.centery < tile.rect.centery:
                    self.dy = -abs(start_dy)
                    self.rect.bottom = tile.rect.top
                elif self.rect.centery > tile.rect.centery:
                    self.dy = abs(start_dy)
                    self.rect.top = tile.rect.bottom

    def hit(self):
        if self.hitframe <= 0:
            self.hitframe = 3
            self.hp -= 1
            if self.hp <= 0:
                self.kill()
    
    def do_ai(self, player):
        pass
