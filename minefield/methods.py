import numpy as np
import pyhop, pyhop0
import utils

def random_moves(w):
    destination = utils.to_cell(np.random.randint(20), np.random.randint(5, 15))
    build = []
    build.append(("move_diag", destination))
    build.append(("random_moves",))
    return build

pyhop.declare_methods("random_moves", random_moves)
pyhop0.declare_methods("random_moves", random_moves)


def search_near(w, cell, traversal):
    """
    Move to neighboring cells of 'cell'; only visit ones that haven't been visited and non-diagonally
    """

    build = []

    cells = utils.build_spiral(cell)

    for c in cells:
        x, y = utils.to_coord(c)
        if traversal[y, x] == 0:
            build.append(("move_diag", c))
    
    return build

pyhop.declare_methods("search_near", search_near)


def move_diag(w, destination):
    x0, y0 = utils.to_coord(w.world.agent.cell)
    x1, y1 = utils.to_coord(destination)

    if x0 < x1:
        delta_x = 1
    elif x0 == x1:
        delta_x = 0
    elif x0 > x1:
        delta_x = -1

    if y0 < y1:
        delta_y = 1
    elif y0 == y1:
        delta_y = 0
    elif y0 > y1:
        delta_y = -1

    build = []

    if delta_x == 0 and delta_y == 0:
        return build
    
    cell = utils.to_cell(x0 + delta_x, y0 + delta_y)
    build.append(("move", cell))
    build.append(("move_diag", destination))
    return build

pyhop.declare_methods("move_diag", move_diag)
pyhop0.declare_methods("move_diag", move_diag)


def follow(w, name):
    """
    Move to the named vessel's location
    """

    x0, y0 = utils.to_coord(w.world.agent.cell)
    x1, y1 = utils.to_coord(w.world.vessels[name].cell)

    if x0 < x1:
        delta_x = 1
    elif x0 == x1:
        delta_x = 0
    elif x0 > x1:
        delta_x = -1

    if y0 < y1:
        delta_y = 1
    elif y0 == y1:
        delta_y = 0
    elif y0 > y1:
        delta_y = -1

    build = []

    if delta_x == 0 and delta_y == 0:
        return build
    
    cell = utils.to_cell(x0 + delta_x, y0 + delta_y)
    build.append(("move", cell))
    build.append(("follow", name))
    return build

pyhop.declare_methods("follow", follow)