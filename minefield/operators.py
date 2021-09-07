import time
import utils
import pyhop, pyhop0
import numpy as np

#from world import MoosWorld


# Implements all 8 legal directions in one operator
# Precondition - cell must be one square up/down/left/right adjacent to also include diagonally ajadcent
# current location 
# results in agent moving to cell 
def move(w, cell):
    if (is_adjacent(cell, w.world.agent.cell)):
        # w.apply_agent_action(cell)
        while w.world.agent.cell != cell:
            #time.sleep(0.1)
            # print 'stuck in move operator loop...'
            # print 'w.agent.cell =', w.agent.cell
            # print 'w.world.agent.cell =', w.world.agent.cell
            w.update_world()
            w.apply_agent_action(cell)
        # So remus automatically clears cells it moves to
        #w.update_world()
        print ("The Ship Count is :" + str(w.get_ship_count()))
        w.remove_cell(cell)
        w.update_world()

        x, y = utils.to_coord(w.world.agent.cell)
        if x in range(20) and y in range(20):
            w.agent_traversal[y, x] = 1

        mine_locs = np.zeros((20, 20))

        for mine in w.world.mines:
            mine_cell = utils.sim_to_grid(mine.x, mine.y)
            x, y = utils.to_coord(mine_cell)
            mine_locs[y, x] = 1
        survival = utils.compute_expected_survival(mine_locs)

        merged = np.concatenate((w.agent_traversal, w.pirate_traversal)).flatten()
        datapoint = np.concatenate((merged, [w.mine_prob * 100, survival]))
        datapoint = np.expand_dims(datapoint, axis=0)

        with open('data.txt', 'a') as f:
            np.savetxt(f, datapoint, fmt='%d', delimiter=" ")

        return w
    
    else:
        return False


def arrest(w, name):
    '''
    Wait for 1 seconds and attempt to arrest the named vessel.
    Preconditions: the named vessel is adjacent
    '''

    endtime = time.time() + 1
    while time.time() < endtime:
        if utils.is_adjacent(w.world.agent.cell, w.world.vessels[name].cell):
            if (name == "fisher4"):
                w.world.pirate_flag = True
            return w
        #time.sleep(0.1)
        w.update_world()
    
    return w


def declare_ops():
    pyhop.declare_operators(move, arrest)
    pyhop0.declare_operators(move, arrest)


###################################
# Internal functions go here

# function returns Boolean determining whether two cells are immediately
# left/right/up/down adjacent (same cell is allowed)
# Note current implementation allows diagonal adjacency (can change if needed)
def is_adjacent(cell1, cell2):
    cell = cell1
    cell = cell.replace("c", "")
    cell = cell.split(".")
    #row index is the y coordinate
    row_index0 = int(cell[1])
    #column index is the x coordinate
    column_index0 = int(cell[0])

    cell = cell2
    cell = cell.replace("c", "")
    cell = cell.split(".")
    #row index is the y coordinate
    row_index1 = int(cell[1])
    #column index is the x coordinate
    column_index1 = int(cell[0])

    #Perhaps this would be better:
    num1 = abs(row_index0 - row_index1)
    num2 = abs(column_index0 - column_index1)
    # if ((num1 + num2) > 1):
    #     return False
    # return True

    # diagonal is allowed
    if num1 <= 1 and num2 <=1:
        return True
    
    return False