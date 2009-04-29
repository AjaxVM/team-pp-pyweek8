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

class AmmoRoom(object):
    def __init__(self, state):
        self.state = state
        self.grid = objects.HouseGrid()
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

        for i in xrange(20):
            x = objects.HouseItem(self, None)
            self.scene.add_3d(x)
        self.run()

    def run(self):
        while 1:
            self.event_handler.update()
            if self.event_handler.quit:
                self.state.quit = True
                return

            pyggel.view.clear_screen()
            pick = self.scene.render(self.camera)
            if pick and isinstance(pick, objects.HouseItem):
                pick.highlight()

            if 1 in self.event_handler.mouse.released: #click?
                if pick and isinstance(pick, objects.HouseItem):
                    pick.pickup()
                    print self.ammo
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
        pyggel.quit()

def run():
    a = GameController()
    a.run()
