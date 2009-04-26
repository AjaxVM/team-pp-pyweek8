import pygame
from pygame.locals import *

import data

def resize_image(image, size, border_size=None):
    x, y = size
    if x < image.get_width(): x = image.get_width()
    if y < image.get_height(): y = image.get_height()
    size = x, y
    if border_size != None:
        if border_size > int(min(image.get_size())/3):
            border_size = int(min(image.get_size())/3)
        x1=min((border_size, int(image.get_width()/3)))
        y1=min((border_size, int(image.get_height()/3)))
        x2 = image.get_width()-x1*2
        y2 = image.get_height()-y1*2
    else:
        x1=x2=int(image.get_width()/3)
        y1=y2=int(image.get_height()/3)

    topleft = image.subsurface((0, 0), (x1, y1))
    top = pygame.transform.scale(image.subsurface((x1, 0), (x2, y1)), (size[0]-x1*2, y1))
    topright = image.subsurface((x1+x2, 0), (x1,y1))

    left = pygame.transform.scale(image.subsurface((0, y1), (x1, y2)), (x1, size[1]-y1*2))
    middle = pygame.transform.scale(image.subsurface((x1, y1), (x2,y2)), (size[0]-x1*2, size[1]-y1*2))
    right = pygame.transform.scale(image.subsurface((x1+x2, y1), (x1,y2)), (x1, size[1]-y1*2))

    botleft = image.subsurface((0, y1+y2), (x1,y1))
    bottom = pygame.transform.scale(image.subsurface((x1, y1+y2), (x2, y1)), (size[0]-x1*2, y1))
    botright = image.subsurface((x1+y1, y1+y2), (x1,y1))

    new = pygame.Surface(size).convert_alpha()
    new.fill((0,0,0,0))
    new.blit(topleft, (0, 0))
    new.blit(top, (x1, 0))
    new.blit(topright, (size[0]-x1, 0))

    new.blit(left, (0, y1))
    new.blit(middle, (x1,y1))
    new.blit(right, (size[0]-x1, y1))

    new.blit(botleft, (0, size[1]-y1))
    new.blit(bottom, (x1, size[1]-y1))
    new.blit(botright, (size[0]-x1, size[1]-y1))
    return image, (x1, y1)

class App(object):
    def __init__(self, surf):
        self.surf = surf

        self.widgets = []

    def update(self, event):
        for i in self.widgets:
            x = i.update(event)
            if x:
                return True
        return False

    def render(self):
        self.widgets.reverse()
        for i in self.widgets:
            i.render()
        self.widgets.reverse()

class Widget(object):
    def __init__(self, app, anchor="topleft"):
        self.app = app
        self.app.widgets.insert(0, self)

        self.anchor = anchor

        self.image = None
        self.text = None
        self.rect = None
        self.font = data.font(None, 32)
        self.text_color = (255,255,255,255)
        self.image_border_size = None
        self.tsize = (0,0)

        self.hover = False
        self.click = False

        self.events = {}

    def set_pos(self, pos):
        setattr(self.rect, self.anchor, pos)

    def fire_event(self, event):
        if event in self.events:
            self.events[event]()

    def kill(self):
        self.app.widgets.remove(self)

    def load_text_and_image(self, text, image):
        if text:
            text = self.font.render(text, 1, self.text_color)
            rect = text.get_rect()
        else:
            text = None
            rect = None
        if image:
            if not rect:
                rect = data.image(image).get_rect()
            image, image_tsize = resize_image(data.image(image), rect.size,
                                               self.image_border_size)
            rect = self.image.get_rect()
        else:
            image = None
            image_tsize = (0,0)
        return text, image, rect, image_tsize

    def update(self, event):
        if event.type == MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.hover = True
                for i in self.app.widgets:
                    if not i == self:
                        i.hover = False
                return True
            else:
                self.hover = False
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.hover:
                    self.click = True
                    for i in self.app.widgets:
                        if not i == self:
                            i.hover = False
                            i.click = False
                    return True
                else:
                    self.click = False
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                if self.click and self.hover:
                    self.fire_event("click")
                    self.click = False
                    for i in self.app.widgets:
                        if not i == self:
                            i.hover = False
                            i.click = False
                    return True

    def render(self):
        if self.image:
            self.app.surf.blit(self.image, self.rect)
        if self.text:
            x, y = self.rect.topleft
            x += self.tsize[0]
            y += self.tsize[1]
            self.app.surf.blit(self.text, (x, y))

class Label(Widget):
    def __init__(self, app, text, background_image=None, text_color=(255,255,255,255),
                 background_border=None, pos=(0,0), anchor="topleft"):
        Widget.__init__(self, app, anchor)

        self.text_color=text_color
        self.image_border_size = background_border

        self.text, self.image, self.rect, self.tsize = self.load_text_and_image(text, background_image)
        self.set_pos(pos)
        
