import pygame
from pygame.locals import *

_images = {}
def load_image(filename):
    if filename in _images:
        return _images[filename]
    image = pygame.image.load(filename).convert_alpha()
    _images[filename] = image
    return image

_fonts = {}
def font(fname, size):
    if (fname, size) in _fonts:
        return _fonts[(fname, size)]
    font = pygame.font.Font(fname, size)
    _fonts[(fname, size)] = font
    return font
