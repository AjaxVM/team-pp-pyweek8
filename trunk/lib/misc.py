import pygame
from pygame.locals import *

import math

def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)




import heapq

def calculatePath(start, end, blockedmap):
    """Calculates a path using an a* like algorithm.
    @param start: coordinates of start
    @param end: coordinates of end
    @param blockedmap: 2d array of coordinates, true for blocked, false if free
    @returns: a list of coordinates for the path, or false if no path was found
    @todo:  return multiple paths? variation?

    Used this for reference: http://www.gamedev.net/reference/articles/article2003.asp

    We need more info to implement this effectively. When are we calculating paths?
    Should they be pre-calculated? I can make this function return a couple different
    paths to the target -- we could use that to pre-bake the paths from the spawn
    points to whatever targets we have. This would drastically cut down on the
    pathfinding time, which is usually a massive part of the CPU time, especially
    if we are using tons of guys.

    Maybe as simple as a list of paths from point A to B that a unit can lookup
    if they need a path. Decide on the memory used vs the cpu time.

    Currently horizontal movement costs a bit less than diagonal movement -- this
    really depends on how we implement the actual unit movement, so tweak the
    constants below for that as necessary. We can also tweak the movement cost
    for each direction if needed via the adjacent list.

    Options:
        add random weights in the nodelist to generate tweaked paths?
        just add some 'wobble'?


    """

    # type checking
    tupletype = type(())
    listtype = type([])
    if type(start) != tupletype or len(start) != 2:
        raise Exception('Start parameter must be a 2 tuple representing the coordinates of the start position')
    if type(end) != tupletype or len(end) != 2:
        raise Exception('End parameter must be a 2 tuple representing the coordinates of the end position')
    if type(blockedmap) != listtype:
        raise Exception('blockedmap parameter must be a 2D array with true/false values')

    # some useful info
    numcols = len(blockedmap)
    numrows = len(blockedmap[0])

    ORTHOGONALMOVE = 10
    DIAGONALMOVE = 14

    # create open and closed lists
    openlist = []       # cost, coords, parentcoords
    closedlist = []
    INOPENLIST = 1
    INCLOSEDLIST = 2
    inlist = [ [-1 for j in xrange(numrows)] for i in xrange(numcols)]
    #nodelist = [ [False for j in xrange(numcols)] for i in xrange(numrows)]
    nodelist = [ [(0,0, ORTHOGONALMOVE * (abs(end[1]-i) + abs(end[0]-j))) for j in xrange(numrows)] for i in xrange(numcols)]
    parentlist = [ [(-1,-1) for j in xrange(numrows)] for i in xrange(numcols)]
    # todo: do I really need all these lists? this got so messy trying to keep object overhead out of it...

    # add starting location to open list-- hopefully it is on our map...
    openlist.append( (-1, start, False))
    parentlist[start[0]][start[1]] = False
    inlist[start[0]][start[1]] = INOPENLIST

    # loop through map until path is found
    adjacent = [ (-1, -1, DIAGONALMOVE), (0,-1, ORTHOGONALMOVE), (1,-1, DIAGONALMOVE),
                 (-1, 0, ORTHOGONALMOVE),                        (1, 0, ORTHOGONALMOVE),
                 (-1, 1, DIAGONALMOVE),  (0, 1, ORTHOGONALMOVE), (1, 1, DIAGONALMOVE)]

    while True:
        # if open heap is empty, no path is available
        if len(openlist) == 0:

##            # print debug info
##            for i in xrange(numcols):
##                string = ''
##                for j in xrange(numrows):
##                    string += '%d\t'%nodelist[i][j][0]
##                print string
            return False

        # pop lowest open node from the heap
        cost, coordinates, parentcoordinates = heapq.heappop(openlist)
        costs = nodelist[coordinates[0]][coordinates[1]]

        #print "DEBUG:  Checking (%d, %d)" % coordinates

        # if this is target, build path and return
        if coordinates == end:
            path = []

##            # print debug info
##            for i in xrange(numcols):
##                string = ''
##                for j in xrange(numrows):
##                    if parentlist[i][j] is not False:
##                        string += '%d,%d\t'%parentlist[i][j]
##                    else:
##                        string += '\t'
##                print string

            path.append(end)
            while parentcoordinates:
                path.append(parentcoordinates)
                parentcoordinates = parentlist[parentcoordinates[0]][parentcoordinates[1]]

            path.reverse()
            return path

        # add it to the closed list
        closedlist.append( (coordinates, parentcoordinates) )
        inlist[coordinates[0]][coordinates[1]] = INCLOSEDLIST

        # check adjacent nodes
        for modx, mody, modmovecost in adjacent:
            newx = coordinates[0] + modx
            newy = coordinates[1] + mody

            # skip if off map
            if newx < 0 or newx >= numcols or newy < 0 or newy >= numrows:
                #print "DEBUG: (%d, %d) OFF MAP" % (newx,newy)
                continue

            # skip if not walkable
            if blockedmap[newx][newy]:
                #print "DEBUG: (%d, %d) BLOCKED" % (newx,newy)
                continue

            # skip if on closed list
            if inlist[newx][newy] == INCLOSEDLIST:
                #print "DEBUG: (%d, %d) ALREADY CLOSED" % (newx,newy)
                continue

            #print "DEBUG: TESTING (%d, %d)" % (newx, newy)
            # if on open list
            if inlist[newx][newy] == INOPENLIST:

                #print "DEBUG: --- FOUND IN OPEN LIST"

                # get existing info for this
                newcost, newmovecost, newhcost = nodelist[newx][newy]

                # check if this path is cheaper, update it
                if nodelist[newx][newy][1] + modmovecost < newmovecost:
                    # find node in openlist and update it
                    for index in xrange(len(openlist)):
                        if openlist[index][3] == (newx, newy):
                            updatedmovecost = costs[1] + modmovecost
                            updatedcost = updatedmovecost + newhcost

                            # update node -- cost, coords, parentcoords
                            openlist[index] = ( updatedcost, (newx,newy), coordinates)
                            parentlist[newx][newy] = coordinates
                            nodelist[newx][newy] = updatedcost, updatedmovecost, newhcost

                            # re-sort openlist
                            openlist.sort()

                            break

            # not on open list
            else:
                #print "DEBUG: --- NOT IN LIST YET"
                # calculate costs
                newcost, newmovecost, newhcost = nodelist[newx][newy]
                newmovecost = costs[1] + modmovecost
                newcost = newmovecost + newhcost

                # add to open list
                heapq.heappush(openlist, (newcost, (newx,newy), coordinates))
                inlist[newx][newy] = INOPENLIST
                parentlist[newx][newy] = coordinates
                # save cost info
                nodelist[newx][newy] = (newcost, newmovecost, newhcost)


    return False


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

        [False, True, True, True, False, False],
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

        [True, True, True, True, True, True],
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
        [False, True, False, False, False, False],
        [False, True, False, False, False, False],
        [False, False, False, False, False, False],

        [False, False, True, False, True, True],
        [False, False, False, False, False, False],
        [False, False, False, True, True, False],
        [False, False, False, True, False, False],
    ]
    start = (0,0)
    end = (7,5)
    path = calculatePath(start, end, blockedmap)
    displayPath(start, end, blockedmap, path)

    # simple maze
    blockedmap = [
        [False, False, False, False, False, False],
        [True, True, True, False, True, True],
        [False, False, False, True, False, False],
        [False, False, False, True, False, False],

        [False, True, True, True, True, True],
        [False, True, False, False, False, False],
        [False, True, False, False, True, True],
        [False, False, False, True, False, False],
    ]
    start = (0,0)
    end = (7,5)
    path = calculatePath(start, end, blockedmap)
    displayPath(start, end, blockedmap, path)