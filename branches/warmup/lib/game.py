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
    
    def move_view(self, dx, dy):
        for obj in self.objects:
            if obj != self.player:
                obj.kill()
        self.engine.pos[0] += dx
        self.engine.pos[1] += dy
        self.engine.parse_level()
    
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
        for obj in self.objects:
            obj.update()
    
    def handle_input(self):
        
        # Have rgl check and handle the input for us
        rgl.button.handle_input()
        
        self.player.moving = False
        self.player.lookup = False
        if rgl.button.is_held(LEFT):
            self.player.move(-3, 0)
        if rgl.button.is_held(RIGHT):
            self.player.move(3, 0)
        if rgl.button.is_held(UP):
            self.player.lookup = True
            
        # Make the player jump if you press the A Button/Z Key
        if rgl.button.is_pressed(A_BUTTON):
            self.player.jump()
        if rgl.button.is_held(A_BUTTON):
            self.player.jump_accel = self.player.jump_accel_slow
        else:
            self.player.jump_accel = self.player.jump_accel_fast
    
        if self.player.rect.left > 256:
            self.player.rect.left = 0
            self.move_view(1, 0)
        if self.player.rect.right < 0:
            self.player.rect.right = 256
            self.move_view(-1, 0)
        if self.player.rect.top > 240:
            self.player.rect.top = 0
            self.move_view(0, 1)
        if self.player.rect.bottom < 0:
            self.player.rect.bottom = 240
            self.move_view(0, -1)
    
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
