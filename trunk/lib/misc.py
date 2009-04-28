import pygame
from pygame.locals import *

import math
import random

def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

## TEST CODE
if __name__ == '__main__':

    def displayPath(start, end, blockedmap, path):
        for i in xrange(len(blockedmap)):
            string = ''
            for j in xrange(len(blockedmap[i])):
                if (i,j) == start:
                    string += 's'
                elif (i,j) == end:
                    string += 'E'
                elif path and (i,j) in path:
                    string += '-'
                else:
                    if blockedmap[i][j]:
                        string += 'X'
                    else:
                        string += '.'
                #string += 'X\t'
            print string

        print '\n'*2

    # returns a path
    blockedmap = [
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],

        [False, 2, 2, 2, 2, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
    ]
    start = (2,2)
    end = (6,2)
    path = calculatePath(start, end, blockedmap)
    displayPath(start, end, blockedmap, path)

    # blocked by solid wall
    blockedmap = [
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],

        [2, 2, 2, 2, 2, 2],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
        [False, False, False, False, False, False],
    ]

    start = (2,2)
    end = (6,2)
    path = calculatePath(start, end, blockedmap)
    displayPath(start, end, blockedmap, path)

    # straight diagonal with stuff in the way
    # this one doesnt seem to be grabbing the best path -- takes an extra diag
    blockedmap = [
        [False, False, False, False, False, False],
        [False, 2, False, False, False, False],
        [False, 2, False, False, False, False],
        [False, False, False, False, False, False],

        [False, False, 2, False, 2, 2],
        [False, False, False, False, False, False],
        [False, False, False, 2, 2, False],
        [False, False, False, True, False, False],
    ]
    start = (0,0)
    end = (7,5)
    path = calculatePath(start, end, blockedmap)
    displayPath(start, end, blockedmap, path)

    # simple maze
    blockedmap = [
        [False, False, False, False, False, False],
        [2, 2, 2, False, 2, 2],
        [False, False, False, 2, False, False],
        [False, False, False, 2, False, False],

        [False, 2, 2, 2, 2, 2],
        [False, 2, False, False, False, False],
        [False, 2, False, False, 2, 2],
        [False, False, False, 2, False, False],
    ]
    start = (0,0)
    end = (7,5)
    path = calculatePath(start, end, blockedmap)
    displayPath(start, end, blockedmap, path)
