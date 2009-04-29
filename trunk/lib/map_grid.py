import random, heapq

ORTHOGONALMOVE = 10
DIAGONALMOVE = 14 #so they don't keep cutting across the blasted towers all the time!
INOPENLIST = 1
INCLOSEDLIST = 2

class MapGrid(object):
    """This object stores all map related stuff, as well as "open"
       spaces for towers/traps to be built on..."""
    def __init__(self, game):
        self.size = (800/20, 500/20)

        self.game = game

        self.make_base_grid()
        self.fill((0,0), (10, 10)) #fill in the enemy area so we can't build there!
        self.fill((self.size[0]-8, self.size[1]-8), (8,8))

    def make_base_grid(self):
        """This creates the base grid.
           Each grid must have one of 3 states:
               0: empty
               1: occupied, non-movement-blocking
               2: occupied, blocking
               3: occupied, blocking, bugs should avoid!"""
        grid = []
        for x in xrange(self.size[0]):
            grid.append([])
            for y in xrange(self.size[1]):
                grid[-1].append(0)

        self.grid = grid

    def fill(self, start, size, code=1):
        """Fill area from start to start + size with occupied stuffs..."""
        for x in xrange(size[0]):
            for y in xrange(size[1]):
                _x=x+start[0]
                _y=y+start[1]
                if not self.out_of_bounds((_x,_y)):
                    self.set((_x, _y), code)

    def set(self, pos, code=1):
        if self.out_of_bounds(pos):
            return
        self.grid[pos[0]][pos[1]] = code

    def out_of_bounds(self, pos):
        return pos[0] < 0 or pos[0] >= self.size[0] or pos[1] < 0 or pos[1] >= self.size[1]

    def is_open(self, pos):
        return self.grid[pos[0]][pos[1]] == 0

    def is_blocking(self, pos):
        return self.grid[pos[0]][pos[1]] == 2

    def screen_to_grid(self, pos):
        x, y = pos
        x = (int(x/20) if x else 0)
        y = (int(y/20) if y else 0)
        return x, y

    def grid_to_screen(self, pos):
        x, y = pos
        #TODO: why do we need to be adding 10 here - obviously because it is wrong on screen otherwise, but why?
        x = x * 20
        y = y * 20
        return x, y

    def screen_to_screen(self, pos):
        """This just makes sure the screen pos is moved to the nearest grid pos..."""
        return self.grid_to_screen(self.screen_to_grid(pos))

    def empty_around(self, pos):
        """Return wether there are no filled spaces +/- 1 of pos."""
        for x in xrange(pos[0]-1, pos[0]+2):
            for y in xrange(pos[1]-1, pos[1]+2):
                if not self.out_of_bounds((x, y)):
                    if self.grid[x][y]:
                        return False
        return True

    def should_avoid(self, pos):
        """Return whether there are no filled spaces +/- 1 of pos."""
        for x in xrange(pos[0]-2, pos[0]+3):
            for y in xrange(pos[1]-2, pos[1]+3):
                if not self.out_of_bounds((x, y)):
                    if self.grid[x][y] == 3:
                        return True
        return False

    def disable_diag(self, pos):
        """Return whether there are no filled spaces +/- 1 of pos."""
        for x in xrange(pos[0]-1, pos[0]+2):
            for y in xrange(pos[1]-1, pos[1]+2):
                if not self.out_of_bounds((x, y)):
                    if self.grid[x][y] > 1:
                        return True
        return False

    def calculate_path(self, start, end):
        """Calculates a path using an a* like algorithm.
        @param start: coordinates of start
        @param end: coordinates of end
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
        """

        blockedmap = self.grid

        # type checking
        tupletype = type(())
        listtype = type([])
        if type(start) != tupletype or len(start) != 2:
            raise Exception('Start parameter must be a 2 tuple representing the coordinates of the start position')
        if type(end) != tupletype or len(end) != 2:
            raise Exception('End parameter must be a 2 tuple representing the coordinates of the end position')

        # some useful info
        numcols, numrows = self.size

        # create open and closed lists
        openlist = []       # cost, coords, parentcoords
        closedlist = []
        inlist = [ [-1 for j in xrange(numrows)] for i in xrange(numcols)]
        nodelist = [ [(0,0, ORTHOGONALMOVE * (abs(end[1]-i) + abs(end[0]-j))) for j in xrange(numrows)] for i in xrange(numcols)]
        parentlist = [ [(-1,-1) for j in xrange(numrows)] for i in xrange(numcols)]
        # todo: do I really need all these lists? this got so messy trying to keep object overhead out of it...

        # add starting location to open list-- hopefully it is on our map...
        openlist.append( (-1, start, False))
        parentlist[start[0]][start[1]] = False
        inlist[start[0]][start[1]] = INOPENLIST

        # loop through map until path is found
        group = random.randrange(5)
        if not group:
            r = lambda x: 0
        else:
            r = random.randrange
        #this is weighted so that the less obvious paths are given some advantage
        #since bottomright is the most direct course to the hero base, that is weighted the lowest
        adjacent = [ (-1, -1, DIAGONALMOVE+r(75)), (0,-1, ORTHOGONALMOVE+r(25)), (1,-1, DIAGONALMOVE+r(20)),
                     (-1, 0, ORTHOGONALMOVE+r(40)),                             (1, 0, ORTHOGONALMOVE+r(50)),
                     (-1, 1, DIAGONALMOVE+r(20)),  (0, 1, ORTHOGONALMOVE+r(25)), (1, 1, DIAGONALMOVE+r(75))]

        swap_adj = 0

        while True:
            swap_adj += 1
            if swap_adj > 25:
                swap_adj = 0
                adjacent = [ (-1, -1, DIAGONALMOVE+r(75)), (0,-1, ORTHOGONALMOVE+r(25)), (1,-1, DIAGONALMOVE+r(20)),
                     (-1, 0, ORTHOGONALMOVE+r(30)),                             (1, 0, ORTHOGONALMOVE+r(50)),
                     (-1, 1, DIAGONALMOVE+r(20)),  (0, 1, ORTHOGONALMOVE+r(25)), (1, 1, DIAGONALMOVE+r(75))]
            # if open heap is empty, no path is available
            if len(openlist) == 0:
                return False

            # pop lowest open node from the heap
            cost, coordinates, parentcoordinates = heapq.heappop(openlist)
            costs = nodelist[coordinates[0]][coordinates[1]]

            # if this is target, build path and return
            if coordinates == end:
                path = []

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
            num = -1
            for modx, mody, modmovecost in adjacent:
                num += 1
                if num in (0, 2, 5, 7):
                    diag = True
                else:
                    diag = False
                newx = coordinates[0] + modx
                newy = coordinates[1] + mody


                # skip if off map
                if newx < 0 or newx >= numcols or newy < 0 or newy >= numrows:
                    continue

                # skip if not walkable
                if blockedmap[newx][newy] >= 2:
                    continue

                # skip if on closed list
                if inlist[newx][newy] == INCLOSEDLIST:
                    continue

                # if on open list
                if inlist[newx][newy] == INOPENLIST:

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
                                if (newx, newy) == end:
                                    openlist.sort()

                                break

                # not on open list
                else:
                    # calculate costs
                    newcost, newmovecost, newhcost = nodelist[newx][newy]
                    newmovecost = costs[1] + modmovecost
                    newcost = newmovecost + newhcost

                    for x in xrange(newx-2, newx+3):
                        for y in xrange(newy-2, newy+3):
                            if not self.out_of_bounds((x, y)):
                                if blockedmap[x][y] == 3:
                                    newcost += 25
                                if diag and blockedmap[x][y] > 1:
                                    newcost += 10000

                    # add to open list
                    heapq.heappush(openlist, (newcost, (newx,newy), coordinates))
                    inlist[newx][newy] = INOPENLIST
                    parentlist[newx][newy] = coordinates
                    # save cost info
                    nodelist[newx][newy] = (newcost, newmovecost, newhcost)


        return False
