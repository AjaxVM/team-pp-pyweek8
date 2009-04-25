import retrogamelib as rgl
from retrogamelib.constants import *
from objects import *
from engine import *

class Game(object):
    
    def __init__(self):
        
        # Setup the display
        rgl.display.init(2.0, "Lunaroid")
        
        # Create some groups to hold objects
        self.objects = rgl.gameobject.Group()
        
        # Assign some groups to the global objects' `groups` attributes
        Player.groups = [self.objects]
        Wall.groups = [self.objects]
        
        # Create some starting objects
        self.engine = Engine()
        self.engine.parse_level()
        self.player = Player(self.engine)
    
    def loop(self):
        while 1:
            
            # Update and cap framerate
            rgl.clock.tick()
            self.update()
            
            # Handle input
            self.handle_input()
            
            # Drawing
            self.draw()
    
    def update(self):
        pass
    
    def handle_input(self):
        
        # Have rgl check and handle the input for us
        rgl.button.handle_input()
        
        if rgl.button.is_held(LEFT):
            self.player.move(-3, 0)
        if rgl.button.is_held(RIGHT):
            self.player.move(3, 0)
        if rgl.button.is_held(UP):
            self.player.move(0, -3)
        if rgl.button.is_held(DOWN):
            self.player.move(0, 3)
    
    def draw(self):
        
        # Get the surface to draw to
        surface = rgl.display.get_surface()
        
        # Do basic pygame drawing
        surface.fill((0, 0, 0))
        
        # Draw all the objects
        for obj in self.objects:
            obj.draw(surface)
        
        # Update the display
        rgl.display.update()
