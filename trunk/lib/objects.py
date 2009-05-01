import pygame, math
from pygame.locals import *
import random
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
        self.show_hp_bar = False
        self.hp = 0
        self.max_hp = 0
        self.hp_bar_color=(255,0,0)

    def kill(self):
        for i in self.groups:
            i.remove(self)
        self.was_killed = True

    def update(self):
        pass

    def render(self):
        if self.image and self.rect:
            self.game.screen.blit(self.image, self.rect)

        if self.show_hp_bar and self.hp and self.max_hp:
            outer = pygame.Surface((20, 5))
            full = 18 #by 3
            total = int(self.hp*1.0/self.max_hp*full)
            pygame.draw.rect(outer, self.hp_bar_color, (1,1,total, 3))

            r = pygame.Rect(0,0,20,20)
            r.center = self.rect.center
            r.top -= 7

            self.game.screen.blit(outer, r)

    def hit(self, damage):
        if hasattr(self, "hp"):
            self.hp -= damage
            if self.hp <= 0:
                self.kill()
        else:
            self.kill()

    def update_path(self, grid):
        if hasattr(self, "path"):
            if self.path and grid in self.path:
                p = self.path.index(grid)
                changes = [(grid[0]-1,grid[1]-1), (grid[0],grid[1]-1), (grid[0]+1,grid[1]-1),
                           (grid[0]+1,grid[1]),                        (grid[0]+1,grid[1]+1),
                           (grid[0],grid[1]+1), (grid[0]-1,grid[1]+1), (grid[0]-1,grid[1])]
                if p == 0 or p == len(self.path)-1:
                    return #useless info now!
                start = changes.index(self.path[p-1])
                do = []
                for i in xrange(8):
                    i = start+i
                    if i >= 7:
                        i = 7 - i
                    if not changes[i] in (self.path[p+1::]):
                        do.append(changes[i])
                    else:
                        break
                self.path = self.path[0:p] + do + self.path[p+1::]

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
        if self.current_name != None:
            imgs_len = len(self.images[self.current_name])
            imgs = self.images[self.current_name]
            self.image = pygame.transform.rotate(imgs[self.frame/self.delay%imgs_len], self.angle)
            self.rect = self.image.get_rect(center = self.rect.center)
        self.game.screen.blit(self.image, self.rect)
        if self.num_loops < self.loops and self.loops > -1:
            if self.frame >= len(self.images[self.current_name])*self.delay - 1:
                self.num_loops += 1
                self.on_animation_end()

        if self.show_hp_bar and self.hp and self.max_hp:
            outer = pygame.Surface((20, 5))
            full = 18 #by 3
            total = int(self.hp*1.0/self.max_hp*full)
            pygame.draw.rect(outer, self.hp_bar_color, (1,1,total, 3))

            r = pygame.Rect(0,0,20,20)
            r.center = self.rect.center
            r.top -= 7

            self.game.screen.blit(outer, r)

    def on_animation_end(self):
        pass

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

        self.worker_level = 1
        self.warrior_level = 1
        self.trap_level = 1

        self.hp = 2
        self.max_hp = 2

        self.building = None
        self.build_timer = 0

    def build_worker(self):
        if not self.building:
            self.building = Worker
            self.build_timer = 0

    def build_warrior(self):
        if not self.building:
            self.building = BattleBot
            self.build_timer = 0

    def update(self):
        if self.building:
            self.build_timer += 1
            if self.build_timer > self.building.time_cost:
                self.build_timer = 0
                self.building(self.game)
                self.game.money -= self.building.money_cost
                self.game.scraps -= self.building.scrap_cost
                self.building = None
                self.game.update_money()

class Hive(GameObject):
    def __init__(self, game):
        self.groups = game.main_group, game.hive_group
        GameObject.__init__(self, game)

        self.image = pygame.Surface((45, 45))
        self.image.fill((100,0,100))
        pygame.draw.circle(self.image, (255,0,0), (23,22), 25, 3)
        self.rect = self.image.get_rect()
        self.rect.topleft = (5,5)

        self.level = 1

        self.hp = 2
        self.max_hp = 2

        self.counter = 0
        self.num_spawned = 0
        self.wait_for = 10
        self.fast = False

    def update(self):
        self.counter += 1
        if self.fast:
            num = 40
        else:
            num = 200
        if self.counter >= num:
            if not random.randrange(10):
                self.fast = True
            else:
                self.fast = False
            self.counter = 0
            Insect(self.game, self.level)
            self.num_spawned += 1

        if self.num_spawned >= self.wait_for:
            self.wait_for += 10
            self.level += 1

class BuildTower(GameObject):
    def __init__(self, game, pos, to_build="Base Tower"):
        self.groups = game.main_group, game.build_tower_group, game.blocking_group
        GameObject.__init__(self, game)

        self.image = pygame.Surface((20,20)) #tile size...
        pygame.draw.rect(self.image, (255,0,0), (0,0,20,20), 3)

        self.rect = self.image.get_rect()
        x, y = pos
        x += 10
        y += 20 #so we can put it at center...
        self.rect.midbottom = x, y

        if to_build == "Base Tower":
            to_build = TowerBase
        elif to_build == "Missile Tower":
            to_build = MissileTower
        self.to_build = to_build
        self.game.money -= self.to_build.money_cost
        self.game.scraps -= self.to_build.scrap_cost
        self.game.update_money()

        #set blocking!
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(pos), 1)

        self.built = 0

    def kill(self):
        GameObject.kill(self)
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(self.rect.topleft), 0)

class TowerBase(GameObject):
    ui_icon = "data/tower-base.png" #the ui needs these :S
    fire_sound = 'gun1.ogg'
    time_cost = 250
    money_cost = 50
    scrap_cost = 50
    name = "Base Tower"
    def __init__(self, game, pos):
        self.groups = game.main_group, game.tower_group, game.blocking_group
        GameObject.__init__(self, game)

        self.level = 1

        self.image = data.image("data/tower-base.png")

        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.range = 100
        self.selected = False #this is for the ui to swap to upgrading
        #and for rendering of the range circle

        #set blocking!
        x, y = pos #this makes sure we don't grab like the center of the tower which is one tile too high!
        x -= 10
        y -= 20
        self.game.map_grid.set(self.game.map_grid.screen_to_grid((x,y)), 3)

        self.shot_timer = 0
        self.shot_type = Bullet
        self.shot_speed = 45

        self.inc_cost()

        for i in self.game.insect_group.objects:
            i.update_path(self.game.map_grid.screen_to_grid((x, y)))

        self.damage = 5

        self.upgrade_types = [MissileTower]

    def inc_cost(self):
        self.money_cost = int(self.money_cost * 2.25)
        self.scrap_cost = int(self.scrap_cost * 2.25)

    def upgrade(self):
        self.level += 1
        self.game.money -= self.money_cost
        self.game.scraps -= self.scrap_cost
        self.game.update_money()
        self.inc_cost()
        self.damage *= 2
        self.range += 10

    def update(self):
        diso = (None, self.range+1)
        for i in self.game.insect_group.objects:
            x = misc.distance(self.rect.center, i.rect.center)
            if x < diso[1]:
                diso = (i, x)

        if diso[0] and diso[1] < self.range:
            self.shot_timer += 1
            if self.shot_timer >= self.shot_speed:
                self.shot_timer = 0
                target = diso[0]
                self.shot_type(self.game, self.rect.center, self.range+20, target, self.damage)
                self.game.audio.sounds[self.fire_sound].play()
        else:
            self.shot_timer = int(self.shot_speed/2)

    def kill(self):
        GameObject.kill(self)
        x, y = self.rect.midbottom
        x -= 10
        y -= 20 #midbottom of grid size
        self.game.map_grid.set(self.game.map_grid.screen_to_grid((x, y)), 0)

    def render(self):
        GameObject.render(self)
        if self.selected:
            pygame.draw.circle(self.game.screen, (255,255,255), self.rect.center, self.range, 1)

class MissileTower(TowerBase):
    ui_icon = "data/tower-missile.png"
    fire_sound = 'missile1.ogg'
    time_cost = 300
    money_cost = 100
    scrap_cost = 100
    name = "Missile Tower"
    def __init__(self, game, pos):
        TowerBase.__init__(self, game, pos)

        self.image = data.image("data/tower-missile.png")

        self.level = 1

        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.shot_speed = 60
        self.shot_type = Missile
        self.range = 150
        self.damage = 10

        self.upgrade_types = []

    def upgrade(self):
        self.level += 1
        self.game.money -= self.money_cost
        self.game.scraps -= self.scrap_cost
        self.damage += 7
        self.range += 10
        self.inc_cost()

class Bullet(GameObject):
    def __init__(self, game, pos, range, target, damage):
        self.groups = game.main_group, game.bullet_group
        GameObject.__init__(self, game)

        ydiff = target.rect.centery - pos[1]
        xdiff = target.rect.centerx - pos[0]
        angle = math.degrees(math.atan2(xdiff, ydiff))
        x = math.sin(math.radians(angle))
        y = math.cos(math.radians(angle))

        self.image = pygame.Surface((5,5))
        self.rect = self.image.get_rect()

        self.pos = pos

        self.angle = angle

        self.direction = (x, y)
        self.range = range
        self.age = 0
        self.speed = 4
        self.target = target
        self.damage = damage
        

    def update(self):
        self.age += 1
        if self.age > self.range/self.speed:
            self.kill()

        x, y = self.pos
        x += self.direction[0] * self.speed
        y += self.direction[1] * self.speed

        self.pos = (x, y)

        self.rect.center = self.pos

        for i in self.game.insect_group.objects:
            if self.rect.colliderect(i.rect):
                i.hit(self.damage)
                self.kill()
                Explosion(self.game, self.rect.center)

class Missile(Bullet):
    def __init__(self, game, pos, range, target, damage):
        self.groups = game.main_group, game.bullet_group
        Bullet.__init__(self, game, pos, range*2, target, damage)
        self.angle = random.randrange(360)
        self.image.fill((255,0,0))
        self.damage = damage
        self.speed = 2

    def update(self):
        if self.target.was_killed:
            self.kill()
        ydiff = self.target.rect.centery - self.pos[1]
        xdiff = self.target.rect.centerx - self.pos[0]
        angle = math.degrees(math.atan2(xdiff, ydiff))

        if abs(angle-self.angle) <= 25:
            self.angle = angle
        
        if angle< self.angle:
            self.angle -= 20
        else:
            self.angle += 20
        x = math.sin(math.radians(self.angle))
        y = math.cos(math.radians(self.angle))
        self.direction = (x, y)
        
        Bullet.update(self)

class Scraps(GameObject):
    def __init__(self, game, pos):
        self.groups = game.main_group, game.scraps_group, game.blocking_group
        GameObject.__init__(self, game)

        self.image = data.image("data/scraps-1.png")

        self.rect = self.image.get_rect()
        x, y = pos
        x += 10
        y += 10
        self.rect.center = x, y

        self.cooldown = False
        self.timer = 0

        self.game.map_grid.set(self.game.map_grid.screen_to_grid(pos), 2)

    def update(self):
        if self.cooldown:
            self.timer += 1
            if self.timer >= 200:
                self.timer = 0
                self.cooldown = False

class Boulder(GameObject):
    def __init__(self, game, pos):
        self.groups = game.main_group, game.blocking_group
        GameObject.__init__(self, game)

        self.image = data.image("data/rock-%s.png"%(random.randrange(2)+1))

        self.rect = self.image.get_rect()
        x, y = pos
        x += 10
        y += 10
        self.rect.center = x, y

        self.cooldown = False
        self.timer = 0

        self.game.map_grid.set(self.game.map_grid.screen_to_grid(pos), 2)

    def update(self):
        if self.cooldown:
            self.timer += 1
            if self.timer >= 200:
                self.timer = 0
                self.cooldown = False

class RandomTarget(object):
    def __init__(self, game):
        self.rect = pygame.Rect(0,0,20,20)
        res = 0
        while 1:
            x = random.randrange(game.map_grid.size[0])
            y = random.randrange(game.map_grid.size[1])
            if game.map_grid.is_open((x, y)):
                self.rect.topleft = game.map_grid.grid_to_screen((x, y))
            res += 1
            if res >= 10:
                break #oh well, charge the enemy, shall we?

        self.was_killed = False

class Worker(Animation):
    time_cost = 30
    money_cost = 0
    scrap_cost = 35
    used_targets = []
    ui_icon = "data/worker-1.png"
    diesound = 'boom2.ogg'
    def __init__(self, game):
        self.groups = game.main_group, game.bot_group
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

        self.level = self.game.hero.worker_level

        self.target = None
        self.move_timer = 0
        self.have_scraps = False
        self.damage = 1
        self.max_hp = 5*int((self.level+1)*.5)
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.attack_timer = 0

        self.speed = 5
        self.speed -= int(self.level / 2)
        if self.speed < 1:
            self.speed = 1

        self.level = 1

        self.path = None

    def hit(self, damage):
        Animation.hit(self, damage)
        DamageNote(self.game, self.rect.midtop, (255,0,0), damage)

    def reset_target(self):
        if not self.target == self.game.hero:
            if self.target in self.used_targets:
                self.used_targets.remove(self.target)
            self.target = None

    def update(self):
        #Battling first, because we gotta stop movement for that!
        do_hit = []

        if self.rect.colliderect(self.game.hive):
            self.game.hive.hit(1)
            self.kill()

        for i in self.game.insect_group.objects:
            if misc.distance(i.rect.center, self.rect.center) <= 31:
                do_hit.append(i)

        if do_hit:
            self.attack_timer += 1
            if self.attack_timer >= 5:
                self.attack_timer = 0
                for i in do_hit:
                    i.hit(self.damage)
            return #we can't move anymore ;)
        else:
            self.attack_timer = 0

        if not self.target or isinstance(self.target, Scraps) or isinstance(self.target, RandomTarget):
            #if we have no target, or are just going for scraps, see if something more important is needed of us!
            old_target = self.target
            if isinstance(self.target, Scraps):
                self.reset_target() #in case it is a scrap O.o
            diso = None
            passed = []
            for i in self.game.build_tower_group.objects: #will need to add scraps and whatnot later...
                if not i in self.used_targets:
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


            if not diso:
                #we need to find some scraps!
                for i in self.game.scraps_group.objects:
                    if not i in self.used_targets:
                        if not i.cooldown:
                            if not diso:
                                diso = (i, misc.distance(self.rect.center, i.rect.center))
                                continue
                            x = misc.distance(self.rect.center, i.rect.center)
                            if x < diso[1]:
                                diso = (i,x)

            if diso:
                self.target = diso[0]
                if not self.path or old_target != self.target:
                    if not self.path:
                        start = self.game.map_grid.screen_to_grid(self.rect.center)
                    else:
                        start = self.path[0]
                    self.path = self.game.map_grid.calculate_path(start, self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)
                self.used_targets.append(self.target)
            else:
                #ok, can't do ANYTHING
                if self.target == None:
                    self.target = RandomTarget(self.game)
                    if not self.path or old_target != self.target:
                        if not self.path:
                            start = self.game.map_grid.screen_to_grid(self.rect.center)
                        else:
                            start = self.path[0]
                        self.path = self.game.map_grid.calculate_path(start, self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)

        if not self.path:
            if self.target:
                start = self.game.map_grid.screen_to_grid(self.rect.center)
                self.path = self.game.map_grid.calculate_path(start, self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)

        if self.target.was_killed:
            self.reset_target()
            self.animate("stand", 1, 1)
            return

        if not self.rect.colliderect(self.target.rect):
            grid_pos = None
            if self.path:
                x, y = self.game.map_grid.grid_to_screen(self.path[0])
                grid_pos = x+10, y+10
                if self.rect.centerx == grid_pos[0] and self.rect.centery == grid_pos[1]:
                    self.path.pop(0)
                    if self.path:
                        x, y = self.game.map_grid.grid_to_screen(self.path[0])
                        grid_pos = x+10, y+10
                    else:
                        grid_pos = None
            if grid_pos:
                self.move_timer += 1
                if self.move_timer >= self.speed:
                    self.animate("walk", 15, 1)
                    ydiff = grid_pos[1] - self.rect.centery
                    xdiff = grid_pos[0] - self.rect.centerx
                    self.angle = math.degrees(math.atan2(xdiff, ydiff)) + 180
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
            if isinstance(self.target, BuildTower):
                self.target.built += 1
                if self.target.built >= self.target.to_build.time_cost:
                    self.target.kill()
                    t = self.target.to_build(self.game, self.target.rect.midbottom)
                    self.reset_target()
                    self.animate("stand", 1, 1)
                    self.target = None
                    self.path = None
            elif isinstance(self.target, Scraps):
                self.have_scraps = True
                self.target.cooldown = True
                self.reset_target()
                self.target = self.game.hero
                start = self.game.map_grid.screen_to_grid(self.rect.center)
                self.path = self.game.map_grid.calculate_path(start, self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)
            elif isinstance(self.target, Hero):
                self.have_scraps = False
                self.game.scraps += 5
                self.game.update_money()
                self.reset_target()
                self.target = None
                self.path = None
                #do addition of scraps to inventory stuff here!!!
            elif isinstance(self.target, RandomTarget):
                self.target = RandomTarget(self.game) #move again O.o

    def kill(self):
        self.reset_target()

        self.game.audio.sounds[self.diesound].play()

        Animation.kill(self)

    def render(self):
        Animation.render(self)
        if self.path:
            last = None
            for i in self.path:
                x, y = self.game.map_grid.grid_to_screen(i)
                x += 10
                y += 10
                if last:
                    pygame.draw.line(self.game.screen, (0, 255, 0), last, (x, y))
                last = (x, y)

class Insect(Animation):
    def __init__(self, game, level=1):
        self.groups = game.main_group, game.insect_group
        Animation.__init__(self, game)

        self.walk_images = [
            data.image("data/ant-1.png"),
            data.image("data/ant-2.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.rect = self.image.get_rect()
        self.rect.center = self.game.hive.rect.center

        self.diesound = 'die1.ogg'

        self.level = level

        self.target = None
        self.move_timer = 0
        self.attack_timer = 0
        self.path = None

        self.max_hp = 15 * self.level
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.worth = 1 * self.level
        self.damage = 1 * self.level

    def reset_target(self):
        self.target = None

    def hit(self, damage):
        Animation.hit(self, damage)
        if self.hp <= 0:
            self.game.audio.sounds[self.diesound].play()
            self.game.money += self.worth
            self.game.kills += 1
            self.game.update_money()

        DamageNote(self.game, self.rect.midtop, (100,100,255), damage)

    def update(self):

        do_hit = []

        for i in self.game.build_tower_group.objects:
            if misc.distance(i.rect.center, self.rect.center) <= 22:
                i.kill()

        for i in self.game.bot_group.objects:
            if misc.distance(i.rect.center, self.rect.center) <= 31:
                do_hit.append(i)

        if do_hit:
            self.attack_timer += 1
            if self.attack_timer >= 5:
                self.attack_timer = 0
                for i in do_hit:
                    i.hit(self.damage)
            return #we can't move anymore ;)
        else:
            self.attack_timer = 0

        if self.path == None or not self.target:
            self.target = self.game.hero
            if not self.path:
                start = self.game.map_grid.screen_to_grid(self.rect.center)
            else:
                start = self.path[0]
            self.path = self.game.map_grid.calculate_path(start, self.game.map_grid.screen_to_grid(self.game.hero.rect.center))
           

        if not self.rect.colliderect(self.target.rect):
            grid_pos = None
            if self.path:
                x, y = self.game.map_grid.grid_to_screen(self.path[0])
                grid_pos = x+10, y+10
                if self.rect.centerx == grid_pos[0] and self.rect.centery == grid_pos[1]:
                    self.path.pop(0)
                    if self.path:
                        x, y = self.game.map_grid.grid_to_screen(self.path[0])
                        grid_pos = x+10, y+10
                    else:
                        grid_pos = None
            if grid_pos:
                self.move_timer += 1
                if self.move_timer >= 2:
                    self.animate("walk", 10, 1)
                    ydiff = grid_pos[1] - self.rect.centery
                    xdiff = grid_pos[0] - self.rect.centerx
                    self.angle = math.degrees(math.atan2(xdiff, ydiff)) + 180
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
            self.target.hit(1)
            self.kill()

    def render(self):
        Animation.render(self)
        if self.path:
            last = None
            for i in self.path:
                x, y = self.game.map_grid.grid_to_screen(i)
                x += 10
                y += 10
                if last:
                    pygame.draw.line(self.game.screen, (0, 255, 0), last, (x, y))
                last = (x, y)

class Explosion(Animation):
    
    def __init__(self, game, pos):
        self.groups = [game.main_group]
        Animation.__init__(self, game)
        self.imgs = [data.image("data/exp-%d.png" % i) for i in range(1, 5)]
        self.image = self.imgs[0]
        self.add_animation("anim", self.imgs)
        self.rect = self.image.get_rect(center = pos)
        self.animate("anim", 5, 1)
    
    def on_animation_end(self):
        self.kill()


class DamageNote(GameObject):
    def __init__(self, game, pos, color, amount):
        self.groups = [game.damage_notes_group]
        GameObject.__init__(self, game)

        font = data.font("data/font.ttf", 12, True)

        amount = str(amount)
        chars = []
        for char in amount:
            big = font.render(char, 1, (0,0,0))
            new = pygame.Surface((big.get_width()+1, big.get_height()+1)).convert_alpha()
            new.fill((0,0,0,0))
            little = font.render(char, 1, color)
            big.blit(little, (1, 1))
            chars.append(big)

        width = 0
        height = 0
        for i in chars:
            width += i.get_width()
            if i.get_height() > height:
                height = i.get_height()

        my_surf = pygame.Surface((width, height)).convert_alpha()
        my_surf.fill((0,0,0,0))

        self.waft_dir = random.randint(-1,1)

        self.pos = pos

        left = 0
        for i in chars:
            my_surf.blit(i, (left, 0))
            left += i.get_width()

        self.image = my_surf
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.age = 0
        self.move_counter = 0

    def update(self):
        self.age += 1
        if self.age > 50:
            self.kill()

        self.move_counter += 1
        if self.move_counter >= 3:
            self.move_counter = 0
            x, y = self.pos
            x += self.waft_dir*.5
            y -= 1
            self.pos = x, y
            self.rect.center = self.pos


class Trap(GameObject):
    money_cost = 10
    scrap_cost = 20
    ui_icon = "data/spikes.png"
    diesound = 'boom1.ogg'
    def __init__(self, game, pos):
        self.groups = game.main_group, game.trap_group
        GameObject.__init__(self, game)

        self.image = data.image("data/spikes.png")

        self.rect = self.image.get_rect()
        x, y = pos
        x += 10
        y += 20 #so we can put it at center...
        self.rect.midbottom = x, y

        self.game.money -= self.money_cost
        self.game.scraps -= self.scrap_cost
        self.game.update_money()

        self.level = self.game.hero.trap_level

        self.times = 0
        self.max_times = 25 + self.level*10

        #set blocking!
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(pos), 1)

        self.attack_timer = 0
        self.damage = 2 + self.level

    def kill(self):
        GameObject.kill(self)
	self.game.audio.sounds[self.diesound].play()
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(self.rect.topleft), 0)

    def update(self):
        for i in self.game.insect_group.objects:
            if self.rect.colliderect(i.rect):
                self.attack_timer += 1
                if self.attack_timer >= 15:
                    self.attack_timer = 0
                    i.hit(self.damage)
                    self.times += 1
                    if self.times >= self.max_times:
                        self.kill()
                        return


class BattleBot(Worker):
    time_cost = 75
    money_cost = 15
    scrap_cost = 45
    ui_icon = "data/warrior-1.png"
    def __init__(self, game):
        self.groups = game.main_group, game.bot_group
        Animation.__init__(self, game)
        self.walk_images = [
            data.image("data/warrior-1.png"),
            data.image("data/warrior-2.png"),
            ]
        self.stand_images = [
            data.image("data/worker-1.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.add_animation("stand", self.stand_images)

        self.level = self.game.hero.warrior_level

        self.rect = self.image.get_rect()
        self.rect.center = self.game.hero.rect.topleft

        self.target = None
        self.move_timer = 0
        self.have_scraps = False
        self.damage = 3 + self.level
        self.max_hp = 25*int((self.level+1)*.5)
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.attack_timer = 0

        self.path = None

        self.count = 0

    def update(self):
        #Battling first, because we gotta stop movement for that!
        do_hit = []

        if self.rect.colliderect(self.game.hive):
            self.game.hive.hit(1)
            self.kill()

        for i in self.game.insect_group.objects:
            if misc.distance(i.rect.center, self.rect.center) <= 31: #to account for biggest things!
                do_hit.append(i)

        if do_hit:
            self.attack_timer += 1
            if self.attack_timer >= 5:
                self.attack_timer = 0
                for i in do_hit:
                    i.hit(self.damage)
            return #we can't move anymore ;)
        else:
            self.attack_timer = 0

        old_target = self.target
        diso = None
        for i in self.game.insect_group.objects+self.game.hive_group.objects:
            if not diso:
                diso = (i, misc.distance(self.rect.center, i.rect.center))
                continue
            x = misc.distance(self.rect.center, i.rect.center)
            if x < diso[1]:
                diso = (i, x)

        if diso:
            if not (diso[0] == old_target and self.path):
                self.target = diso[0]
                start = self.game.map_grid.screen_to_grid(self.rect.center)
                self.path = self.game.map_grid.calculate_path(start,
                                self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)
                self.count = 0
            else:
                self.count += 1
                if self.count >= 80:
                    start = self.game.map_grid.screen_to_grid(self.rect.center)
                    self.path = self.game.map_grid.calculate_path(start,
                                    self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)
                    self.count = 0
        else:
            #what?!?! this really shouldn't happen...
            self.target = self.game.hive
            start = self.game.map_grid.screen_to_grid(self.rect.center)
            self.path = self.game.map_grid.calculate_path(start,
                            self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)
            self.count = 0

        #later!
        if self.target.was_killed:
            self.reset_target()
            self.path = None
            self.animate("stand", 1, 1)
            return

        if not self.rect.inflate(3,3).colliderect(self.target.rect):
            grid_pos = None
            if self.path:
                x, y = self.game.map_grid.grid_to_screen(self.path[0])
                grid_pos = x+10, y+10
                if self.rect.centerx == grid_pos[0] and self.rect.centery == grid_pos[1]:
                    self.path.pop(0)
                    if self.path:
                        x, y = self.game.map_grid.grid_to_screen(self.path[0])
                        grid_pos = x+10, y+10
                    else:
                        grid_pos = None
            if grid_pos:
                self.move_timer += 1
                if self.move_timer >= 1:
                    self.animate("walk", 15, 1)
                    ydiff = grid_pos[1] - self.rect.centery
                    xdiff = grid_pos[0] - self.rect.centerx
                    self.angle = math.degrees(math.atan2(xdiff, ydiff)) + 180
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
            if isinstance(self.target, Hive):
                self.target.hit(1)
                self.kill()

    def render(self):
        Animation.render(self)
        if self.path:
            last = None
            for i in self.path:
                x, y = self.game.map_grid.grid_to_screen(i)
                x += 10
                y += 10
                if last:
                    pygame.draw.line(self.game.screen, (0, 255, 0), last, (x, y))
                last = (x, y)
