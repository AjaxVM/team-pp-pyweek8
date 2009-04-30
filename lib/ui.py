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
    def __init__(self, app, anchor="topleft"):
        self.app = app
        self.app.widgets.insert(0, self)

        self.anchor = anchor

        self.image = None
        self.text = None
        self.rect = None
        self.font = data.font("data/font.ttf", 32)
        self.text_color = (255,255,255,255)
        self.image_border_size = None
        self.tsize = (0,0)

        self.hover = False
        self.click = False

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
        if text:
            text = [self.font.render(t, 1, self.text_color) for t in text.split("\n")]
            rects = [t.get_rect() for t in text]
            w, h = 0,0
            for i in rects:
                if i.width > w:
                    w = i.width
                h += i.height
            rect = pygame.rect.Rect(0,0,w,h)
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
            down = 0
            for t in self.text:
                self.app.surf.blit(t, (x, y+down))
                down += t.get_height()

class Label(Widget):
    def __init__(self, app, text, background_image=None, text_color=(255,255,255,255),
                 background_border=None, pos=(0,0), anchor="topleft"):
        Widget.__init__(self, app, anchor)

        self.text_color=text_color
        self.image_border_size = background_border

        self.text, self.image, self.rect, self.tsize = self.load_text_and_image(text, background_image)
        self.set_pos(pos)


class Button(Label):
    def __init__(self, app, text=None, image=None, image_hover=None, image_click=None,
                 text_color=(255,255,255), text_color_hover=(255,255,255),
                 text_color_click=(255,255,255), image_border=None, pos=(0,0), anchor="topleft",
                 callback=None):
        Widget.__init__(self, app, anchor)

        self.text_color = text_color
        self.reg_atts = self.load_text_and_image(text, image)
        self.text_color = text_color_hover
        self.hov_atts = self.load_text_and_image(text, image_hover)
        self.text_color = text_color_click
        self.cli_atts = self.load_text_and_image(text, image_click)

        if callback:
            self.events["click"] = callback
        self._pos = pos
        self.set_atts(self.reg_atts)

    def set_atts(self, atts):
        self.text, self.image, self.rect, self.tsize = atts
        self.set_pos(self._pos)

    def update(self, event):
        Widget.update(self, event)

        if self.hover and self.click:
            self.set_atts(self.cli_atts)
        elif self.hover:
            self.set_atts(self.hov_atts)
        else:
            self.set_atts(self.reg_atts)

class TowerInfo(Widget):
    def __init__(self, app, tower):
        Widget.__init__(self, app, "midtop")
        self.image = pygame.Surface((180, 175)).convert_alpha()
        self.image.fill((75, 75, 255, 75))
        pygame.draw.rect(self.image, (0,0,0), (0,0,180,175), 2)
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
                cost = font.render("cost:", 1, (0,0,0))
                cost2 = font.render("cost:", 1, (255,255,255))
                color = (255,255,255) if tower.game.money >= i.money_cost else (255,0,0)
                cost_money = font.render(str(i.money_cost)+"m", 1, (0,0,0))
                cost_money2 = font.render(str(i.money_cost)+"m", 1, color)
                color = (255,255,255) if tower.game.scraps >= i.scrap_cost else (255,0,0)
                cost_scrap = font.render(str(i.scrap_cost)+"s", 1, (0,0,0))
                cost_scrap2 = font.render(str(i.scrap_cost)+"s", 1, color)
                cost_rect = cost.get_rect()
                cost_rect.midtop = (rect.centerx, 110)
                cost_money_rect = cost_money.get_rect()
                cost_money_rect.topleft = cost_rect.bottomleft
                cost_scrap_rect = cost_scrap.get_rect()
                cost_scrap_rect.topleft = cost_money_rect.bottomleft

                rect.height = cost_scrap_rect.bottom - rect.top
                hover_rect = pygame.Rect(0,0,35,115)
                hover_rect.centerx = rect.centerx
                hover_rect.bottom = 165

                hover_image = pygame.Surface(hover_rect.size).convert_alpha()

                hover_image.fill((75,255,75,50))
                pygame.draw.rect(hover_image, (0,0,0), ((0,0), hover_image.get_size()), 2)

                level = 1

                self.upgrades.append((image, target, hover_image, rect, hover_rect,
                                      cost, cost2, cost_rect,
                                      cost_money, cost_money2, cost_money_rect,
                                      cost_scrap, cost_scrap2, cost_scrap_rect, level))

        #upgrade now!
        image = tower.image.copy()
        image.blit(data.image("data/arrow.png"), (0,0))
        target = tower.name
        rect = image.get_rect()
        rect.centerx = 150
        rect.centery = 80 #???

        cost = font.render("cost:", 1, (0,0,0))
        cost2 = font.render("cost:", 1, (255,255,255))
        color = (255,255,255) if tower.game.money >= tower.money_cost else (255,0,0)
        cost_money = font.render(str(tower.money_cost)+"m", 1, (0,0,0))
        cost_money2 = font.render(str(tower.money_cost)+"m", 1, color)
        color = (255,255,255) if tower.game.scraps >= tower.scrap_cost else (255,0,0)
        cost_scrap = font.render(str(tower.scrap_cost)+"s", 1, (0,0,0))
        cost_scrap2 = font.render(str(tower.scrap_cost)+"s", 1, color)
        cost_rect = cost.get_rect()
        cost_rect.midtop = (rect.centerx, 110)
        cost_money_rect = cost_money.get_rect()
        cost_money_rect.topleft = cost_rect.bottomleft
        cost_scrap_rect = cost_scrap.get_rect()
        cost_scrap_rect.topleft = cost_money_rect.bottomleft

        rect.height = cost_scrap_rect.bottom - rect.top

        hover_rect = pygame.Rect(0,0,35,115)
        hover_rect.centerx = rect.centerx
        hover_rect.bottom = 165

        hover_image = pygame.Surface(hover_rect.size).convert_alpha()
        hover_image.fill((75,255,75,50))
        pygame.draw.rect(hover_image, (0,0,0), ((0,0), hover_image.get_size()), 2)

        level = tower.level + 1
        self.upgrades.append((image, target, hover_image, rect, hover_rect,
                                  cost, cost2, cost_rect,
                                  cost_money, cost_money2, cost_money_rect,
                                  cost_scrap, cost_scrap2, cost_scrap_rect, level))

        self.events["click"] = self.handle_click

    def handle_click(self):
        x, y = self.rect.topleft
        mx, my = pygame.mouse.get_pos()
        mx -= x
        my -= y

        for i in self.upgrades:
            (image, target, hover_image, rect, hover_rect,
             cost, cost2, cost_rect,
             cost_money, cost_money2, cost_money_rect,
             cost_scrap, cost_scrap2, cost_scrap_rect, level) = i

            if hover_rect.collidepoint((mx, my)):
                if target == self.tower.name:
                    if self.tower.game.money >= self.tower.money_cost and\
                       self.tower.game.scraps >= self.tower.scrap_cost:
                        self.tower.upgrade()
                        self.kill()
                        self.tower.game.selected_ui = TowerInfo(self.app, self.tower)
                else:
                    if target == "Missile Tower":
                        to_build = objects.MissileTower
                    else:
                        to_build = objects.MissileTower
                    if to_build.money_cost <= self.tower.game.money and\
                       to_build.scrap_cost <= self.tower.game.scraps:
                        self.tower.kill()
                        x, y = self.tower.rect.midbottom
                        objects.BuildTower(self.tower.game, self.tower.game.map_grid.screen_to_screen((x-10, y-20)), target)
                        for i in self.tower.game.worker_group.objects:
                            i.reset_target()
                        self.kill()
                

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
             cost, cost2, cost_rect,
             cost_money, cost_money2, cost_money_rect,
             cost_scrap, cost_scrap2, cost_scrap_rect, level) = i
            _x, _y = rect.topleft
            _x += x
            _y += y
            self.app.surf.blit(image, (_x, _y))

            _x, _y = cost_rect.topleft
            _x += x
            _y += y
            self.app.surf.blit(cost, (_x, _y))
            self.app.surf.blit(cost2, (_x+1, _y+1))

            _x, _y = cost_money_rect.topleft
            _x += x
            _y += y
            self.app.surf.blit(cost_money, (_x, _y))
            self.app.surf.blit(cost_money2, (_x+1, _y+1))

            _x, _y = cost_scrap_rect.topleft
            _x += x
            _y += y
            self.app.surf.blit(cost_scrap, (_x, _y))
            self.app.surf.blit(cost_scrap2, (_x+1, _y+1))

            if hover_rect.collidepoint((mx, my)):
                _x, _y = hover_rect.topleft
                _x += x
                _y += y
                self.app.surf.blit(hover_image, (_x, _y))
