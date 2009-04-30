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
        ui.Label(self.app, "Testing,\n123", text_color=(255,0,0), pos=(0,0), anchor="topleft")

        ui.Button(self.app, "Play!", text_color=(0,255,0), pos=(0,75),
                  callback=lambda: self.parent.use_child("game"))

    def update(self):
        for event in pygame.event.get():
            if self.app.update(event):
                continue
            if event.type == QUIT:
                self.get_root().shutdown()
                return

        self.get_root().screen.fill((0,0,0))
        self.app.render()
        pygame.display.flip()

class Game(GameState):
    def __init__(self, parent):
        GameState.__init__(self, parent)

        self.screen = self.get_root().screen

        self.audio = sound.SoundManager('data')

        self.background = data.image("data/background1.png")

        self.app = ui.App(self.screen)
        ui.Button(self.app, "Quit Game", pos=(0,500), callback=self.goback,
                  status_message="Quit game...?")
        ui.Button(self.app, "Build Tower!", pos=(160,520), callback=self.set_tower_build,
                  status_message="build a tower already!")
        ui.Button(self.app, "Build Worker!", pos=(160, 560), callback=self.build_worker,
                  status_message="build a worker to build that tower already!")
        ui.Button(self.app, "Build Trap!", pos=(320, 520), callback=self.build_trap,
                  status_message="build a trap?!?!")
        ui.Button(self.app, "Build Warrior!", pos=(320, 560), callback=self.build_warrior,
                  status_message="Let's Ruuuumble!")

        self.status_message = ui.PopupManager(self.app)
        self.status_message.set("Testing, 1,2,3")

        self.main_group = objects.GameGroup()
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

        self.damage_notes_group = objects.GameGroup()

        self.money = 2500
        self.scraps = 2500
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
        self.hive = objects.Hive(self)

        self.map_grid.make_random(40, 7)

        self.build_active = None
        self.building_trap = False
        self.build_overlay = None

        self.selected_object = None
        self.selected_ui = None

    def set_tower_build(self):
        if self.money >= objects.TowerBase.money_cost and self.scraps >= objects.TowerBase.scrap_cost:
            self.build_active = True

            bo = pygame.Surface((800,500)).convert_alpha()
            bo.fill((0,0,0,0))
            for x in xrange(self.map_grid.size[0]):
                for y in xrange(self.map_grid.size[1]):
                    if not self.map_grid.empty_around((x, y)):
                        pygame.draw.rect(bo, (200,0,0,85), (self.map_grid.grid_to_screen((x, y)), (20,20)))
            pygame.draw.rect(bo, (200,0,0,85), ((0,0), (11*20,11*20)))
            pygame.draw.rect(bo, (200,0,0,85), ((800-9*20,500-9*20), (9*20,9*20)))

            self.build_overlay = bo

    def update_money(self):
        self.money_ui = self.font.render("money: %s"%self.money, 1, (255,255,255))
        self.scraps_ui = self.font.render("scraps: %s"%self.scraps, 1, (255,255,255))
        self.kills_ui = self.font.render("kills: %s"%self.kills, 1, (255,255,255))

    def build_worker(self):
        if self.money >= objects.Worker.money_cost and self.scraps >= objects.Worker.scrap_cost:
            self.hero.build_worker()

    def build_trap(self):
        #TODO: replace with trap type picker
        if self.money >= objects.Trap.money_cost and self.scraps >= objects.Trap.scrap_cost:
            self.building_trap = True
            self.build_active = False
            self.build_overlay = None

    def build_warrior(self):
        #TODO: replace with warrior type selection
        if self.money >= objects.BattleBot.money_cost and self.scraps >= objects.BattleBot.scrap_cost:
            self.hero.build_warrior()

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
                            if self.map_grid.empty_around(grid):
                                self.build_active = False
                                objects.BuildTower(self, self.map_grid.grid_to_screen(grid))
                                for i in self.bot_group.objects:
                                    i.reset_target()
                        else:
                            if self.building_trap:
                                if self.map_grid.is_open(grid):
                                    self.building_trap = False
                                    objects.Trap(self, self.map_grid.grid_to_screen(grid))
                        self.build_active = False
                        for i in self.tower_group.objects:
                            if i.rect.collidepoint(event.pos):
                                i.selected = True
                                self.selected_object = i
                                self.selected_ui = ui.TowerInfo(self.app, i)
                    else:
                        self.build_active = False
                        self.building_trap = False
                if event.button == 3: #right
                    self.build_active = False
                    self.building_trap = False

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
        self.main_group.sort()

        self.screen.blit(self.background, (0,0))

        if self.build_active:
            self.screen.blit(self.build_overlay, (0,0))
        pygame.draw.rect(self.screen, (255,0,255), (self.map_grid.screen_to_screen(pygame.mouse.get_pos()), (20,20)), 2)


        self.main_group.render()
        self.damage_notes_group.render()
        pygame.draw.rect(self.screen, (125,125,125), (0,500,800,600))
        self.app.render()
        self.screen.blit(self.money_ui, self.money_ui_pos)
        self.screen.blit(self.scraps_ui, self.scraps_ui_pos)
        self.screen.blit(self.kills_ui, self.kills_ui_pos)

        pygame.display.flip()
