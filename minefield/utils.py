def to_coord(cell):
    """
    Convert "cx.y" to x and y
    """

    coord = cell.replace("c", "").split(".")
    return int(coord[0]), int(coord[1])


def to_cell(x, y):
    """
    Convert x and y to "cx.y"
    """

    return "c" + str(x) + "." + str(y)


def is_adjacent(cell1, cell2):
    """
    Determine whether cell1 and cell2 are adjacent (including diagonally)
    """

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


# Computes Manhattan distance
def dist(cell1, cell2):
    cell = cell1
    cell = cell.replace("c", "")
    cell = cell.split(".")
    y0 = int(cell[1])
    x0 = int(cell[0])

    cell = cell2
    cell = cell.replace("c", "")
    cell = cell.split(".")
    y1 = int(cell[1])
    x1 = int(cell[0])

    num1 = abs(x0 - x1)
    num2 = abs(y0 - y1)

    return num1 + num2



# Entire method wrriten by DO
# Takes simulation coordinates and transforms to grid coordinates,
# I.e., if (x, y) is in grid (i, j) will return string associated with
# (i, j). All simulation coordinates in a given grid cell mapped to
# grid coordinates of that cell
def sim_to_grid(x, y):
    # side length of a grid cell
    side = 20
    #need offsets since [-131, 65] is center of top left cell
    start_x = -131 - 10
    start_y = 65 + 10
    found = False
    i = 0
    j = -1
    while (found == False):
        current = start_x + (i * side)
        if ((x >= current) and (x < (current + side))):
            found = True
        else:
            i += 1
    found = False
    while (found == False):
        current = start_y - (j * side)
        if ((y <= current) and (y > (current - side))):
            found = True
        else:
            j += 1
    return "c" + str(i) + "." + str(j)



def build_waypoints(cell1, cell2, build):
    """
    Build a list of adjacent cells from cell1 to cell2
    """

    build.append(cell1)

    x1, y1 = to_coord(cell1)
    x2, y2 = to_coord(cell2)

    if x1 < x2:
        delta_x = 1
    elif x1 == x2:
        delta_x = 0
    elif x1 > x2:
        delta_x = -1

    if y1 < y2:
        delta_y = 1
    elif y1 == y2:
        delta_y = 0
    elif y1 > y2:
        delta_y = -1

    if delta_x == 0 and delta_y == 0:
        return build

    cell1 = to_cell(x1 + delta_x, y1 + delta_y)
    return build_waypoints(cell1, cell2, build)


def build_spiral(cell):
    """
    Build a list of cells (1 to 8)
      4   3   2
      5  cell 1
      6   7   8
    """

    x, y = to_coord(cell)

    n = 8

    count = 1
    i = 0
    build = []
    orient = ['right', 'up', 'left', 'down']
    while (n > 0):
        for j in range(2):
            if (orient[i] == 'right'):
                for k in range (count):
                    x += 1
                    cell = "c" + str(x) + "." + str(y)
                    build.append(cell)
                    n -= 1
                    if (n == 0):
                        return build
                i += 1
            elif (orient[i] == 'up'):
                for k in range (count):
                    y -= 1
                    cell = "c" + str(x) + "." + str(y)
                    build.append(cell)
                    n -= 1
                    if (n == 0):
                        return build
                i = ((i+1) % 4)
            elif (orient[i] == 'left'):
                for k in range (count):
                    x -= 1
                    cell = "c" + str(x) + "." + str(y)
                    build.append(cell)
                    n -= 1
                    if (n == 0):
                        return build
                i = ((i+1) % 4)
            elif (orient[i] == 'down'):
                for k in range (count):
                    y += 1
                    cell = "c" + str(x) + "." + str(y)
                    build.append(cell)
                    n -= 1
                    if (n == 0):
                        return build
                i = ((i+1) % 4)
        count += 1
    return build


def compute_expected_survival(probabilities):
    survival = 0
    x_range = (0, 20)
    y_range = (5, 15)
    for y in range(y_range[0], y_range[1]):
        row_survival = 1
        for x in range(x_range[0], x_range[1]):
            row_survival *= 1 - probabilities[y, x]
        survival += row_survival

    return survival