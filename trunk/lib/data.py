import pygame
from pygame.locals import *

_images = {}
def image(filename):
    if filename in _images:
        return _images[filename]
    image = pygame.image.load(filename).convert_alpha()
    _images[filename] = image
    return image

_fonts = {}
def font(fname, size, bold=False, italic=False):
    if (fname, size, bold, italic) in _fonts:
        return _fonts[(fname, size, bold, italic)]
    font = pygame.font.Font(fname, size)
    _fonts[(fname, size, bold, italic)] = font
    return font
