import pyggel
from pyggel import *

class Menu(object):
    def __init__(self, state):
        self.state = state
        self.state.wave = 0 #reset this...

        self.run()

    def run(self):
        print 32 #this should loop!
        self.state.quit = True

class AmmoRoom(object):
    def __init__(self, state):
        self.state = state
        self.run()

    def run(self):
        print 33

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

        self.state = "menu"

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
run()
