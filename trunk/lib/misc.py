import pygame
from pygame.locals import *

import math
import random

def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def dist2(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2

