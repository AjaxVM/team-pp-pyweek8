import pygame
from pygame.locals import *

import data, objects

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
    def __init__(self, app, anchor="topleft", text_color=(255,255,255)):
        self.app = app
        self.app.widgets.insert(0, self)

        self.anchor = anchor

        self.text_color = text_color

        self.image = None
        self.text = None
        self.rect = None
        self.font = data.font("data/font.ttf", 32)

        self.hover = False
        self.click = False
        self.highlight = True

        self.events = {}

    def set_pos(self, pos):
        setattr(self.rect, self.anchor, pos)

    def kill(self):
        if self in self.app.widgets:
            self.app.widgets.remove(self)

    def fire_event(self, event):
        if event in self.events:
            self.events[event]()

    def kill(self):
        if self in self.app.widgets:
            self.app.widgets.remove(self)

    def load_text_and_image(self, text, image):
        rect = None
        if text:
            r,g,b = self.text_color
            r = 255-r
            g = 255-g
            b = 255-b
            text2 = [self.font.render(t, 1, self.text_color) for t in text.split("\n") if t]
            text = [self.font.render(t, 1, (r,g,b)) for t in text.split("\n") if t]
            [i.blit(j, (1,1)) for (i,j) in zip(text, text2)]
            rects = [t.get_rect() for t in text]
            w, h = 0,1
            for i in rects:
                if i.width+1 > w:
                    w = i.width+1
                h += i.height
            rect = pygame.rect.Rect(0,0,w,h)
        if image:
            if isinstance(image, pygame.Surface):
                pass
            else:
                image = data.image(image)
            if not rect:
                rect = image.get_rect()
            else:
                nr = image.get_rect()
                rect = rect.union(nr)
        return text, image, rect

    def update(self, event):
        if self.rect:
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
        if self.hover and self.rect and self.highlight:
            surf = pygame.Surface(self.rect.inflate(5,5).size).convert_alpha()
            surf.fill((75,75,255,125))
            new_rect = surf.get_rect(center=self.rect.center)
            pygame.draw.rect(surf, (0,0,0), ((0,0),self.rect.inflate(5,5).size), 1)
            self.app.surf.blit(surf, new_rect)
        if self.text:
            x, y = self.rect.topleft
            down = 0
            for t in self.text:
                self.app.surf.blit(t, (x, y+down))
                down += t.get_height()

    def get_status(self):
        return None

class Label(Widget):
    def __init__(self, app, text, image=None, pos=(0,0), anchor="topleft",
                 text_color=(255,255,255)):
        Widget.__init__(self, app, anchor, text_color)

        self.text, self.image, self.rect = self.load_text_and_image(text, image)
        self.set_pos(pos)
        self.highlight = False


class LinesGroup(Widget):
    def __init__(self, app, obj):
        Widget.__init__(self, app)

        r = obj.rect

        lines = []
        left, top = r.topleft
        right, bottom = r.bottomright
        y = r.centery
        height = int(r.height / 3)

        lines.append(((left-3, top+height*2), (left-7, top+height*2)))
        lines.append(((left-7, top+height*2), (left-7, top+height*4)))
        lines.append(((left-7, top+height*4), (left-3, top+height*4)))

        lines.append(((right+3, top+height*2), (right+7, top+height*2)))
        lines.append(((right+7, top+height*2), (right+7, top+height*4)))
        lines.append(((right+7, top+height*4), (right+3, top+height*4)))

        self.lines = lines

    def render(self):
        for i in self.lines:
            pygame.draw.line(self.app.surf, (255,255,255), i[0], i[1], 1)


class Button(Label):
    def __init__(self, app, text=None, image=None, pos=(0,0), anchor="topleft",
                 callback=None, text_color=(255,255,255),
                 status_message=""):
        Widget.__init__(self, app, anchor, text_color)

        self.text, self.image, self.rect = self.load_text_and_image(text, image)

        if callback:
            self.events["click"] = callback
        self.set_pos(pos)

        self.status_message = status_message

    def get_status(self):
        if self.hover:
            return self.status_message

class TowerInfo(Widget):
    def __init__(self, app, tower):
        Widget.__init__(self, app, "midtop")
        self.image = pygame.Surface((180, 135)).convert_alpha()
        self.image.fill((75, 75, 255, 150))
        pygame.draw.rect(self.image, (0,0,0), (0,0,180,135), 2)
        self.rect = self.image.get_rect()
        self.set_pos((tower.rect.centerx, tower.rect.bottom-10))
        if self.rect.right > 800:
            self.rect.right = 800
        if self.rect.bottom > 600:
            self.rect.bottom = 600
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0

        self.highlight = False

        self.tower = tower

        font = data.font("data/font.ttf", 14)

        self.name_text = font.render("%s - L%s"%(tower.name, tower.level), 1, (0,0,0))
        self.name_text2 = font.render("%s - L%s"%(tower.name, tower.level), 1, (255,255,255))
        self.name_text_pos = (2,2)

        self.damage_text = font.render("damage - %s"%tower.damage, 1, (0,0,0))
        self.damage_text2 = font.render("damage - %s"%tower.damage, 1, (255,255,255))
        self.damage_text_pos = (2,16)

        self.range_text = font.render("range - %s"%tower.range, 1, (0,0,0))
        self.range_text2 = font.render("range - %s"%tower.range, 1, (255,255,255))
        self.range_text_pos = (2,30)

        #we have four spots, 3 for potential new tower types to morph to, and 1 for just upgrading this tower
        self.upgrades = []
        spaces = [60, 20, 100]
        if tower.level == 1:
            for i in tower.upgrade_types:
                image = data.image(i.ui_icon).copy()
                target = i.name
                rect = image.get_rect()
                rect.centerx = spaces.pop(0)
                rect.centery = 80 #???
                cost = i.money_cost, i.scrap_cost

                hover_rect = pygame.Rect(0,0,40,70)
                hover_rect.centerx = rect.centerx
                hover_rect.bottom = 117

                hover_image = pygame.Surface(hover_rect.size).convert_alpha()

                hover_image.fill((75,255,75,50))
                pygame.draw.rect(hover_image, (0,0,0), ((0,0), hover_image.get_size()), 2)

                level = 1

                damage = i.base_attack
                range = i.base_range
                speed = i.base_shoot_speed

                self.upgrades.append((image, target, hover_image, rect, hover_rect,
                                      cost, level, damage, range, speed))

        #upgrade now!
        image = tower.image.copy()
        image.blit(data.image("data/arrow.png"), (0,0))
        target = tower.name
        rect = image.get_rect()
        rect.centerx = 150
        rect.centery = 80 #???

        cost = tower.money_cost, tower.scrap_cost

        hover_rect = pygame.Rect(0,0,40,70)
        hover_rect.centerx = rect.centerx
        hover_rect.bottom = 117

        hover_image = pygame.Surface(hover_rect.size).convert_alpha()
        hover_image.fill((75,255,75,50))
        pygame.draw.rect(hover_image, (0,0,0), ((0,0), hover_image.get_size()), 2)

        level = tower.level + 1
        damage, range, speed = tower.get_stats_at_next_level()

        self.upgrades.append((image, target, hover_image, rect, hover_rect,
                              cost, level, damage, range, speed))

        self.events["click"] = self.handle_click

    def handle_click(self):
        x, y = self.rect.topleft
        mx, my = pygame.mouse.get_pos()
        mx -= x
        my -= y

        for i in self.upgrades:
            (image, target, hover_image, rect, hover_rect,
             cost, level, damage, range, speed) = i

            if hover_rect.collidepoint((mx, my)):
                if target == self.tower.name:
                    if self.tower.game.money >= self.tower.money_cost and\
                       self.tower.game.scraps >= self.tower.scrap_cost:
                        self.tower.upgrade()
                        self.kill()
                        self.tower.game.selected_ui = None
                else:
                    if target == "Missile Tower":
                        to_build = objects.MissileTower
                    elif target == "Bird Food Tower":
                        to_build = objects.BirdFoodTower
                    else:
                        to_build = objects.MissileTower
                    if to_build.money_cost <= self.tower.game.money and\
                       to_build.scrap_cost <= self.tower.game.scraps:
                        self.tower.kill()
                        x, y = self.tower.rect.midbottom
                        objects.BuildTower(self.tower.game, self.tower.game.map_grid.screen_to_screen((x-10, y-20)), target)
                        for i in self.tower.game.bot_group.objects:
                            i.reset_target()
                        self.kill()
                        self.tower.game.selected_ui = None

    def get_status(self):
        if self.hover:
            x, y = self.rect.topleft
            mx, my = pygame.mouse.get_pos()
            mx -= x
            my -= y
            for i in self.upgrades:
                (image, target, hover_image, rect, hover_rect,
                 cost, level, damage, range, speed) = i
                if hover_rect.collidepoint((mx, my)):
                    if target == self.tower.name:
                        n = "Upgrade "
                    else:
                        n = ""
                    x = "\ncost:\n  money: %s\n  scraps: %s\n----------\nattack: %s\nrange: %s\nspeed: %s"
                    return n + target + x % (cost[0], cost[1], damage, range, speed)

    def render(self):
        Widget.render(self)
        x, y = self.rect.topleft

        _x, _y = self.name_text_pos
        _x += x
        _y += y
        self.app.surf.blit(self.name_text, (_x, _y))
        self.app.surf.blit(self.name_text2, (_x+1, _y+1))

        _x, _y = self.damage_text_pos
        _x += x
        _y += y
        self.app.surf.blit(self.damage_text, (_x, _y))
        self.app.surf.blit(self.damage_text2, (_x+1, _y+1))

        _x, _y = self.range_text_pos
        _x += x
        _y += y
        self.app.surf.blit(self.range_text, (_x, _y))
        self.app.surf.blit(self.range_text2, (_x+1, _y+1))

        mx, my = pygame.mouse.get_pos()
        mx -= x
        my -= y

        for i in self.upgrades:
            (image, target, hover_image, rect, hover_rect,
             cost, level, damage, range, speed) = i
            _x, _y = rect.topleft
            _x += x
            _y += y
            self.app.surf.blit(image, (_x, _y))

            if hover_rect.collidepoint((mx, my)):
                _x, _y = hover_rect.topleft
                _x += x
                _y += y
                self.app.surf.blit(hover_image, (_x, _y))


class PopupManager(Widget):
    def __init__(self, app):
        Widget.__init__(self, app, "bottomleft")

        self.messages = []
        self.bg = None
        self.font = data.font("data/font.ttf", 32)

        self.rect = None
        self.pos = (2,498)

    def set(self, text):
        if text:
            self.text, i, self.rect = self.load_text_and_image(text, None)
            self.set_pos(self.pos)
        else:
            self.text, self.rect = None, None

    def render(self):
        self.hover = True
        Widget.render(self)
        self.hover = False
