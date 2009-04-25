import retrogamelib as rgl

class Game(object):
    
    def __init__(self):
        
        # Setup the display
        rgl.display.init(2.0, "Lunaroid")
    
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
    
    def draw(self):
        
        # Get the surface to draw to
        surface = rgl.display.get_surface()
        surface.fill((0, 0, 0))
        
        # Update the display
        rgl.display.update()
