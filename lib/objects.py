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

        self.image = data.image("data/steps.png")

        self.rect = self.image.get_rect()
        self.rect.bottomright = (800,500) #bottom 100 is the ui bar!

        self.hero_image = data.image("data/hero.png")
        self.hero_image_hover = data.image("data/hero_hover.png")
        self.hero_rect = self.hero_image.get_rect()
        self.hero_rect.bottomright = self.rect.bottomright
        self.hero_rect.move_ip(25,-10)

        self.worker_level = 1
        self.warrior_level = 1
        self.trap_level = 1

        self.tech_worker_upgrade_cost = 35
        self.tech_warrior_upgrade_cost = 50
        self.tech_trap_upgrade_cost = 25

        self.hp = 20
        self.max_hp = 20

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

    def build_trapper(self):
        if not self.building:
            self.building = TrapperBot
            self.build_timer = 0

    def build_guard(self):
        if not self.building:
            self.building = GuardBot
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

    def hit(self, damage):
        GameObject.hit(self, damage)
        FloatingMessage(self.game, self.hero_rect.topleft, "EEP!!!")

    def render(self):
        GameObject.render(self)

        if self.hero_rect.collidepoint(pygame.mouse.get_pos()):
            self.game.screen.blit(self.hero_image_hover, self.hero_rect)
        else:
            self.game.screen.blit(self.hero_image, self.hero_rect)

        t = data.font("data/font.ttf", 45)
        t1 = t.render(str(self.hp), 1, (0,255,0))
        t2 = t.render(str(self.hp), 1, (0,0,0))
        r = t2.get_rect(midleft=self.rect.inflate(-16,0).midleft)
        self.game.screen.blit(t2, r)
        self.game.screen.blit(t1, r.move(1,1))

class Hive(GameObject):
    def __init__(self, game):
        self.groups = game.main_group, game.hive_group
        GameObject.__init__(self, game)

        self.image = data.image("data/hive.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = (5,5)

        self.level = 1

        self.hp = 20
        self.max_hp = 20

        self.counter = -125 #make it wait a little before first spawn
        self.num_spawned = 0
        self.wait_for = 20
        self.fast = False

        self.fast_chance = 15

        self.flying = False
        self.immune = False

        self.choice_list = [Ant]*10 + [Beetle]*2 + [Worm] + [Wasp]

    def hit(self, damage):
        GameObject.hit(self, damage)
        FloatingMessage(self.game, self.rect.midbottom, "Hurrah!!!")

    def update(self):
        self.counter += 1
        if self.fast:
            num = 100
            num -= self.level * 5
            if num < 70:
                num = 70
        else:
            num = 350
            num -= self.level * 15
            if num < 200:
                num = 200

        fast_chance = self.fast_chance - int(self.level*.5)
        if fast_chance <= 3:
            fast_chance = 3
        if self.counter >= num:
            if len(self.game.insect_group.objects) < 15:
                if not random.randrange(fast_chance):
                    self.fast = True
                else:
                    self.fast = False
                self.counter = 0
                random.choice(self.choice_list)(self.game, self.level)
                self.num_spawned += 1

        if self.num_spawned >= self.wait_for:
            self.wait_for += 10
            self.level += 1
            self.choice_list.extend([Ant] + [Beetle] + [Worm] + [Wasp]) #this will even it out over time ;)
            self.wait_for += 1

    def render(self):
        GameObject.render(self)

        t = data.font("data/font.ttf", 45)
        t1 = t.render(str(self.hp), 1, (255,0,0))
        t2 = t.render(str(self.hp), 1, (0,0,0))
        r = t2.get_rect(center=self.rect.center)
        self.game.screen.blit(t2, r)
        self.game.screen.blit(t1, r.move(1,1))

class BuildTower(GameObject):
    def __init__(self, game, pos, to_build="Base Tower"):
        self.groups = game.main_group, game.build_tower_group, game.blocking_group
        GameObject.__init__(self, game)

        self.image = data.image("data/base.png")

        self.rect = self.image.get_rect()
        x, y = pos
        x += 10
        y += 20 #so we can put it at center...
        self.rect.midbottom = x, y

        if to_build == "Base Tower":
            to_build = TowerBase
        elif to_build == "Missile Tower":
            to_build = MissileTower
        elif to_build == "Bird Food Tower":
            to_build = BirdFoodTower
        elif to_build == "Laser Tower":
            to_build = LaserTower
        elif to_build == "Electro Tower":
            to_build = ElectroTower
        else:
            to_build = TowerBase
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
    base_attack = 10
    base_shoot_speed = 45
    base_range = 100
    def __init__(self, game, pos):
        self.groups = game.main_group, game.tower_group, game.blocking_group
        GameObject.__init__(self, game)

        self.level = 1

        self.image = data.image("data/tower-base.png")

        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.range = int(self.base_range)
        self.selected = False #this is for the ui to swap to upgrading
        #and for rendering of the range circle

        #set blocking!
        x, y = pos #this makes sure we don't grab like the center of the tower which is one tile too high!
        x -= 10
        y -= 20
        self.game.map_grid.set(self.game.map_grid.screen_to_grid((x,y)), 3)

        self.shot_timer = 0
        self.shot_type = Bullet
        self.shot_speed = int(self.base_shoot_speed)

        self.inc_cost()

        for i in self.game.insect_group.objects:
            i.update_path(self.game.map_grid.screen_to_grid((x, y)))

        self.damage = int(self.base_attack)

        self.upgrade_types = [MissileTower, LaserTower]

    def get_stats_at_next_level(self):
        return (self.damage + (5 + int(self.damage/5)),#damage
                10 + self.range,#range
                self.shot_speed) #speed

    def inc_cost(self):
        self.money_cost = int(self.money_cost * 1.75)
        self.scrap_cost = int(self.scrap_cost * 1.75)

    def upgrade(self):
        self.level += 1
        self.game.money -= self.money_cost
        self.game.scraps -= self.scrap_cost
        self.game.update_money()
        self.inc_cost()
        self.damage += 5 + int(self.damage/5)
        self.range += 10

    def update(self):
        diso = (None, self.range+1)
        for i in self.game.insect_group.objects:
            if not i.immune:
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
    base_attack = 25
    base_shoot_speed = 60
    base_range = 150
    def __init__(self, game, pos):
        TowerBase.__init__(self, game, pos)

        self.image = data.image("data/tower-missile.png")

        self.level = 1

        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.shot_speed = int(self.base_shoot_speed)
        self.shot_type = Missile
        self.range = int(self.base_range)
        self.damage = int(self.base_attack)

        self.upgrade_types = [BirdFoodTower]

    def get_stats_at_next_level(self):
        return (self.damage + 7 + int(self.damage/7),#damage
                20 + self.range,#range
                self.shot_speed)

    def upgrade(self):
        self.level += 1
        self.game.money -= self.money_cost
        self.game.scraps -= self.scrap_cost
        self.damage += 7 + int(self.damage/7)
        self.range += 20
        self.inc_cost()
        self.game.update_money()

class BirdFoodTower(TowerBase):
    ui_icon = "data/tower-bird-food.png"
    fire_sound = 'missile1.ogg'
    time_cost = 450
    money_cost = 250
    scrap_cost = 250
    name = "Bird Food Tower"
    base_attack = 100
    base_shoot_speed = 100
    base_range = 175
    def __init__(self, game, pos):
        TowerBase.__init__(self, game, pos)

        self.image = data.image("data/tower-bird-food.png")

        self.level = 1

        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.shot_speed = int(self.base_shoot_speed)
        self.shot_type = BirdFoodPellet
        self.range = int(self.base_range)
        self.damage = int(self.base_attack)

        self.upgrade_types = []

    def get_stats_at_next_level(self):
        return (self.damage + 20 + int(self.damage/10),#damage
                10 + self.range,#range
                self.shot_speed)

    def upgrade(self):
        self.level += 1
        self.game.money -= self.money_cost
        self.game.scraps -= self.scrap_cost
        self.damage += 20 + int(self.damage/10)
        self.range += 10
        self.inc_cost()
        self.game.update_money()

class LaserTower(TowerBase):
    ui_icon = "data/tower-laser.png" #the ui needs these :S
    fire_sound = 'lazor1.ogg'
    time_cost = 250
    money_cost = 100
    scrap_cost = 100
    name = "Laser Tower"
    base_attack = 11
    base_shoot_speed = 20
    base_range = 120
    def __init__(self, game, pos):
        TowerBase.__init__(self, game, pos)

        self.level = 1

        self.image = data.image("data/tower-laser.png")

        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.range = int(self.base_range)
        self.selected = False #this is for the ui to swap to upgrading
        #and for rendering of the range circle

        #set blocking!
        x, y = pos #this makes sure we don't grab like the center of the tower which is one tile too high!
        x -= 10
        y -= 20
        self.game.map_grid.set(self.game.map_grid.screen_to_grid((x,y)), 3)

        self.shot_timer = 0
        self.shot_type = Laser
        self.shot_speed = int(self.base_shoot_speed)

        self.inc_cost()

        for i in self.game.insect_group.objects:
            i.update_path(self.game.map_grid.screen_to_grid((x, y)))

        self.damage = int(self.base_attack)

        self.upgrade_types = [ElectroTower]

    def get_stats_at_next_level(self):
        return (self.damage + (3 + int(self.damage/3)),#damage
                5 + self.range,#range
                self.shot_speed) #speed

    def inc_cost(self):
        self.money_cost = int(self.money_cost * 1.25)
        self.scrap_cost = int(self.scrap_cost * 1.25)

    def upgrade(self):
        self.level += 1
        self.game.money -= self.money_cost
        self.game.scraps -= self.scrap_cost
        self.damage += 3 + int(self.damage/3)
        self.range += 5
        self.inc_cost()
        self.game.update_money()

    def update(self):
        diso = (None, self.range+1)
        for i in self.game.insect_group.objects:
            if not i.immune:
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

class ElectroTower(LaserTower):
    ui_icon = "data/tower-electro.png" #the ui needs these :S
    fire_sound = 'zap1.ogg'
    time_cost = 400
    money_cost = 220
    scrap_cost = 220
    name = "Electro Tower"
    base_attack = 25
    base_shoot_speed = 35
    base_range = 130
    def __init__(self, game, pos):
        LaserTower.__init__(self, game, pos)

        self.image = data.image("data/tower-electro.png")

        self.rect = self.image.get_rect()
        self.rect.midbottom = pos

        self.upgrade_types = []
        self.shot_type = ElectroBolt

    def get_stats_at_next_level(self):
        return (self.damage + (4 + int(self.damage/3)),#damage
                7 + self.range,#range
                self.shot_speed) #speed

    def inc_cost(self):
        self.money_cost = int(self.money_cost * 1.25)
        self.scrap_cost = int(self.scrap_cost * 1.25)

    def upgrade(self):
        self.level += 1
        self.game.money -= self.money_cost
        self.game.scraps -= self.scrap_cost
        self.damage += 4 + int(self.damage/3)
        self.range += 7
        self.inc_cost()
        self.game.update_money()

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
        self.image = pygame.transform.flip(data.image("data/missile.png"), 0, 1)
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

    def render(self):
        _image = self.image
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        Bullet.render(self)
        self.image = _image
        self.rect = _image.get_rect(center=self.rect.center)

class SwoopingBird(Bullet):
    def __init__(self, game, target, damage):
        self.groups = game.main_group, game.bullet_group
        Bullet.__init__(self, game, (0,0), 10000, target, damage)

        self.image = data.image("data/bird.png")
        self.rect = self.image.get_rect()
        self.rect.topright = 800,0
        self.pos = self.rect.center

        self.angle = 0
        self.speed = 6
        self.hit_target = False

    def update(self):

        if self.hit_target or self.target.was_killed:
            x, y = self.pos
            x += self.direction[0] * self.speed*2
            y += self.direction[1] * self.speed*2

            self.pos = (x, y)

            self.rect.center = self.pos

            if not self.rect.colliderect(pygame.Rect(0,0,800,500)):
                self.kill()

        else:
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


            x, y = self.pos
            x += self.direction[0] * self.speed
            y += self.direction[1] * self.speed

            self.pos = (x, y)

            self.rect.center = self.pos

            if self.rect.colliderect(self.target.rect):
                self.target.hit(self.damage)
                self.hit_target = True

    def render(self):
        _image = self.image
        self.image = pygame.transform.rotate(self.image, self.angle+180)
        self.rect = self.image.get_rect(center=self.rect.center)
        Bullet.render(self)
        self.image = _image
        self.rect = _image.get_rect(center=self.rect.center)

class Laser(Bullet):
    def __init__(self, game, pos, range, target, damage):
        self.groups = game.main_group, game.bullet_group
        Bullet.__init__(self, game, pos, range, target, damage)

        self.pos = pos
        self.speed = 0
        self.to_die = False
        self.die_counter = 0

    def update(self):
        if self.target.was_killed:
            self.kill()

        if self.to_die:
            self.die_counter += 1
            if self.die_counter >= 10:
                self.kill()

        else:
            self.target.hit(self.damage)
            Explosion(self.game, self.target.rect.center)
            self.to_die = True

    def render(self):
        pygame.draw.line(self.game.screen, (255,0,0), self.pos, self.target.rect.center, 4)

class ElectroBolt(Laser):
    def __init__(self, game, pos, range, target, damage, used_insects=[], base_pos=None):
        self.groups = game.main_group, game.bullet_group
        Laser.__init__(self, game, pos, range, target, damage)

        if not base_pos:
            base_pos = pos
        self.base_pos = base_pos

        self.used_insects = used_insects
        for i in self.game.insect_group.objects:
            if not (i in self.used_insects or i.immune):
                if misc.distance(base_pos, i.rect.center) < self.range*1.5:
                    self.used_insects.append(i)
                    ElectroBolt(self.game, self.target.rect.center, self.range,
                                i, self.damage, self.used_insects, self.base_pos)

    def render(self):
        pygame.draw.line(self.game.screen, (0,0,255), self.pos, self.target.rect.center, 6)
        pygame.draw.line(self.game.screen, (255,255,255), self.pos, self.target.rect.center, 2)

class BirdFoodPellet(Bullet):
    def __init__(self, game, pos, range, target, damage):
        self.groups = game.main_group, game.bullet_group
        Bullet.__init__(self, game, pos, range, target, damage)

        self.image = data.image("data/bird_food_bullet.png")
        self.speed = 5

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
                SwoopingBird(self.game, self.target, self.damage)
                self.kill()

class Net(Bullet):
    def __init__(self, game, pos, range, target, damage, duration):
        self.groups = game.main_group, game.bullet_group
        Bullet.__init__(self, game, pos, range*2, target, damage)
        self.angle = random.randrange(360)
        self.image = data.image("data/net_shot.png")
        self.damage = damage
        self.duration = duration
        self.speed = 4

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
                i.netted = True
                i.netted_count = 0
                i.hit(self.damage)
                i.netted_duration = self.duration
                self.kill()

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
    money_cost = 10
    scrap_cost = 20
    used_targets = []
    ui_icon = "data/worker-1.png"
    diesound = 'boom2.ogg'

    base_speed = 4
    base_hp = 25
    base_damage = 1
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

        self.name = "Worker"

        self.level = 1

        self.target = None
        self.move_timer = 0
        self.have_scraps = False
        self.damage = int(self.base_damage)
        self.max_hp = int(self.base_hp)
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.attack_timer = 0

        self.speed = self.base_speed
        if self.speed < 1:
            self.speed = 1

        self.scrap_load = 10 * self.level

        for i in xrange(self.game.hero.worker_level-1):
            self.upgrade_level()

        self.path = None

    def upgrade_level(self):
        self.max_hp += 7 + int(self.level*.2)
        self.hp += 7 + int(self.level*.2)
        self.damage += 1
        self.speed -= 1
        if self.speed < 1:
            self.speed = 1
        self.level += 1
        self.scrap_load += 10

    def hit(self, damage):
        Animation.hit(self, damage)
        if not self.was_killed:
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
            if not (i.immune or i.flying):
                if self.rect.inflate(6,6).colliderect(i.rect.inflate(6,6)):
                    do_hit.append(i)

        if do_hit:
            self.attack_timer += 1
            if self.attack_timer >= 25:
                self.attack_timer = 0
                for i in do_hit:
                    i.hit(self.damage)
            if not (self.target == self.game.hero and self.path):
                self.target = self.game.hero
                start = self.game.map_grid.screen_to_grid(self.rect.center)
                self.path = self.game.map_grid.calculate_path(start, self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)
            else:
                start = self.path[0]
                self.path = self.game.map_grid.calculate_path(start, self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)
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
                    self.animate("walk", int(15/self.speed), 1)
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
                if self.have_scraps:
                    self.game.scraps += self.scrap_load
                    self.have_scraps = False
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

class Ant(Animation):
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

        self.ani_speed = 15

        self.level = level

        self.target = None
        self.move_timer = 0
        self.attack_timer = 0
        self.path = None

        self.max_hp = 5 * self.level + self.level
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.worth = 5 * self.level
        self.damage = self.level

        self.speed = 2

        self.immune = False
        self.flying = False
        self.stuck = False
        self.netted = False
        self.netted_duration = 125 #this should probably be overwritten when netter?
        self.netted_count = 0

    def reset_target(self):
        self.target = None

    def hit(self, damage):
        Animation.hit(self, damage)
        if self.hp <= 0:
            self.game.audio.sounds[self.diesound].play()
            self.game.money += self.worth
            self.game.kills += 1
            self.game.update_money()
            DamageNote(self.game, self.rect.midtop, (220, 200, 50), self.worth, True)
            Fadeout(self.game, self.rect.center, self.image)
            return
        DamageNote(self.game, self.rect.midtop, (100,100,255), damage)

    def update(self):

        do_hit = []

        for i in self.game.build_tower_group.objects:
            if self.rect.inflate(6,6).colliderect(i.rect.inflate(6,6)):
                i.kill()

        for i in self.game.bot_group.objects:
            if self.rect.inflate(6,6).colliderect(i.rect.inflate(6,6)):
                do_hit.append(i)

        if do_hit:
            self.attack_timer += 1
            if self.attack_timer >= 25:
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
            if self.netted:
                self.netted_count += 1
                if self.netted_count >= self.netted_duration:
                    self.netted = False
                    self.netted_count = 0
                return # we can't move, wah!
            if self.stuck:
                self.stuck = False
                return #assume this is set each frame by traps ;)
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
                    if self.immune:
                        ta = "walk-immune"
                    else:
                        ta = "walk"
                    self.animate(ta, int(self.ani_speed/self.speed), 1)
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
        if self.netted:
            i = data.image("data/netted_show.png")
            r = i.get_rect(center=self.rect.center)
            self.game.screen.blit(i, r)

class Beetle(Ant):
    def __init__(self, game, level=1):
        self.groups = game.main_group, game.insect_group
        Ant.__init__(self, game, level)

        self.walk_images = [
            data.image("data/beetle-1.png"),
            data.image("data/beetle-2.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.rect = self.image.get_rect()
        self.rect.center = self.game.hive.rect.center

        self.max_hp = 15 * self.level
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.worth = 5 * self.level
        self.damage = 2 * self.level

        self.speed = 4

class Worm(Ant):
    def __init__(self, game, level=1):
        self.groups = game.main_group, game.insect_group
        Ant.__init__(self, game, level)

        self.walk_images = [
            data.image("data/worm-1.png"),
            data.image("data/worm-2.png"),
            ]
        self.walk_images_immune = [
            data.image("data/worm-1-immune.png"),
            data.image("data/worm-2-immune.png"),
            data.image("data/worm-3-immune.png"),
            data.image("data/worm-4-immune.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.add_animation("walk-immune", self.walk_images_immune)
        self.rect = self.image.get_rect()
        self.rect.center = self.game.hive.rect.center

        self.max_hp = 13 * self.level
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.worth = 5 * self.level
        self.damage = int(self.level*1.75)

        self.speed = 4
        self.immune_start = None
        self.went_immune = False
        self.wait = random.randint(250, 500)
        self.wait_counter = 0
        self.ani_speed = 50
        self.immune_distance = random.randint(425, 500)

    def update(self):
        if self.immune:
            self.speed = 5
            self.ani_speed = 65
        else:
            self.speed = 4
            self.ani_speed = 50
        Ant.update(self)

        if not self.immune:
            self.wait_counter += 1
            if self.wait_counter >= self.wait:
                if not self.went_immune:
                    self.went_immune = True
                    self.immune = True
                    self.immune_start = self.rect.center

        if self.immune:
            if misc.distance(self.rect.center, self.immune_start) >= self.immune_distance:
                self.immune = False

class Wasp(Ant):
    def __init__(self, game, level=1):
        Ant.__init__(self, game, level)
        self.kill()
        self.was_killed = False
        self.groups = game.flying_group, game.insect_group
        for i in self.groups:
            i.add(self)

        self.walk_images = [
            data.image("data/wasp-1.png"),
            data.image("data/wasp-2.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.rect = self.image.get_rect()
        self.rect.center = self.game.hive.rect.center

        self.max_hp = 5 + self.level
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.worth = 5 * self.level
        self.damage = self.level+1

        self.speed = 1
        self.flying = True

    def update(self):

        do_hit = []

        for i in self.game.build_tower_group.objects:
            if self.rect.inflate(6,6).colliderect(i.rect.inflate(6,6)):
                i.kill()

        for i in self.game.bot_group.objects:
            if self.rect.inflate(6,6).colliderect(i.rect.inflate(6,6)):
                do_hit.append(i)

        if do_hit:
            self.attack_timer += 1
            if self.attack_timer >= 25:
                self.attack_timer = 0
                for i in do_hit:
                    i.hit(self.damage)
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
            if self.netted:
                self.netted_count += 1
                if self.netted_count >= self.netted_duration:
                    self.netted = False
                    self.netted_count = 0
                return # we can't move, wah!
            if self.stuck:
                self.stuck = False
                return #assume this is set each frame by traps ;)
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
                    self.animate("walk", int(self.ani_speed/self.speed), 1)
                    self.angle = 0
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

class Explosion(Animation):
    
    def __init__(self, game, pos, big=False):
        self.groups = [game.main_group]
        Animation.__init__(self, game)
        if big:
            self.imgs = [pygame.transform.scale(data.image("data/exp-%d.png" % i), (50,50)) for i in range(1, 5)]
        else:
            self.imgs = [data.image("data/exp-%d.png" % i) for i in range(1, 5)]
        self.image = self.imgs[0]
        self.add_animation("anim", self.imgs)
        self.rect = self.image.get_rect(center = pos)
        self.animate("anim", 5, 1)
    
    def on_animation_end(self):
        self.kill()

class Fadeout(GameObject):
    
    def __init__(self, game, pos, image):
        self.groups = [game.main_group]
        GameObject.__init__(self, game)
        self.image = pygame.Surface(image.get_size())
        self.image.fill((255, 53, 255))
        self.image.set_colorkey((255, 53, 255), RLEACCEL)
        self.image.blit(image, (0, 0))
        self.rect = self.image.get_rect(center = pos)
        self.alpha = 255

    def render(self):
        self.alpha -= 5
        if self.alpha <= 0:
            self.kill()
        self.image.set_alpha(self.alpha)
        self.game.screen.blit(self.image, self.rect)

class DamageNote(GameObject):
    def __init__(self, game, pos, color, amount, _big=False):
        self.groups = [game.damage_notes_group]
        GameObject.__init__(self, game)

        if _big:
            size = 20
        else:
            size = 12

        font = data.font("data/font.ttf", size, True)

        amount = str(amount)
        if _big:
            amount="+"+amount
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

        self.pos = pos

        left = 0
        for i in chars:
            my_surf.blit(i, (left, 0))
            left += i.get_width()

        self.image = my_surf
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.age = 0
        if _big:
            self.lifespan = 75
            self.waft_dir = 0
            self.vert_dir = 3
        else:
            self.lifespan = 50
            self.waft_dir = random.choice((-1,1))*.5
            self.vert_dir = 1
        self.move_counter = 0

    def update(self):
        self.age += 1
        if self.age > self.lifespan:
            self.kill()

        self.move_counter += 1
        if self.move_counter >= 3:
            self.move_counter = 0
            x, y = self.pos
            x += self.waft_dir
            y -= self.vert_dir
            self.pos = x, y
            self.rect.center = self.pos


class FloatingMessage(GameObject):
    def __init__(self, game, pos, text):
        self.groups = [game.damage_notes_group]
        GameObject.__init__(self, game)

        size = 32

        font = data.font("data/font.ttf", size, True)

        my_surf = data.image("data/floating_message.png").copy()
        x = font.render(text, 1, (0,0,0))
        r = x.get_rect(center=my_surf.get_rect().center)
        my_surf.blit(x, r)

        self.image = my_surf
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.pos = pos

        self.age = 0
        self.lifespan = 75
        self.waft_dir = 0
        self.vert_dir = 3
        self.move_counter = 0

    def update(self):
        self.age += 1
        if self.age > self.lifespan:
            self.kill()

        self.move_counter += 1
        if self.move_counter >= 3:
            self.move_counter = 0
            x, y = self.pos
            x += self.waft_dir
            y -= self.vert_dir
            self.pos = x, y
            self.rect.center = self.pos


class SpikeTrap(GameObject):
    money_cost = 10
    scrap_cost = 20
    ui_icon = "data/spikes.png"
    diesound = 'boom1.ogg'

    base_usage_count = 25
    base_damage = 3
    special = None
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

        self.level = 1

        self.times = 0
        self.max_times = int(self.base_usage_count)

        #set blocking!
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(pos), 1)

        self.attack_timer = 0
        self.damage = int(self.base_damage)
        for i in xrange(self.game.hero.trap_level-1):
            self.upgrade_level()

    def upgrade_level(self):
        self.damage += int(self.level)
        self.max_times = int(self.max_times * 1.5)
        self.level += 1

    def kill(self):
        GameObject.kill(self)
        self.game.audio.sounds[self.diesound].play()
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(self.rect.topleft), 0)

    def update(self):
        for i in self.game.insect_group.objects:
            if not i.flying:
                if self.rect.colliderect(i.rect):
                    self.attack_timer += 1
                    if self.attack_timer >= 25:
                        self.attack_timer = 0
                        i.hit(self.damage)
                        self.times += 1
                        if self.times >= self.max_times:
                            self.kill()
                            return

class CageTrap(GameObject):
    money_cost = 25
    scrap_cost = 50
    ui_icon = "data/cage.png"
    diesound = 'boom1.ogg'

    base_usage_count = 200
    base_damage = 0
    special = "traps"
    def __init__(self, game, pos):
        self.groups = game.main_group, game.trap_group
        GameObject.__init__(self, game)

        self.image = data.image("data/cage.png")

        self.rect = self.image.get_rect()
        x, y = pos
        x += 10
        y += 20 #so we can put it at center...
        self.rect.midbottom = x, y

        self.game.money -= self.money_cost
        self.game.scraps -= self.scrap_cost
        self.game.update_money()

        self.damage = 0

        self.level = 1

        self.times = 0
        self.max_times = int(self.base_usage_count)

        #set blocking!
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(pos), 1)

        for i in xrange(self.game.hero.trap_level-1):
            self.upgrade_level()

    def upgrade_level(self):
        self.max_times = 200 * self.level
        self.level += 1

    def kill(self):
        GameObject.kill(self)
        self.game.audio.sounds[self.diesound].play()
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(self.rect.topleft), 0)

    def update(self):
        for i in self.game.insect_group.objects:
            if self.rect.inflate(-10,-10).colliderect(i.rect.inflate(-5,-5)):
                i.rect.center = self.rect.center
                i.stuck = True
                if i.immune:
                    i.immune = False
                self.times += 1
                if self.times >= self.max_times:
                    self.kill()
                    return

class BombTrap(GameObject):
    money_cost = 75
    scrap_cost = 65
    ui_icon = "data/bomb.png"
    diesound = 'boom1.ogg'

    base_usage_count = 1
    base_damage = 50
    special = "splash damage"
    def __init__(self, game, pos):
        self.groups = game.main_group, game.trap_group
        GameObject.__init__(self, game)

        self.image = data.image("data/bomb.png")

        self.rect = self.image.get_rect()
        x, y = pos
        x += 10
        y += 20 #so we can put it at center...
        self.rect.midbottom = x, y

        self.game.money -= self.money_cost
        self.game.scraps -= self.scrap_cost
        self.game.update_money()

        self.damage = int(self.base_damage)

        self.level = 1

        self.times = 0
        self.max_times = int(self.base_usage_count)

        #set blocking!
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(pos), 1)

        for i in xrange(self.game.hero.trap_level-1):
            self.upgrade_level()

    def upgrade_level(self):
        self.damage += 50 + self.level
        self.level += 1

    def kill(self):
        GameObject.kill(self)
        self.game.audio.sounds[self.diesound].play()
        self.game.map_grid.set(self.game.map_grid.screen_to_grid(self.rect.topleft), 0)

    def update(self):
        targets = []
        shoot = False
        for i in self.game.insect_group.objects:
            if misc.distance(self.rect.center, i.rect.center) < 100:
                targets.append(i)
            if misc.distance(self.rect.center, i.rect.center) <= 22:
                shoot = True

        if shoot:
            for i in targets:
                i.hit(self.damage)
                Explosion(self.game, i.rect.center)
            self.kill()
            Explosion(self.game, self.rect.center, big=True)


class BattleBot(Worker):
    time_cost = 75
    money_cost = 35
    scrap_cost = 35
    ui_icon = "data/warrior-1.png"

    base_speed = 3
    base_hp = 35
    base_damage = 10
    special = None
    def __init__(self, game):
        self.groups = game.main_group, game.bot_group
        Animation.__init__(self, game)
        self.walk_images = [
            data.image("data/warrior-1.png"),
            data.image("data/warrior-2.png"),
            ]
        self.stand_images = [
            data.image("data/warrior-1.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.add_animation("stand", self.stand_images)

        self.name = "Warrior"

        self.level = 1

        self.rect = self.image.get_rect()
        self.rect.center = self.game.hero.rect.topleft

        self.target = None
        self.move_timer = 0
        self.have_scraps = False
        self.damage = int(self.base_damage)
        self.max_hp = int(self.base_hp)
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.attack_timer = 0
        self.speed = int(self.base_speed)

        for i in xrange(self.game.hero.warrior_level-1):
            self.upgrade_level()

        self.path = None

        self.count = 0

    def upgrade_level(self):
        self.max_hp += 15 + self.level
        self.hp += 15 + self.level
        self.damage += 3 * self.level
        self.level += 1

    def update(self):
        #Battling first, because we gotta stop movement for that!
        do_hit = []

        if self.rect.colliderect(self.game.hive):
            self.game.hive.hit(1)
            self.kill()

        for i in self.game.insect_group.objects:
            if not (i.immune or i.flying):
                if self.rect.inflate(6,6).colliderect(i.rect.inflate(6,6)):
                    do_hit.append(i)

        if do_hit:
            self.attack_timer += 1
            if self.attack_timer >= 25:
                self.attack_timer = 0
                for i in do_hit:
                    i.hit(self.damage)
            return #we can't move anymore ;)
        else:
            self.attack_timer = 0

        if not self.target:
            self.target = self.game.hive

            self.path = self.game.map_grid.calculate_path(self.game.map_grid.screen_to_grid(self.rect.center),
                                self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)

        old_target = self.target
        diso = None
        for i in self.game.insect_group.objects:
            if not (i.immune or i.flying):
                x = misc.distance(self.rect.center, i.rect.center)
                if x < 125:
                    if not diso:
                        diso = (i, x)
                        continue
                    if x < diso[1]:
                        diso = (i, x)

        if diso:
            if not (diso[0] == old_target and self.path):
                self.target = diso[0]
                if not self.path:
                    start = self.game.map_grid.screen_to_grid(self.rect.center)
                else:
                    start = self.path[0]
                self.path = self.game.map_grid.calculate_path(start,
                                self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)
                self.count = 0
            else:
                self.count += 1
                if self.count >= 80:
                    if not self.path:
                        start = self.game.map_grid.screen_to_grid(self.rect.center)
                    else:
                        start = self.path[0]
                    self.path = self.game.map_grid.calculate_path(start,
                                    self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)
                    self.count = 0
        else:
            if not self.target == self.game.hive:
                self.target = self.game.hive

                self.path = self.game.map_grid.calculate_path(self.game.map_grid.screen_to_grid(self.rect.center),
                                    self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)

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
                if self.move_timer >= self.speed:
                    self.animate("walk", int(15/self.speed), 1)
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

class TrapperBot(BattleBot):
    time_cost = 75
    money_cost = 40
    scrap_cost = 55
    ui_icon = "data/trapper-1.png"

    base_speed = 2
    base_hp = 20
    base_damage = 8
    base_range=110
    base_net_duration=175
    special = "traps"
    def __init__(self, game):

        self.damage = int(self.base_damage)
        self.max_hp = int(self.base_hp)
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.attack_timer = 0
        self.speed = int(self.base_speed)
        self.throw_net_counter = 0
        self.throw_net_wait = 50
        self.range = int(self.base_range)
        self.net_duration=int(self.base_net_duration)

        self.name = "Trapper"

        BattleBot.__init__(self, game)

        self.walk_images = [
            data.image("data/trapper-1.png"),
            data.image("data/trapper-2.png"),
            ]
        self.stand_images = [
            data.image("data/trapper-1.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.add_animation("stand", self.stand_images)

        self.rect = self.image.get_rect()
        self.rect.center = self.game.hero.rect.topleft

    def upgrade_level(self):
        self.max_hp += 12
        self.hp += 12
        self.damage += 3 + int(self.level/2)
        self.range += 8
        self.net_duration += 25
        self.level += 1

    def update(self):
        BattleBot.update(self)

        target = None
        for i in self.game.insect_group.objects:
            if not (i.immune or i.netted):
                x = misc.distance(self.rect.center, i.rect.center)
                if x <= self.range:
                    if not target:
                        target = (i, x)
                    elif x < target[1]:
                        target = (i, x)

        if target:
            self.throw_net_counter += 1
            if self.throw_net_counter >= self.throw_net_wait:
                self.throw_net_counter = 0
                Net(self.game, self.rect.center, self.range+20, target[0], int(self.damage*.65), self.net_duration)

class GuardBot(BattleBot):
    time_cost = 100
    money_cost = 75
    scrap_cost = 45
    ui_icon = "data/guard-1.png"

    base_speed = 4
    base_hp = 50
    base_damage = 7
    special = "guard workers"
    def __init__(self, game):

        self.damage = int(self.base_damage)
        self.max_hp = int(self.base_hp)
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.attack_timer = 0
        self.speed = int(self.base_speed)

        BattleBot.__init__(self, game)

        self.walk_images = [
            data.image("data/guard-1.png"),
            data.image("data/guard-2.png"),
            ]
        self.stand_images = [
            data.image("data/guard-1.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.add_animation("stand", self.stand_images)

        self.name = "Guard"

        self.rect = self.image.get_rect()
        self.rect.center = self.game.hero.rect.topleft

    def upgrade_level(self):
        self.max_hp += 20 + self.level*2
        self.hp += 20 + self.level*2
        self.damage += 5 + self.level
        self.level += 1

    def update(self):
        #Battling first, because we gotta stop movement for that!
        do_hit = []

        if self.rect.colliderect(self.game.hive):
            self.game.hive.hit(1)
            self.kill()

        for i in self.game.insect_group.objects:
            if not (i.immune or i.flying):
                if self.rect.inflate(6,6).colliderect(i.rect.inflate(6,6)):
                    do_hit.append(i)

        if do_hit:
            self.attack_timer += 1
            if self.attack_timer >= 25:
                self.attack_timer = 0
                for i in do_hit:
                    i.hit(self.damage)
            return #we can't move anymore ;)
        else:
            self.attack_timer = 0

        old_target = self.target
        diso = None
        for i in self.game.bot_group.objects:
            if i.name == "Worker":
                if not diso:
                    diso = (i, misc.distance(self.rect.center, i.rect.center))
                    continue
                x = misc.distance(self.rect.center, i.rect.center)
                if x < diso[1]:
                    diso = (i, x)

        for i in self.game.insect_group.objects:
            if not (i.immune or i.flying):
                if not diso:
                    diso = (i, misc.distance(self.rect.center, i.rect.center))
                    continue
                x = misc.distance(self.rect.center, i.rect.center)
                if x < diso[1]*3:
                    diso = (i, x)

        if diso:
            if (not diso[0] == old_target) or (not self.path):
                self.target = diso[0]
                if not self.path:
                    start = self.game.map_grid.screen_to_grid(self.rect.center)
                else:
                    start = self.path[0]
                self.path = self.game.map_grid.calculate_path(start,
                                self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)
        else:
            #what?!?! this really shouldn't happen...
            if (not self.target == self.game.hive) or (not self.path):
                self.target = self.game.hive
                if not self.path:
                    start = self.game.map_grid.screen_to_grid(self.rect.center)
                else:
                    start = self.path[0]
                self.path = self.game.map_grid.calculate_path(start,
                                self.game.map_grid.screen_to_grid(self.target.rect.center), False, False)

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
                if self.move_timer >= self.speed:
                    self.animate("walk", int(15/self.speed), 1)
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

class PoisonSpray(GameObject):
    def __init__(self, game, pos):
        self.groups = game.main_group, game.special_group
        GameObject.__init__(self, game)

        self.image = data.image("data/green_cloud.png")
        self.rot = 0
        self.add_rot = random.choice((-1,1))
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        for i in self.game.insect_group.objects:
            if self.rect.colliderect(i.rect):
                i.hit(99999999)

        self.rect.move_ip(-1,0)
        if self.rect.right <= 0:
            self.kill()

        self.rot += self.add_rot

    def render(self):
        _image = self.image
        self.image = pygame.transform.rotate(self.image, self.rot)
        self.rect = self.image.get_rect(center=self.rect.center)
        GameObject.render(self)
        self.image = _image
        self.rect = self.image.get_rect(center=self.rect.center)


class Dust(GameObject):
    def __init__(self, game, pos):
        self.groups = game.main_group, game.special_group
        GameObject.__init__(self, game)

        self.image = data.image("data/grey_cloud.png")
        self.rot = 0
        self.add_rot = random.choice((-1,1))
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.age = 0

    def update(self):

        self.rect.move_ip(random.randint(-2,2), -1)

        self.age += 1
        if self.age >= 150:
            self.kill()

        self.rot += self.add_rot

    def render(self):
        _image = self.image
        self.image = pygame.transform.rotate(self.image, self.rot)
        self.rect = self.image.get_rect(center=self.rect.center)
        GameObject.render(self)
        self.image = _image
        self.rect = self.image.get_rect(center=self.rect.center)

        
class SprayCanSpecial(GameObject):
    def __init__(self, game):
        self.groups = game.main_group, game.special_group
        GameObject.__init__(self, game)

        self.image = data.image("data/spray_can.png")
        self.rect = self.image.get_rect()
        self.rect.topright = (800,0)

        self.spray_count = 5

    def update(self):
        self.spray_count += 1
        if self.spray_count >= 5:
            PoisonSpray(self.game, self.rect.topleft)
            PoisonSpray(self.game, (self.rect.left-40, self.rect.top))
            PoisonSpray(self.game, (self.rect.left-80, self.rect.top))
            self.spray_count = 0

        self.rect.move_ip(0,4)
        if self.rect.top > 500:
            self.kill()


class BroomSpecial(GameObject):
    def __init__(self, game):
        self.groups = game.main_group, game.special_group
        GameObject.__init__(self, game)

        self.image = data.image("data/broom.png")
        self.rect = self.image.get_rect()
        self.rect.bottomright = self.game.hero.rect.topleft

        self.d = (-10,20) #bottomleft first!

        self.throw_dust_counter = 0
        self.hit_hive = False

    def update(self):
        self.rect.move_ip(self.d)

        r = pygame.Rect(0,0,self.rect.width, self.rect.width)
        r.midbottom = self.rect.midbottom
        if r.centery >= 475 or r.centerx <= 25:
            self.d = (10,-20)
        elif r.centerx >= 775 or r.centery <= 25:
            self.d = (-10,20)
            self.rect.move_ip(-45,0)

        self.throw_dust_counter += 1
        if self.throw_dust_counter >= 5:
            Dust(self.game, r.midbottom)
            self.throw_dust_counter = 0

        for i in self.game.insect_group.objects + self.game.bot_group.objects:
            if r.colliderect(i.rect):
                i.hit(99999999)

        if not self.hit_hive:
            if r.colliderect(self.game.hive.rect):
                self.game.hive.hit(random.randint(2,4))
                self.hit_hive = True

        if self.rect.left <= -100 and self.rect.top <= -100:
            self.kill()

class MowerSpecial(GameObject):
    def __init__(self, game):
        self.groups = game.main_group, game.special_group
        GameObject.__init__(self, game)

        self.image = pygame.transform.rotate(data.image("data/mower.png"), 90)
        self.rect = self.image.get_rect()
        self.rect.topright = 800,0

        self.d = -1

        self.throw_dust_counter = 0
        self.hit_hive = False

    def update(self):
        self.rect.move_ip(self.d, 0)

        self.rect.move_ip(self.d*10, 0)
        if self.rect.right < 0 and self.d == -1:
            self.d = 1
            self.rect.move_ip(0, 100)
            self.image = pygame.transform.flip(self.image, 1, 0)
        elif self.rect.left > 800 and self.d == 1:
            self.d = -1
            self.rect.move_ip(0, 100)
            self.image = pygame.transform.flip(self.image, 1, 0)

        self.throw_dust_counter += 1
        if self.throw_dust_counter >= 10:
            for i in (self.rect.topleft, self.rect.topright,
                      self.rect.midtop, self.rect.midright,
                      self.rect.bottomright, self.rect.midbottom,
                      self.rect.midleft):
                Dust(self.game, i)
                self.throw_dust_counter = 0

        for i in self.game.insect_group.objects + self.game.bot_group.objects +\
            self.game.tower_group.objects + self.game.build_tower_group.objects:
            if self.rect.colliderect(i.rect):
                self.game.scraps += 50
                i.hit(99999999)

        if not self.hit_hive:
            if self.rect.colliderect(self.game.hive.rect):
                self.game.hive.hit(random.randint(4,8))
                self.hit_hive = True

        if self.rect.centery > 500:
            self.kill()
