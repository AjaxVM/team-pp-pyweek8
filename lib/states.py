import pygame
from pygame.locals import *

import random, time

import data, ui, objects, map_grid, sound

class GameState(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.children = {}

        self._use_child = None

    def use_child(self, name):
        if name in self.children:
            self._use_child = self.children[name](self)
        else:
            self.use_child(None)

    def goback(self):
        if self.parent:
            self.parent.use_child(None)

    def goback_to_root(self):
        if self.parent:
            self.parent.use_child(None)
            self.parent.goback_to_root()

    def get_root(self):
        if self.parent:
            return self.parent.get_root()
        return self

    def do_update(self):
        if self._use_child:
            self._use_child.do_update()
            return
        self.update()

    def update(self):
        pass

class Menu(GameState):
    def __init__(self, parent):
        GameState.__init__(self, parent)

        self.app = ui.App(self.get_root().screen)
        ui.Label(self.app, "Game Name!", text_color=(255,255,255), pos=(100,25), anchor="topleft")

        ui.Button(self.app, "Play - easy", text_color=(0,0,0), pos=(150,100),
                  callback=lambda: self.parent.use_child("game-easy"))
        ui.Button(self.app, "Play - medium", text_color=(0,0,0), pos=(325,100),
                  callback=lambda: self.parent.use_child("game-medium"))
        ui.Button(self.app, "Play - hard", text_color=(0,0,0), pos=(525,100),
                  callback=lambda: self.parent.use_child("game-hard"))

        ui.Button(self.app, "Quit", text_color=(0,0,0), pos=(100,150),
                  callback=self._kill)

        self.bg = data.image("data/background1.png").copy()
        for i in xrange(100):
            self.bg.blit(data.image("data/worker-1.png"), (random.randint(0,800), random.randint(200,300)))
            self.bg.blit(data.image("data/tower-base.png"), (random.randint(0,800), random.randint(200,300)))

        n = self.bg.copy()
        n.fill((255,228,196,65))
        self.bg.blit(n, (0,0))

        for i in xrange(300):
            i = random.choice(("ant-1.png", "beetle-1.png", "worm-1.png", "wasp-1.png"))
            self.bg.blit(data.image("data/"+i), (random.randint(0,800), random.randint(350,600)))

        self.killed = False

    def _kill(self):
        self.get_root().shutdown()
        self.killed = True

    def update(self):
        for event in pygame.event.get():
            if self.app.update(event):
                if self.killed:
                    return
                continue
            if event.type == QUIT:
                self.get_root().shutdown()
                return

        self.get_root().screen.blit(self.bg, (0,0))
        self.app.render()
        pygame.display.flip()

class YouWonMenu(GameState):
    def __init__(self, parent):
        GameState.__init__(self, parent)

        self.app = ui.App(self.get_root().screen)
        ui.Label(self.app, "You won, congratulations!", text_color=(75,75,255), pos=(0,0), anchor="topleft")

        ui.Button(self.app, "Menu", text_color=(0,0,0), pos=(50,150),
                  callback=lambda: self.parent.use_child("menu"))

        self.bg = data.image("data/background1.png").copy()
        for i in xrange(100):
            self.bg.blit(data.image("data/worker-1.png"), (random.randint(0,800), random.randint(200,600)))
            self.bg.blit(data.image("data/tower-base.png"), (random.randint(0,800), random.randint(200,600)))

        n = self.bg.copy()
        n.fill((0,0,0,75))
        self.bg.blit(n, (0,0))

    def update(self):
        for event in pygame.event.get():
            if self.app.update(event):
                continue
            if event.type == QUIT:
                self.get_root().shutdown()
                return

        self.get_root().screen.blit(self.bg, (0,0))
        self.app.render()
        pygame.display.flip()

class YouLostMenu(GameState):
    def __init__(self, parent):
        GameState.__init__(self, parent)

        self.app = ui.App(self.get_root().screen)
        ui.Label(self.app, 'You lost...\noh well, like they say:\n    Try, try again :)', text_color=(255,0,0), pos=(0,0), anchor="topleft")

        ui.Button(self.app, "Menu", text_color=(0,0,0), pos=(50,150),
                  callback=lambda: self.parent.use_child("menu"))

        self.bg = data.image("data/background1.png").copy()
        for i in xrange(500):
            i = random.choice(("ant-1.png", "beetle-1.png", "worm-1.png", "wasp-1.png"))
            self.bg.blit(data.image("data/"+i), (random.randint(0,800), random.randint(350,600)))
        n = self.bg.copy()
        n.fill((0,0,0,75))
        self.bg.blit(n, (0,0))

    def update(self):
        for event in pygame.event.get():
            if self.app.update(event):
                continue
            if event.type == QUIT:
                self.get_root().shutdown()
                return

        self.get_root().screen.blit(self.bg, (0,0))
        self.app.render()
        pygame.display.flip()

class Game(GameState):
    def __init__(self, parent, mode="easy"):
        GameState.__init__(self, parent)

        self.screen = self.get_root().screen

        self.audio = sound.SoundManager('data')
        self.audio.sounds['ants_on_my_lawn.ogg'].set_volume(0.6)
        self.audio.sounds['ants_on_my_lawn.ogg'].play(loops=-1)

        self.background = data.image("data/background1.png")
        self.ui_background = data.image("data/porch_ui.png")

        self.main_group = objects.GameGroup()
        self.flying_group = objects.GameGroup()
        self.hero_group = objects.GameGroup()
        self.hive_group = objects.GameGroup()
        self.build_tower_group = objects.GameGroup()
        self.bot_group = objects.GameGroup()
        self.tower_group = objects.GameGroup()
        self.insect_group = objects.GameGroup()
        self.scraps_group = objects.GameGroup()
        self.blocking_group = objects.GameGroup()
        self.bullet_group = objects.GameGroup()
        self.trap_group = objects.GameGroup()
        self.special_group = objects.GameGroup()

        self.damage_notes_group = objects.GameGroup()

        if mode == "easy":
            level = 1
            scraps = 10
            self.money = 500
            self.scraps = 500
        elif mode=="medium":
            level = 4
            scraps = 6
            self.money = 425
            self.scraps = 425
        else:
            level = 7
            scraps = 3
            self.money = 350
            self.scraps = 350
        self.hive = objects.Hive(self)
        self.hive.level = level
        self.hive.max_hp += level
        self.hive.hp += level



        self.kills = 0

        self.font = data.font("data/font.ttf", 24)

        self.money_ui = self.font.render("money: %s"%self.money, 1, (255,255,255))
        self.money_ui_pos = (0, 530)
        self.scraps_ui = self.font.render("scraps: %s"%self.scraps, 1, (255,255,255))
        self.scraps_ui_pos = (0, 550)
        self.kills_ui = self.font.render("kills: %s"%self.kills, 1, (255,255,255))
        self.kills_ui_pos = (0, 570)

        self.map_grid = map_grid.MapGrid(self)

        self.hero = objects.Hero(self)

        self.map_grid.make_random(random.randint(40, 60), scraps)

        self.build_active = None
        self.building = None
        self.build_overlay = None

        self.selected_object = None
        self.selected_ui = None

        #UI here, so it has access to all the data above!
        self.app = ui.App(self.screen)
        ui.Button(self.app, "Quit Game", pos=(0,500), callback=self.goback,
                  status_message="Quit game...?")

        #Make build objects gui
        #TODO: implement multiple kinds of warriors/traps!!!

        l = ui.Label(self.app, "Basic", pos=(180, 500))
        ui.LinesGroup(self.app, l)
        b = ui.Button(self.app, image=objects.TowerBase.ui_icon, pos=l.rect.inflate(0,2).bottomleft,
                  callback=self.build_tower,
                      status_message=("Build a Tower\ncost:\n  money: %s\n  scraps: %s"+\
                                      "\n----------\nattack: %s\nrange: %s\nspeed: %s")%(objects.TowerBase.money_cost,
                                                                                         objects.TowerBase.scrap_cost,
                                                                                         objects.TowerBase.base_attack,
                                                                                         objects.TowerBase.base_range,
                                                                                         objects.TowerBase.base_shoot_speed),
                      anchor="topleft")
        
        b = ui.Button(self.app, image=objects.Worker.ui_icon, pos=b.rect.inflate(8,0).topright,
                  callback=self.build_worker,
                      status_message=("Build a Worker\ncost:\n  money: %s\n  scraps: %s"+\
                                      "\n----------\nattack: %s\nhp: %s\nspeed: %s")%(objects.Worker.money_cost,
                                                                                      objects.Worker.scrap_cost,
                                                                                      objects.Worker.base_damage,
                                                                                      objects.Worker.base_hp,
                                                                                      objects.Worker.base_speed),
                      anchor="topleft")
        self.build_worker_button = b

        l = ui.Label(self.app, "Warriors ", pos=(250, 500))
        ui.LinesGroup(self.app, l)
        b = ui.Button(self.app, image=objects.BattleBot.ui_icon, pos=l.rect.inflate(0,2).bottomleft,
                  callback=self.build_warrior,
                      status_message=("Build a Warrior\ncost:\n  money: %s\n  scraps: %s"+\
                                      "\n----------\nattack: %s\nhp: %s\nspeed: %s\nspecial: %s")%(objects.BattleBot.money_cost,
                                                                                      objects.BattleBot.scrap_cost,
                                                                                      objects.BattleBot.base_damage,
                                                                                      objects.BattleBot.base_hp,
                                                                                      objects.BattleBot.base_speed,
                                                                                                   objects.BattleBot.special),
                      anchor="topleft")
        self.build_warrior_button = b

        b = ui.Button(self.app, image=objects.TrapperBot.ui_icon, pos=b.rect.inflate(8,0).topright,
                  callback=self.build_trapper,
                      status_message=("Build a Trapper\ncost:\n  money: %s\n  scraps: %s"+\
                                      "\n----------\nattack: %s\nhp: %s\nspeed: %s\nspecial: %s")%(objects.TrapperBot.money_cost,
                                                                                      objects.TrapperBot.scrap_cost,
                                                                                      objects.TrapperBot.base_damage,
                                                                                      objects.TrapperBot.base_hp,
                                                                                      objects.TrapperBot.base_speed,
                                                                                                   objects.TrapperBot.special),
                      anchor="topleft")
        self.build_trapper_button = b

        b = ui.Button(self.app, image=objects.GuardBot.ui_icon, pos=b.rect.inflate(8,0).topright,
                  callback=self.build_guard,
                      status_message=("Build a Guard\ncost:\n  money: %s\n  scraps: %s"+\
                                      "\n----------\nattack: %s\nhp: %s\nspeed: %s\nspecial: %s")%(objects.GuardBot.money_cost,
                                                                                      objects.GuardBot.scrap_cost,
                                                                                      objects.GuardBot.base_damage,
                                                                                      objects.GuardBot.base_hp,
                                                                                      objects.GuardBot.base_speed,
                                                                                                   objects.GuardBot.special),
                      anchor="topleft")
        self.build_guard_button = b
        

        l = ui.Label(self.app, " Traps ", pos=(370, 500))
        ui.LinesGroup(self.app, l)
        b = ui.Button(self.app, image=objects.SpikeTrap.ui_icon, pos=l.rect.inflate(0,2).bottomleft,
                  callback=self.build_spike_trap,
                      status_message=("Build a Spike Trap\ncost:\n  money: %s\n  scraps: %s"+\
                                      "\n----------\nattack: %s\nuses: %s\nspecial: %s")%(objects.SpikeTrap.money_cost,
                                                                                      objects.SpikeTrap.scrap_cost,
                                                                                      objects.SpikeTrap.base_damage,
                                                                                      objects.SpikeTrap.base_usage_count,
                                                                                      objects.SpikeTrap.special),
                      anchor="topleft")
        self.build_spike_trap_button = b

        b = ui.Button(self.app, image=objects.CageTrap.ui_icon, pos=b.rect.inflate(8,0).topright,
                  callback=self.build_cage_trap,
                      status_message=("Build a Cage Trap\ncost:\n  money: %s\n  scraps: %s"+\
                                      "\n----------\nattack: %s\nuses: %s\nspecial: %s")%(objects.CageTrap.money_cost,
                                                                                      objects.CageTrap.scrap_cost,
                                                                                      objects.CageTrap.base_damage,
                                                                                      objects.CageTrap.base_usage_count,
                                                                                      objects.CageTrap.special),
                      anchor="topleft")
        self.build_cage_trap_button = b

        b = ui.Button(self.app, image=objects.BombTrap.ui_icon, pos=b.rect.inflate(8,0).topright,
                  callback=self.build_bomb_trap,
                      status_message=("Build a Bomb Trap\ncost:\n  money: %s\n  scraps: %s"+\
                                      "\n----------\nattack: %s\nuses: %s\nspecial: %s")%(objects.BombTrap.money_cost,
                                                                                      objects.BombTrap.scrap_cost,
                                                                                      objects.BombTrap.base_damage,
                                                                                      objects.BombTrap.base_usage_count,
                                                                                      objects.BombTrap.special),
                      anchor="topleft")
        self.build_bomb_trap_button = b


        #Ooh, techs, gotta love them!
        l = ui.Label(self.app, "  Techs   ", pos=(470, 500))
        ui.LinesGroup(self.app, l)
        i = pygame.Surface((30,30)).convert_alpha()
        i.fill((0,0,0,0))
        i.blit(data.image("data/worker-1.png"), (10,10))
        i.blit(data.image("data/arrow.png"), (0,0))
        self.upg_worker = ui.Button(self.app, image=i, pos=l.rect.inflate(0,2).bottomleft,
                      callback=self.upgrade_worker,
                      status_message="Upgrade Workers\ncurrent level: %s\ncost:\n  money: %s"%(self.hero.worker_level,
                                                                                     self.hero.tech_worker_upgrade_cost),
                      anchor="topleft")

        i = pygame.Surface((40,40)).convert_alpha()
        i.fill((0,0,0,0))
        i.blit(data.image("data/warrior-1.png"), (10,10))
        i.blit(data.image("data/arrow.png"), (0,0))
        self.upg_warrior = ui.Button(self.app, image=i, pos=self.upg_worker.rect.inflate(8,0).topright,
                      callback=self.upgrade_warrior,
                      status_message="Upgrade Warriors\ncurrent level: %s\ncost:\n  money: %s"%(self.hero.warrior_level,
                                                                                      self.hero.tech_warrior_upgrade_cost),
                      anchor="topleft")

        i = pygame.Surface((30,30)).convert_alpha()
        i.fill((0,0,0,0))
        i.blit(data.image("data/spikes.png"), (10,10))
        i.blit(data.image("data/arrow.png"), (0,0))
        self.upg_traps = ui.Button(self.app, image=i, pos=self.upg_warrior.rect.inflate(8,0).topright,
                      callback=self.upgrade_traps,
                      status_message="Upgrade Traps\ncurrent level: %s\ncost:\n  money: %s"%(self.hero.trap_level,
                                                                                   self.hero.tech_trap_upgrade_cost),
                      anchor="topleft")

        l = ui.Label(self.app, "Specials     ", pos=(610, 500))
        ui.LinesGroup(self.app, l)
        i = pygame.transform.scale(data.image("data/spray_can.png"), (35, 70))
        self.special_spray = ui.Button(self.app, image=i, pos=l.rect.inflate(0,2).bottomleft,
                      callback=self.use_spray_special,
                      status_message="Insects whooping on you?\nUse your spray can - kills all baddies!",
                      anchor="topleft")
        i = pygame.transform.scale(data.image("data/broom.png"), (35, 70))
        self.special_broom = ui.Button(self.app, image=i, pos=self.special_spray.rect.inflate(8,0).topright,
                      callback=self.use_broom_special,
                      status_message="Wah! They are too strong!\nCall down some major beatdown\nfrom your mom's broom!",
                      anchor="topleft")

        self.status_message = ui.PopupManager(self.app)
        self.status_message.set("Testing, 1,2,3")

        if mode == "easy":
            self.money += self.hero.tech_worker_upgrade_cost
            self.upgrade_worker()

    def upgrade_worker(self):
        if self.money >= self.hero.tech_worker_upgrade_cost:
            self.hero.worker_level += 1
            self.money -= self.hero.tech_worker_upgrade_cost
            self.hero.tech_worker_upgrade_cost = int(self.hero.tech_worker_upgrade_cost * 2.25)
            self.upg_worker.status_message = "Upgrade Workers\ncurrent level: %s\ncost: %s"%(self.hero.worker_level,
                                                                                             self.hero.tech_worker_upgrade_cost)

            for i in self.bot_group.objects:
                if isinstance(i, objects.Worker):
                    i.upgrade_level()
            self.update_money()

            test = objects.Worker(self)
            test.kill() #we don't want to leave this laying around O.o
            b = ("Build a Worker\ncost:\n  money: %s\n  scraps: %s"+\
                 "\n----------\nattack: %s\nhp: %s\nspeed: %s")%(test.money_cost,
                                                                 test.scrap_cost,
                                                                 test.damage,
                                                                 test.max_hp,
                                                                 test.speed)
            self.build_worker_button.status_message = b

    def use_spray_special(self):
        self.special_spray.kill() #because you can't do it twice!
        objects.SprayCanSpecial(self)

    def use_broom_special(self):
        self.special_broom.kill() #because you can't do it twice!
        objects.BroomSpecial(self)

    def upgrade_warrior(self):
        if self.money >= self.hero.tech_warrior_upgrade_cost:
            self.hero.warrior_level += 1
            self.money -= self.hero.tech_warrior_upgrade_cost
            self.hero.tech_warrior_upgrade_cost = int(self.hero.tech_warrior_upgrade_cost * 2.25)
            self.upg_warrior.status_message = "Upgrade Warriors\ncurrent level: %s\ncost: %s"%(self.hero.warrior_level,
                                                                                               self.hero.tech_warrior_upgrade_cost)
            for i in self.bot_group.objects:
                if not isinstance(i, objects.Worker): #must be a warrior!
                    i.upgrade_level()
            self.update_money()

            test = objects.BattleBot(self)
            test.kill() #we don't want to leave this laying around O.o
            b = ("Build a Warrior\ncost:\n  money: %s\n  scraps: %s"+\
                  "\n----------\nattack: %s\nhp: %s\nspeed: %s\nspecial: %s")%(test.money_cost,
                                                                  test.scrap_cost,
                                                                  test.damage,
                                                                  test.max_hp,
                                                                  test.speed,
                                                                   test.special)
            self.build_warrior_button.status_message = b


            test = objects.TrapperBot(self)
            test.kill() #we don't want to leave this laying around O.o
            b = ("Build a Trapper\ncost:\n  money: %s\n  scraps: %s"+\
                  "\n----------\nattack: %s\nhp: %s\nspeed: %s\nspecial: %s")%(test.money_cost,
                                                                  test.scrap_cost,
                                                                  test.damage,
                                                                  test.max_hp,
                                                                  test.speed,
                                                                   test.special)
            self.build_trapper_button.status_message = b


            test = objects.GuardBot(self)
            test.kill() #we don't want to leave this laying around O.o
            b = ("Build a Guard\ncost:\n  money: %s\n  scraps: %s"+\
                  "\n----------\nattack: %s\nhp: %s\nspeed: %s\nspecial: %s")%(test.money_cost,
                                                                  test.scrap_cost,
                                                                  test.damage,
                                                                  test.max_hp,
                                                                  test.speed,
                                                                   test.special)
            self.build_guard_button.status_message = b

    def upgrade_traps(self):
        if self.money >= self.hero.tech_trap_upgrade_cost:
            self.hero.trap_level += 1
            self.money -= self.hero.tech_trap_upgrade_cost
            self.hero.tech_trap_upgrade_cost = int(self.hero.tech_trap_upgrade_cost * 2.25)
            self.upg_traps.status_message = "Upgrade Traps\ncurrent level: %s\ncost: %s"%(self.hero.trap_level,
                                                                                          self.hero.tech_trap_upgrade_cost)
            for i in self.trap_group.objects:
                i.upgrade_level()
            self.update_money()

            test = objects.SpikeTrap(self, (0,0))
            test.kill() #we don't want to leave this laying around O.o
            b = ("Build a Spike Trap\ncost:\n  money: %s\n  scraps: %s"+\
                  "\n----------\nattack: %s\nuses: %s\nspecial: %s")%(test.money_cost,
                                                                  test.scrap_cost,
                                                                  test.damage,
                                                                  test.max_times,
                                                                  test.special)
            self.build_spike_trap_button.status_message = b

            test = objects.CageTrap(self, (0,0))
            test.kill() #we don't want to leave this laying around O.o
            b = ("Build a Cage Trap\ncost:\n  money: %s\n  scraps: %s"+\
                  "\n----------\nattack: %s\nuses: %s\nspecial: %s")%(test.money_cost,
                                                                  test.scrap_cost,
                                                                  test.damage,
                                                                  test.max_times,
                                                                  test.special)
            self.build_cage_trap_button.status_message = b

            test = objects.BombTrap(self, (0,0))
            test.kill() #we don't want to leave this laying around O.o
            b = ("Build a Bomb Trap\ncost:\n  money: %s\n  scraps: %s"+\
                  "\n----------\nattack: %s\nuses: %s\nspecial: %s")%(test.money_cost,
                                                                  test.scrap_cost,
                                                                  test.damage,
                                                                  test.max_times,
                                                                  test.special)
            self.build_bomb_trap_button.status_message = b

    def build_tower(self):
        if self.money >= objects.TowerBase.money_cost and self.scraps >= objects.TowerBase.scrap_cost:
            self.build_active = True
            self.building = objects.TowerBase

            bo = pygame.Surface((800,500)).convert_alpha()
            bo.fill((0,0,0,0))
            for x in xrange(self.map_grid.size[0]):
                for y in xrange(self.map_grid.size[1]):
                    if not self.map_grid.empty_around((x, y)):
                        pygame.draw.rect(bo, (200,0,0,125), (self.map_grid.grid_to_screen((x, y)), (20,20)))
            pygame.draw.rect(bo, (200,0,0,125), ((0,0), (11*20,11*20)))
            pygame.draw.rect(bo, (200,0,0,125), ((800-9*20,500-9*20), (9*20,9*20)))

            self.build_overlay = bo

    def update_money(self):
        self.money_ui = self.font.render("money: %s"%self.money, 1, (255,255,255))
        self.scraps_ui = self.font.render("scraps: %s"%self.scraps, 1, (255,255,255))
        self.kills_ui = self.font.render("kills: %s"%self.kills, 1, (255,255,255))

    def build_worker(self):
        if self.money >= objects.Worker.money_cost and self.scraps >= objects.Worker.scrap_cost and\
           len(self.bot_group.objects) < 20:
            self.hero.build_worker()

    def build_spike_trap(self):
        if self.money >= objects.SpikeTrap.money_cost and self.scraps >= objects.SpikeTrap.scrap_cost:
            self.building = objects.SpikeTrap
            self.build_active = True

            bo = pygame.Surface((800,500)).convert_alpha()
            bo.fill((0,0,0,0))
            for x in xrange(self.map_grid.size[0]):
                for y in xrange(self.map_grid.size[1]):
                    if not self.map_grid.is_open((x, y)):
                        pygame.draw.rect(bo, (200,0,0,125), (self.map_grid.grid_to_screen((x, y)), (20,20)))
            pygame.draw.rect(bo, (200,0,0,125), ((0,0), (11*20,11*20)))
            pygame.draw.rect(bo, (200,0,0,125), ((800-9*20,500-9*20), (9*20,9*20)))

            self.build_overlay = bo

    def build_cage_trap(self):
        if self.money >= objects.CageTrap.money_cost and self.scraps >= objects.CageTrap.scrap_cost:
            self.building = objects.CageTrap
            self.build_active = True

            bo = pygame.Surface((800,500)).convert_alpha()
            bo.fill((0,0,0,0))
            for x in xrange(self.map_grid.size[0]):
                for y in xrange(self.map_grid.size[1]):
                    if not self.map_grid.is_open((x, y)):
                        pygame.draw.rect(bo, (200,0,0,125), (self.map_grid.grid_to_screen((x, y)), (20,20)))
            pygame.draw.rect(bo, (200,0,0,125), ((0,0), (11*20,11*20)))
            pygame.draw.rect(bo, (200,0,0,125), ((800-9*20,500-9*20), (9*20,9*20)))

            self.build_overlay = bo

    def build_bomb_trap(self):
        if self.money >= objects.BombTrap.money_cost and self.scraps >= objects.BombTrap.scrap_cost:
            self.building = objects.BombTrap
            self.build_active = True

            bo = pygame.Surface((800,500)).convert_alpha()
            bo.fill((0,0,0,0))
            for x in xrange(self.map_grid.size[0]):
                for y in xrange(self.map_grid.size[1]):
                    if not self.map_grid.is_open((x, y)):
                        pygame.draw.rect(bo, (200,0,0,125), (self.map_grid.grid_to_screen((x, y)), (20,20)))
            pygame.draw.rect(bo, (200,0,0,125), ((0,0), (11*20,11*20)))
            pygame.draw.rect(bo, (200,0,0,125), ((800-9*20,500-9*20), (9*20,9*20)))

            self.build_overlay = bo

    def build_warrior(self):
        #TODO: replace with warrior type selection
        if self.money >= objects.BattleBot.money_cost and self.scraps >= objects.BattleBot.scrap_cost and\
           len(self.bot_group.objects) < 20:
            self.hero.build_warrior()

    def build_trapper(self):
        if self.money >= objects.TrapperBot.money_cost and self.scraps >= objects.TrapperBot.scrap_cost and\
           len(self.bot_group.objects) < 20:
            self.hero.build_trapper()

    def build_guard(self):
        if self.money >= objects.GuardBot.money_cost and self.scraps >= objects.GuardBot.scrap_cost and\
           len(self.bot_group.objects) < 20:
            self.hero.build_guard()

    def update(self):

        for event in pygame.event.get():
            if self.app.update(event):
                continue
            if event.type == QUIT:
                self.get_root().shutdown()
                return

            if event.type == MOUSEBUTTONDOWN:
                if self.selected_ui:
                    self.selected_ui.kill()
                    self.selected_ui = None
                if event.button == 1:
                    if self.selected_object:
                        self.selected_object.selected = False
                    if event.pos[1] <= 500: #this is for us!
                        grid = self.map_grid.screen_to_grid(event.pos)
                        if self.build_active:
                            if self.building == objects.TowerBase:
                                if self.map_grid.empty_around(grid):
                                    self.build_active = False
                                    objects.BuildTower(self, self.map_grid.grid_to_screen(grid))
                                    for i in self.bot_group.objects:
                                        i.reset_target()
                            elif self.building: #must be a trap of some sort!
                                if self.map_grid.is_open(grid):
                                    self.build_active = False
                                    self.building(self, self.map_grid.grid_to_screen(grid))
                        self.build_active = False
                        for i in self.tower_group.objects:
                            if i.rect.collidepoint(event.pos):
                                i.selected = True
                                self.selected_object = i
                                self.selected_ui = ui.TowerInfo(self.app, i)
                    else:
                        self.build_active = False
                        self.building = None
                if event.button == 3: #right
                    self.build_active = False
                    self.building = None

            if event.type == KEYDOWN:
                if event.key == K_s:
                    pygame.image.save(self.screen, "test.png")

        used = False
        for i in self.app.widgets:
            x = i.get_status()
            if x:
                self.status_message.set(x)
                used = True
                break
        if not used:
            self.status_message.set(None)

        self.hero_group.update()
        self.hive_group.update()
        self.build_tower_group.update()
        self.bot_group.update()
        self.insect_group.update()
        self.scraps_group.update()
        self.tower_group.update()
        self.bullet_group.update()
        self.damage_notes_group.update()
        self.trap_group.update()
        self.special_group.update()
        self.main_group.sort()
        self.flying_group.sort()

        self.screen.blit(self.background, (0,0))

        if self.build_active:
            self.screen.blit(self.build_overlay, (0,0))

        pygame.draw.rect(self.screen, (255,0,255), (self.map_grid.screen_to_screen(pygame.mouse.get_pos()), (20,20)), 2)

        self.main_group.render()
        self.flying_group.render()
        self.damage_notes_group.render()

        #mouse stuffs!
        if self.build_active:
            x, y = self.map_grid.screen_to_screen(pygame.mouse.get_pos())
            grid = self.map_grid.screen_to_grid((x,y))
            if self.building == objects.TowerBase:
                if self.map_grid.empty_around(grid):
                    i = data.image(self.building.ui_icon)
                    r = i.get_rect()
                    r.midbottom = x+10, y+20
                    self.screen.blit(i, r)
            else:
                if self.map_grid.is_open(grid):
                    i = data.image(self.building.ui_icon)
                    r = i.get_rect()
                    r.midbottom = x+10, y+20
                    self.screen.blit(i, r)
            


        self.screen.blit(self.ui_background, (0,500))
        
        self.app.render()
        self.screen.blit(self.money_ui, self.money_ui_pos)
        self.screen.blit(self.scraps_ui, self.scraps_ui_pos)
        self.screen.blit(self.kills_ui, self.kills_ui_pos)
        self.screen.blit(self.font.render("units: %s/20"%len(self.bot_group.objects), 1, (255,255,255)), (90,570))

        if self.hero.was_killed:
            self.parent.use_child("lose")
        if self.hive.was_killed:
            self.parent.use_child("win")

        text = self.font.render("Insect level: %s"%self.hive.level, 1, (255,255,255))
        new = pygame.Surface((text.get_width()+8, text.get_height()+8)).convert_alpha()
        new.fill((75,75,255,50))
        pygame.draw.rect(new, (0,0,0), ((0,0),new.get_size()), 2)
        new.blit(text, (4, 4))
        self.screen.blit(new, (85,3))

        pygame.display.flip()
