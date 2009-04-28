import pygame, math
from pygame.locals import *

import data, misc

class GameGroup(object):
    def __init__(self):
        self.objects = []

    def add(self, obj):
        self.objects.append(obj)

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
        for i in self.groups:
            i.add(self)

        self.was_killed = False

    def kill(self):
        for i in self.groups:
            i.remove(self)
        self.was_killed = True

    def update(self):
        pass

    def render(self):
        if self.image and self.rect:
            self.game.screen.blit(self.image, self.rect)

    def hit(self, damage):
        if hasattr(self, "hp"):
            self.hp -= damage
            if self.hp <= 0:
                self.kill()
        else:
            self.kill()

class Animation(GameObject):
    
    def __init__(self, game):
        GameObject.__init__(self, game)
        self.images = {None: []}
        self.current_name = None
        self.loops = 0
        self.frame = 0
        self.delay = 0
        self.num_loops = 0
        self.angle = 0

    def add_animation(self, name, images):
        """Add a sequence of images and assign a name to it
        """
        
        self.images[name] = images
    
    def animate(self, name, delay, loops):
        """Animate a sequence of images identified by `name`.
        Set `loops` to -1 for an infinite animation. `delay` is how many
        frames to delay progressing to the next image.
        """
        
        if self.current_name != name:
            self.current_name = name
            self.loops = loops
            self.frame = 0
            self.delay = delay
            self.num_loops = 0
    
    def render(self):
        """Render the animation.
        """
        
        self.frame += 1
        if self.num_loops < self.loops and self.loops > -1:
            if self.frame > len(self.images[self.current_name]):
                self.num_loops += 1
            if self.num_loops > self.loops:
                self.frame = 0
                self.current_name = None
        if self.current_name:
            imgs_len = len(self.images[self.current_name])
            imgs = self.images[self.current_name]
            self.image = pygame.transform.rotate(imgs[self.frame/self.delay%imgs_len], self.angle)
            self.rect = self.image.get_rect(center = self.rect.center)
        self.game.screen.blit(self.image, self.rect.center)

class MapGrid(object):
    """This object stores all map related stuff, as well as "open"
       spaces for towers/traps to be built on..."""
    def __init__(self, game):
        self.size = (800/20, 500/20)

        self.make_base_grid()
        self.fill((0,0), (10, 10)) #fill in the enemy area so we can't build there!
        self.fill((self.size[0]-8, self.size[1]-8), (8,8))

    def make_base_grid(self):
        """This creates the base grid.
           Each grid must have one of 3 states:
               0: empty
               1: occupied, non-movement-blocking
               2: occupied, blocking"""
        grid = []
        for x in xrange(self.size[0]):
            grid.append([])
            for y in xrange(self.size[1]):
                grid[-1].append(0)

        self.grid = grid

    def fill(self, start, size, code=1):
        """Fill area from start to start + size with occupied stuffs..."""
        for x in xrange(size[0]):
            for y in xrange(size[1]):
                _x=x+start[0]
                _y=y+start[1]
                if not self.out_of_bounds((_x,_y)):
                    self.grid[_x][_y] = code

    def set(self, pos, code=1):
        if self.out_of_bounds(pos):
            return
        self.grid[pos[0]][pos[1]] = code

    def out_of_bounds(self, pos):
        return pos[0] < 0 or pos[0] >= self.size[0] or pos[1] < 0 or pos[1] >= self.size[1]

    def is_open(self, pos):
        return self.grid[pos[0]][pos[1]] == 0

    def is_blocking(self, pos):
        return self.grid[pos[0]][pos[1]] == 2

    def screen_to_grid(self, pos):
        x, y = pos
        x = (int(x/20) if x else 0)
        y = (int(y/20) if y else 0)
        return x, y

    def grid_to_screen(self, pos):
        x, y = pos
        #TODO: why do we need to be adding 10 here - obviously because it is wrong on screen otherwise, but why?
        x = x * 20
        y = y * 20
        return x, y

    def screen_to_screen(self, pos):
        """This just makes sure the screen pos is moved to the nearest grid pos..."""
        return self.grid_to_screen(self.screen_to_grid(pos))

    def empty_around(self, pos):
        """Return wether there are no filled spaces +/- 1 of pos."""
        for x in xrange(pos[0]-1, pos[0]+2):
            for y in xrange(pos[1]-1, pos[1]+2):
                if not self.out_of_bounds((x, y)):
                    if self.grid[x][y]:
                        return False
        return True

class Hero(GameObject):
    def __init__(self, game):
        self.groups = game.main_group, game.hero_group
        GameObject.__init__(self, game)

        self.image = pygame.Surface((50,50)).convert_alpha()
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (255,0,0), (25,25), 25)
        pygame.draw.circle(self.image, (0,0,255), (30,20), 7, 2)

        self.rect = self.image.get_rect()
        self.rect.bottomright = (800,500) #bottom 100 is the ui bar!

        self.hp = 50

class Hive(GameObject):
    def __init__(self, game):
        self.groups = game.main_group, game.hive_group
        GameObject.__init__(self, game)

        self.image = pygame.Surface((45, 45))
        self.image.fill((100,0,100))
        pygame.draw.circle(self.image, (255,0,0), (23,22), 25, 3)
        self.rect = self.image.get_rect()
        self.rect.topleft = (5,5)

        self.hp = 75

        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= 200:
            self.counter = 0
            Insect(self.game)

class BuildTower(GameObject):
    def __init__(self, game, pos):
        self.groups = game.main_group, game.build_tower_group
        GameObject.__init__(self, game)

        self.image = pygame.Surface((20,20)) #tile size...
        pygame.draw.rect(self.image, (255,0,0), (0,0,20,20), 3)

        self.rect = self.image.get_rect()
        x, y = pos
        x += 10
        y += 20 #so we can put it at center...
        self.rect.midbottom = x, y

    def kill(self):
        GameObject.kill(self)
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(self.rect.topleft), 0)
##        for i in self.game.insect_group.objects:
##            i.target = None
##            i.path = None

class Tower(GameObject):
    def __init__(self, game, pos):
        self.groups = game.main_group, game.tower_group
        GameObject.__init__(self, game)

        self.image = pygame.Surface((20, 30))
        pygame.draw.circle(self.image, (255,0,0), (10, 20), 20)

        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.hp = 200

    def kill(self):
        GameObject.kill(self)
        x, y = self.rect.midbottom
        x -= 10
        y -= 20 #midbottom of grid size
        grid = self.game.map_grid.screen_to_grid((x, y))
        self.game.map_grid.set(grid, 0)
##        for i in self.game.insect_group.objects:
##            i.target = None
##            i.path = None

class Worker(Animation):
    used_build_targets = []
    def __init__(self, game):
        self.groups = game.main_group, game.worker_group
        Animation.__init__(self, game)
        self.walk_images = [
            data.image("data/worker-1.png"),
            data.image("data/worker-2.png"),
            ]
        self.stand_images = [
            data.image("data/worker-1.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.add_animation("stand", self.stand_images)

        self.rect = self.image.get_rect()
        self.rect.center = self.game.hero.rect.topleft

        self.target = None
        self.move_timer = 0

    def update(self):
        if not self.target:
            diso = None
            passed = []
            for i in self.game.build_tower_group.objects: #will need to add scraps and whatnot later...
                if not i in self.used_build_targets:
                    if not diso:
                        diso = (i, misc.distance(self.rect.center, i.rect.center))
                        continue
                    x = misc.distance(self.rect.center, i.rect.center)
                    if x < diso[1]:
                        diso = (i, x)
                else:
                    passed.append(i)
            if not diso:
                for i in passed:
                    if not diso:
                        diso = (i, misc.distance(self.rect.center, i.rect.center))
                        continue
                    x = misc.distance(self.rect.center, i.rect.center)
                    if x < diso[1]:
                        diso = (i, x)

            if diso:
                self.target = diso[0]
                self.used_build_targets.append(self.target)
            else:
                return

        if self.target.was_killed:
            self.target = None
            self.animate("stand", 1, 1)
            return

        if not self.rect.colliderect(self.target.rect):
            #TODO: replace with pathfinding!
            prev_pos = self.rect.center
            self.move_timer += 1
            self.animate("walk", 5, 1)
            if self.move_timer >= 3:
                self.move_timer = 0
                ydiff = self.target.rect.centery - self.rect.centery
                xdiff = self.target.rect.centerx - self.rect.centerx
                angle = math.atan2(xdiff, ydiff)
                self.angle = math.degrees(angle)
                self.rect.x += math.sin(math.radians(self.angle))*3
                self.rect.y += math.cos(math.radians(self.angle))*3
        else:
            t = Tower(self.game, self.target.rect.midbottom)
            self.game.tower_group.add(t)
            self.game.main_group.add(t)
            if self.target in self.used_build_targets:
                self.used_build_targets.remove(self.target)
            self.target.kill()
            self.animate("stand", 1, 1)
            self.target = None

    def kill(self):
        if self.target in self.used_build_targets:
            self.used_build_targets.remove(self.target)

        GameObject.kill(self)


class Insect(GameObject):
    def __init__(self, game):
        self.groups = game.main_group, game.insect_group
        GameObject.__init__(self, game)

        self.image = pygame.transform.rotate(pygame.Surface((17,17)).convert_alpha(), 45)
        self.rect = self.image.get_rect()
        self.rect.center = self.game.hive.rect.bottomright

        self.target = None
        self.move_timer = 0
        self.attack_timer = 0
        self.path = None

    def update(self):

        do_hit = []

        for i in self.game.worker_group.objects:
            if misc.distance(i.rect.center, self.rect.center) <= 20:
                do_hit.append(i)

        for i in self.game.build_tower_group.objects:
            if misc.distance(i.rect.center, self.rect.center) <= 20:
                do_hit.append(i)

        for i in self.game.tower_group.objects:
            if misc.distance(i.rect.center, self.rect.center) <=20:
                do_hit.append(i)

        if do_hit:
            self.attack_timer += 1
            if self.attack_timer >= 5:
                self.attack_timer = 0
                for i in do_hit:
                    i.hit(1)
        else:
            self.attack_timer = 0

        if self.path == None or not self.target:
            self.target = self.game.hero
            if not self.path:
                start = self.game.map_grid.screen_to_grid(self.rect.center)
            else:
                start = self.path[0]
            self.path = misc.calculatePath(
                start,
                self.game.map_grid.screen_to_grid(self.game.hero.rect.center),
                self.game.map_grid.grid)
            

        if not self.rect.colliderect(self.target.rect):
            #TODO: replace with pathfinding!
            # shouldn't update pathfinding every frame -- should only update when something significant changes
            grid_pos = None
            if self.path:
                x, y = self.game.map_grid.grid_to_screen(self.path[0])
                mini_rect = pygame.Rect(0,0,20,20)
                mini_rect2 = pygame.Rect(x,y,20,20)
                mini_rect.center = self.rect.center
                grid_pos = x+10, y+10
                if mini_rect == mini_rect2:
                    self.path.pop(0)
                    if self.path:
                        x, y = self.game.map_grid.grid_to_screen(self.path[0])
                        grid_pos = x+10, y+10
                    else:
                        grid_pos = None
            if grid_pos:
                self.move_timer += 1
                if self.move_timer >= 3:
                    self.move_timer = 0
                    if grid_pos[0] < self.rect.centerx:
                        self.rect.move_ip(-1, 0)
                    elif grid_pos[0] > self.rect.centerx:
                        self.rect.move_ip(1, 0)

                    if grid_pos[1] < self.rect.centery:
                        self.rect.move_ip(0, -1)
                    elif grid_pos[1] > self.rect.centery:
                        self.rect.move_ip(0, 1)
        else:
            self.hit(1) #or whatever
            self.kill()
