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
        self.rect.bottomright = (842,525) #bottom 100 is the ui bar!

        self.worker_level = 1
        self.warrior_level = 1
        self.trap_level = 1

        self.tech_worker_upgrade_cost = 75
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

        self.counter = 0
        self.num_spawned = 0
        self.wait_for = 20
        self.fast = False

        self.flying = False
        self.immune = False

        self.choice_list = [Ant]*10 + [Beetle]*8 + [Worm]*6 + [Wasp]*4

    def update(self):
        self.counter += 1
        if self.fast:
            num = 65
            num -= self.level * 5
            if num < 40:
                num = 40
        else:
            num = 300
            num -= self.level * 15
            if num < 75:
                num = 75
        if self.counter >= num:
            if not random.randrange(3):
                self.fast = True
            else:
                self.fast = False
            self.counter = 0
            random.choice(self.choice_list)(self.game, self.level)
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
    base_attack = 5
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

        self.upgrade_types = [MissileTower]

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
    base_attack = 13
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

        self.upgrade_types = []

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
    base_hp = 5
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
        self.max_hp += 5
        self.hp += 5
        self.damage += 1
        self.speed -= 1
        if self.speed < 1:
            self.speed = 1
        self.level += 1
        self.scrap_load += 10

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
                self.have_scraps = False
                self.game.scraps += self.scrap_load
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

        self.max_hp = 15 * self.level
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.worth = 5 * self.level
        self.damage = 1 * self.level

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
            data.image("data/beetle-1.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.rect = self.image.get_rect()
        self.rect.center = self.game.hive.rect.center

        self.max_hp = 35 * self.level
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.worth = 10 * self.level
        self.damage = 3 * self.level

        self.speed = 3

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

        self.max_hp = 30 * self.level
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.worth = 20 * self.level
        self.damage = 4 * self.level

        self.speed = 3
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
            self.speed = 3
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
            data.image("data/wasp-1.png"),
            ]
        self.image = self.walk_images[0]
        self.add_animation("walk", self.walk_images)
        self.rect = self.image.get_rect()
        self.rect.center = self.game.hive.rect.center

        self.max_hp = 10 + 5*(self.level-1)
        self.hp = int(self.max_hp)
        self.show_hp_bar = True
        self.worth = 25 * self.level
        self.damage = 2 * self.level

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
        self.damage += int(self.level/2)
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
        self.max_times = int(self.max_times * 1.5)
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
    money_cost = 125
    scrap_cost = 75
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
        self.damage += 30 + self.level
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
    base_hp = 30
    base_damage = 8
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
        self.max_hp += 8 + self.level
        self.hp += 8 + self.level
        self.damage += 2 * self.level
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
        for i in self.game.insect_group.objects+self.game.hive_group.objects:
            if not (i.immune or i.flying):
                if not diso:
                    diso = (i, misc.distance(self.rect.center, i.rect.center))
                    continue
                x = misc.distance(self.rect.center, i.rect.center)
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
            #what?!?! this really shouldn't happen...
            self.target = self.game.hive
            if not self.path:
                start = self.game.map_grid.screen_to_grid(self.rect.center)
            else:
                start = self.path[0]
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
    base_hp = 25
    base_damage = 3
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
        self.max_hp += 4
        self.hp += 4
        self.damage += 1
        self.range += 5
        self.net_duration += 2
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
                Net(self.game, self.rect.center, self.range+20, target[0], int(self.damage*.35), self.net_duration)

class GuardBot(BattleBot):
    time_cost = 100
    money_cost = 75
    scrap_cost = 45
    ui_icon = "data/guard-1.png"

    base_speed = 4
    base_hp = 40
    base_damage = 6
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
        self.max_hp += 10 + self.level
        self.hp += 10 + self.level
        self.damage += 2 + int(self.level*.5)
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

        print self.target, bool(self.path)

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

        
