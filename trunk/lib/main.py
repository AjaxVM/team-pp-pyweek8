import pyggel
from pyggel import *

import objects

class Menu(object):
    def __init__(self, state):
        self.state = state
        self.state.wave = 0 #reset this...
        self.state.ammo = [] #reset!

        self.run()

    def run(self):
        print 32 #this should loop!
        self.state.quit = True

class AmmoManager(object):
    def __init__(self, state):
        self.state = state
        self.ammo = self.state.ammo

        self.scene = pyggel.scene.Scene()

        self.event_handler = pyggel.event.Handler()

        self.app = pyggel.gui.App(self.event_handler)
        pyggel.gui.Button(self.app, "Go Back!", callbacks=[self.goto_ammo])
        pyggel.gui.NewLine(self.app)
        pyggel.gui.NewLine(self.app, height=75)
        self.scene.add_2d(self.app)

        self.store = {}

        for i in self.ammo:
            x = pyggel.gui.Button(self.app, str(i.modelname), callbacks=[self.remove_ammo(i)])
            pyggel.gui.NewLine(self.app)
            self.store[i] = x

        self.done = False
        self.run()

    def remove_ammo(self, ammo):
        def r():
            i = self.store[ammo]
            self.ammo.remove(ammo)
            self.app.widgets.remove(i)
            ammo.add_to_grid()
        return r

    def goto_ammo(self):
        self.done = True
        self.state.state = "ammo"

    def run(self):
        while 1:
            self.event_handler.update()
            if self.event_handler.quit:
                self.state.quit = True
                return
            if self.done:
                return

            pyggel.view.clear_screen()
            self.scene.render()
            pyggel.view.refresh_screen()

class AmmoRoom(object):
    def __init__(self, state):
        self.state = state
        self.ammo = self.state.ammo

        self.scene = pyggel.scene.Scene()
        self.scene.pick = True
        self.camera = pyggel.camera.LookAtCamera((0,0,-2), distance=25)
        self.camera.rotx = -45 #look down on our loot!
        light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                               (1,1,1,1), (50,50,50,10),
                               (0,0,0), True)

        self.scene.add_light(light)

        self.event_handler = pyggel.event.Handler()

        self.ammo_ui = pyggel.font.MEFont(None, 32).make_text_image("Ammo: %s/10"%len(self.ammo))
        self.scene.add_2d(self.ammo_ui)

        app = pyggel.gui.App(self.event_handler)
        pyggel.gui.Button(app, "Manage Ammo!", callbacks=[self.goto_ammo_manager],
                          pos=(0,50))
        self.scene.add_2d(app)

        for i in self.state.house_grid.grid:
            for x in i:
                if x:
                    self.scene.add_3d(x)

        self.done = False
        self.run()

    def goto_ammo_manager(self):
        self.done = True
        self.state.state = "ammoM"

    def run(self):
        while 1:
            self.event_handler.update()
            if self.event_handler.quit:
                self.state.quit = True
                return
            if self.done:
                return

            pyggel.view.clear_screen()
            pick = self.scene.render(self.camera)
            if pick and isinstance(pick, objects.HouseItem):
                pick.highlight()

            if 1 in self.event_handler.mouse.released: #click?
                if pick and isinstance(pick, objects.HouseItem):
                    if len(self.ammo) < 10:
                        pick.remove()
                        self.ammo.append(pick)
                        self.scene.remove_3d(pick)
                        self.ammo_ui.text = "Ammo: %s/10"%len(self.ammo)
            pyggel.view.refresh_screen()

class FightScreen(object):
    def __init__(self, state):
        self.state = state
        self.run()

    def run(self):
        print 34

class GameController(object):
    def __init__(self):
        pyggel.init()

        self.wave = 0
        self.ammo = []
        self.house_grid = objects.HouseGrid()
        for i in xrange(20):
            objects.HouseItem(self.house_grid, None)

        self.state = "ammo"

        self.quit = False

    def run(self):
        while not self.quit:
            if self.state == "menu":
                Menu(self)
            if self.state == "ammo":
                AmmoRoom(self)
            if self.state == "game":
                FightScreen(self)
            if self.state == "ammoM":
                AmmoManager(self)
        pyggel.quit()

def run():
    a = GameController()
    a.run()
