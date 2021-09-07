import zmq
import math
import mine_layer
import time
from pyhop import *
import threading

# begin added code DO
import sys
import os
from operators import *
from methods import *

#end added code DO

import numpy as np
from critic import *
import utils


class Vehicle:
    """
    attributes for the underwater vehicle
    """

    def __init__(self, cell, speed=0, direction=90, status="Active", name="ship"):
        # format : cx.y
        self.cell = cell
        self.speed = speed
        self.direction = direction
        self.name = name
        self.status = status     


class MoosWorld:
    """
    This class interfaces with moos
    """

    def __init__(self, state, friendly_delay, mine_prob, init_enemy=False, init_friendly_vessels=False, init_fisher_vessels=False):
        # probability of mines placed  by the pirate
        self.mine_prob = mine_prob

        self.agent_traversal = np.zeros((20, 20))
        self.pirate_traversal = np.zeros((20, 20))

        # lock for threading
        self.lock = threading.Lock()

        # pyhop state
        self.world = state

        # initialize the cells of the grid with their corresponding way_points
        self.grid = self.calculate_grids()

        #delay until friendly vessels start moving
        self.delay = friendly_delay

        # initialize the socket connections
        self.declare_connections()

        self.update_world()


        # initialize the enemy behavior as a thread
        if init_enemy:
            enemy_laying_mines = threading.Thread(target=self.enemy_movement)

        # for ship behavior thread
        if init_friendly_vessels:
            ship_traversal = threading.Thread(target=self.ship_movement)

        # for fisher vessels behavior
        if init_fisher_vessels:
            fisher_traversal = threading.Thread(target=self.fisher_movement)

        # execute the thread
        # This should probably be protected with an if init_enemy. DO
        # Q: thead line have to be executed before socket line? else can put
        # in same if block DO
        if init_enemy:
            enemy_laying_mines.start()

        # waypoints for the friendly vessels
        self.way_points_friendly_vessels = []

                # waypoints for the fisher vessels
        self.way_points_fisher_vessels = []

        if init_friendly_vessels:
            ship_traversal.start()

        if init_fisher_vessels:
            fisher_traversal.start()


    def declare_connections(self):
        """
        Establish the socket connections required with moos
        :return:
        """

        # Zeromq connection with the moos for perception
        context = zmq.Context()
        self.subscriber = context.socket(zmq.SUB)
        self.subscriber_mine = context.socket(zmq.SUB)

        # to get vehicle reports
        self.subscriber.setsockopt(zmq.SUBSCRIBE, '')
        self.subscriber.setsockopt(zmq.RCVTIMEO, -1)
        self.subscriber.setsockopt(zmq.CONFLATE, 1)
        self.subscriber.connect("tcp://127.0.0.1:4999")

        # to get mine reports
        self.subscriber_mine = context.socket(zmq.SUB)
        self.subscriber_mine.setsockopt(zmq.SUBSCRIBE, '')
        self.subscriber_mine.setsockopt(zmq.RCVTIMEO, 5)
        self.subscriber_mine.connect("tcp://127.0.0.1:4998")


        # Zeromq connection with the moos for action
        self.publisher = context.socket(zmq.PUB)
        self.publisher.connect("tcp://127.0.0.1:5999")

        # Zeromq connection with the fisher (enemy) for action
        self.publisher_enemy = context.socket(zmq.PUB)
        self.publisher_enemy.connect("tcp://127.0.0.1:4003")

        # Zeromq connection with the fisher (enemy) for perception
        self.subscriber_enemy  = context.socket(zmq.SUB)
        self.subscriber_enemy.setsockopt(zmq.SUBSCRIBE, '')
        self.subscriber_enemy.setsockopt(zmq.RCVTIMEO, -1)
        self.subscriber_enemy.setsockopt(zmq.CONFLATE, 1)
        self.subscriber_enemy.connect("tcp://127.0.0.1:3003")

        # Zeromq connection with the fisher vessels for action
        self.publisher_fisher_vessels = []
        self.subscriber_fisher_vessels = []
        for i in range(0,3):
            connection  = context.socket(zmq.PUB)
            connection.connect("tcp://127.0.0.1:400"+str(i))
            self.publisher_fisher_vessels.append(connection)
            #time.sleep(0.1)

        for i in range(0,3):
            connection = context.socket(zmq.SUB)
            connection.setsockopt(zmq.SUBSCRIBE, '')
            connection.setsockopt(zmq.RCVTIMEO, -1)
            connection.setsockopt(zmq.CONFLATE, 1)
            connection.connect("tcp://127.0.0.1:300"+str(i))
            self.subscriber_fisher_vessels.append(connection)
            #time.sleep(0.1)

        # Zeromq connection with the friendly vessels for action
        self.publisher_friendly_vessels = []
        self.subscriber_friendly_vessels = []
        for i in range(0,10):
            connection  = context.socket(zmq.PUB)
            connection.connect("tcp://127.0.0.1:600"+str(i))
            self.publisher_friendly_vessels.append(connection)
            #time.sleep(0.1)

        for i in range(0,10):
            connection = context.socket(zmq.SUB)
            connection.setsockopt(zmq.SUBSCRIBE, '')
            connection.setsockopt(zmq.RCVTIMEO, -1)
            connection.setsockopt(zmq.CONFLATE, 1)
            connection.connect("tcp://127.0.0.1:500"+str(i))
            self.subscriber_friendly_vessels.append(connection)
            #time.sleep(0.1)

    def calculate_grids(self, grid_size=20, distance=20):
        """
        :param grid_size: dimensions of the grid
        :param distance: distance between each cell
        :return: returns the way_points associated with the grid
        """
        # this is the center point of the first cell in the grid
        start_point = [-131, 65]

        # to store the way_points associtated with the cell position
        grid = []

        x = start_point[0] - distance
        y = start_point[1] + distance
        # loop for the vertical grid i.e c00, c10, c20 ect.
        for i in range(0, grid_size):
            y = y - distance
            x = start_point[0] - distance
            # loop for the horizontal grid i.e c00, c01, c02
            row = []
            for j in range(0, grid_size):
                x = x + distance
                row.append([x, y])
            grid.append(row)

        return grid



    # Entire method wrriten by DO
    # Takes simulation coordinates and transforms to grid coordinates,
    # I.e., if (x, y) is in grid (i, j) will return string associated with
    # (i, j). All simulation coordinates in a given grid cell mapped to
    # grid coordinates of that cell
    def sim_to_grid(self, x, y):
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

    #this method is the same update/initialization paradigm as the
    #previous method DO
    def set_vehicle_parameters(self, vehicle_pos, name):
        """

        :param vehicle_pos: The string containing all the parameters of a vehicle
        :param name: the name of the vehicle
        :return: updates the parameters of the world
        """

        #decomposes the sim-genereated string in vehicle-pos var DO
        x, y, speed, direction,status = vehicle_pos.split(",")
        x = float(x.split(":")[1])
        y = float(y.split(":")[1])
        speed = float(speed.split(":")[1])
        direction = float(direction.split(":")[1])
        status = status.split(":")[1]

        #update DO
        if name in self.world.vessels:
            # self.world.vessels[name].cell = self.calculate_cell(x, y)
            # Changed from incorrect calculate_cell(x, y) to sim_to_grid
            self.world.vessels[name].cell = self.sim_to_grid(x, y)
            self.world.vessels[name].speed = speed
            self.world.vessels[name].direction = direction
            self.world.vessels[name].status = status
        #else initialize DO
        else:
            #cell = self.calculate_cell(x, y)
            # Changed from incorrect calculate_cell(x, y) to sim_to_grid
            cell = self.sim_to_grid(x, y)
            vehicle = Vehicle(cell, speed, direction,status, name)
            self.world.vessels[name] = vehicle

    # this updates a singular "subscriber" -- could be friendly or enemy ship
    # probably NOT remus though DO
    def get_vessel(self, subscriber, name, verbose=1):
        """

        :param subscriber: subscriber for fisher vessel
        :param name: name of the vessel
        :return:
        """

        # only first update worked (and still required a lot of looping
        # after first initialization, just goes into infintie loop for fisher1
        # update 08.19: seems to update quickly now
        while True:

            try:
                fisher_pos = subscriber.recv()
                #time.sleep(0.1)
                self.set_vehicle_parameters(fisher_pos, name)
                break
            except Exception as e:
                if verbose > 1:
                    #    print ("connection not established .... Retry")
                    print 'in get_vessels -- failed...', name

            ###4)
        #print 'successful updating of', name

        # try:
        #     fisher_pos = self.subscriber.recv()
        #     self.set_vehicle_parameters(fisher_pos, name)
        # except:
        #     #if verbose > 1:
        #     #    print ("connection not established .... Retry")
        #     print 'in get_vessels -- failed...', name

    # Note updating of each vessel needs to be hard coded here
    def update_vessels(self, verbose=1):
        """
        :return: updating the dictionary with vessels
        """
        if verbose > 1:
            print ("Updating fishing vessels")

        for i in range(len(self.subscriber_fisher_vessels)):
             self.get_vessel(self.subscriber_fisher_vessels[i], "fisher" +str(i+1))

        if verbose > 1:
            print ("Updating enemy vessel")
        # for enemy vessel
        self.get_vessel(self.subscriber_enemy, "fisher4")

        if verbose > 1:
            print ("Updating friendly vessels")
        # update friendly vessels
        # please remove this, if you dont want any shipping vessels to be updated
        # If a ship hits a mine then the X,Y coordinates will be -1700, -1500
        # If you read the above coordinates that indicates the ship is hit by a mine
        # I believe this updating is not working correctly DO
        for i in range(len(self.subscriber_friendly_vessels)):
             self.get_vessel(self.subscriber_friendly_vessels[i], "ship" +str(i))

    def check_if_new_mine(self, mine, verbose=1):
        """
        :param mine: instance of the Mine class
        :return: boolean : checks if it is the new mine
        """
        # Begin new method DO
        #Added base case of 0 mines... DO
        if len(self.world.mines) == 0:
            return True

        #End added code DO


        #why not use a dict for faster lookup DO?
        for each in self.world.mines:
            if each.label == mine.label:
                #return True
                # corrected logic - changed return to False DO
                return False

        #return False
        #corrected logic - changed return to True  DO
        return True


    def remove_mine(self, mine):
        """

        :param mine: instance of the mine
        :return: removes the mine from the dictionary
        """
        #Again, dict for efficiency? DO
        for each in self.world.mines:
            if each.label == mine.label:
                #remove mine from python interface DO
                self.world.mines.remove(each)
                #sends message to remove mine in simulation DO
                self.publisher.send_multipart([b"RemoveHazard", str(mine.label)])
                #time.sleep(0.1)

    # First added method DO
    # Takes a cell and removes all mines in cell
    def remove_cell(self, cell):
        print 'in remove mines...'
        #need to use list() to avoid removing elts while iterating

        # count the number of mines removed when this function is called
        mine_count = 0

        for mine in self.world.mines:
            # print 'sim_to_grid(' + str(mine.x) + "," +  str(mine.y)+ ')=', self.sim_to_grid(mine.x, mine.y)
            # print 'cell =', cell
            if (self.sim_to_grid(mine.x, mine.y) == cell):
                # print 'mine terminated...------------------------------'
                #self.remove_mine(mine)
                self.world.mines.remove(mine)
                self.publisher.send_multipart(
                    [b"RemoveHazard", str(mine.label)])
                #time.sleep(0.1)
                mine_count += 1
   
        self.world.clears.append((cell, mine_count))


    # def update_mines(self):
    #     """

    #     :return: Updates the dictionary if there are any mines
    #     """

    #     #Attempting to add a return value that signals if a mine was detected DO
    #     # 0 - no mine added
    #     # 1 = mine added
    #     #ret = 0
    #     try:
    #         mine_report = self.subscriber_mine.recv()
    #         mine_x, mine_y, mine_label = mine_report.split(":")[1].split(",")
    #         mine_x = float(mine_x.split("=")[1])
    #         mine_y = float(mine_y.split("=")[1])
    #         mine_label = mine_label.split("=")[1]
    #         print 'label of mine at x =', mine_x, 'y =', mine_y, 'is', mine_label

    #         # Added mine_cell line DO
    #         #mine_cell = self.calculate_cell(mine_x, mine_y)
    #         #new_mine = Mine(mine_x, mine_y, mine_cell, mine_label)
    #         # End added code
    #         new_mine = Mine(mine_x, mine_y, mine_label)


    #         print 'Attempting to enter add new mine code...'
    #         if self.check_if_new_mine(new_mine):
    #             print 'in adding mine code...' #DO
    #             # Debugging Code Begin 01
    #             cell = self.sim_to_grid(mine_x, mine_y)

    #             if cell not in self.world.mine_dict:
    #                 self.world.mine_dict[cell] = [new_mine]
    #             else:
    #                 self.world.mine_dict[cell].append(new_mine)
    #             # Debugging Code End 01
    #             #self.world.mines.append()
    #             # corrected logic -- added argument new_mine to append DO
    #             self.world.mines.append(new_mine) #DO
    #             #added return value DO
    #             return 1
    #         #added return value DO
    #         # value should be 1 because we should try again even if we hit
    #         # duplicate mine -- maybe sim returns duplicate mines in this
    #         # for unknown technical reasons
    #         print 'hit duplicate mine return...'
    #         return 
    #     except Exception as e:
    #         #begin added code DO
    #         # added warning DO
    #         print 'No mines received'
    #         # print 'Warning - sent to exception code in update_mines'
    #         # print(e)
    #         return 0
    #         #end added code DO
    #         pass
    #     #added safety return value DO
    #     print 'hit safety return value in update mines code-----------'
    #     return 0

    def update_world(self):
        """
        :return: the updated state from the moos
        """

        #lock it

        self.lock.acquire()
        try:

            # updates the state of the remus
            self.update_agent()

            # updates the state of all the fisher vessels
            # this includes enemy posing as fishing vessel DO
            self.update_vessels()

            # if detected updates the state of the mines
            # self.update_mines()

            #Adding while loop to detect all mines placed DO
            # while (self.update_mines() == 1):
                # pass
        finally:
            #release lock
            self.lock.release()

        # new idea: force a set number of calls to update_mines to fail before
        # we give up -- testing deems this unnecessary
        # count = 0
        # thres = 5
        # while (count < thres):
        #     if (self.update_mines() == 0):
        #         count += 1
        #     else:
        #         count = 0

    def update_agent(self, verbose=1):
        """
        :return: the remus state from the moos
        """
        try:
            # get update info from the sim DO
            remus_position = self.subscriber.recv()
            #time.sleep(0.01)
            #decompose update info from sim DO
            x, y, speed, direction, status = remus_position.split(",")
            x = float(x.split(":")[1])
            y = float(y.split(":")[1])
            speed = float(speed.split(":")[1])
            direction = float(direction.split(":")[1])
            status = status.split(":")[1]

            # if block is standard update code for remus DO
            if self.world.agent:
                #self.world.agent.cell = self.calculate_cell(x, y)
                self.world.agent.cell = self.sim_to_grid(x,y)
                #adding print statements for debugging DO
                #print 'agent_x =', x
                #print 'agent_y =', y
                # print 'agent_cell =', self.world.agent.cell
                # print 'my_agent_cell =', self.sim_to_grid(x, y)
                self.world.agent.speed = speed
                self.world.agent.direction = direction
            #else block appears to be initialization code DO
            else:
                #cell = self.calculate_cell(x, y)
                cell = self.sim_to_grid(x, y)
                print 'agent_x =', x
                print 'agent_y =', y
                print 'agent_cell =', cell
                print 'my_agent_cell =', self.sim_to_grid(x, y)
                remus = Vehicle(cell, speed, direction, status, "remus")
                self.world.agent = remus

        except:
            if verbose > 1:
                print ("connection not established in update_agent.... Retry")

    # Analogous to apply_enemy_action. Sends message to move to cell location DO
    # Cmt: so this is called, python sends a message to the simulation,
    # and then the simulation executes the commands sent to it by this python
    # code...
    def apply_agent_action(self, cell):
        """

        :param cell: The location of the cell remus should go to
        :return:
        """
        # print 'ENTERING APPLY_AGENT_ACTION...'
        # print 'original cell =', cell


        # get the grid indexes from the cell
        cell = cell.replace("c", "")
        cell = cell.split(".")
        #row_index = int(cell[0])
        #column_index = int(cell[1])
        #print 'row_index =', row_index
        #print 'col_index =', column_index
        # incorrect logic switching row and column indicies... DO
        # reason: y coordinate is row_index and x coordinate is col index
        row_index = int(cell[1])
        column_index = int(cell[0])
        point = self.grid[row_index][column_index]
        message = [b"Vehicle", b"point = " + str(point[0]) + "," + str(point[1]) + "# speed= 1.5"]
        #time.sleep(0.1)
        self.publisher.send_multipart(message)
        #time.sleep(0.1)
        #adding return value DO
        #list format [x, y]
        #return point

    # Current working assumption - takes the cell and sends a message to the
    # the simulation to move the enemy to the associated point  DO
    def apply_enemy_action(self, cell):
        """

        :param cell: The location of the cell enemy should go to
        :return:
        """
        # get the grid indexes from the cell
        cell = cell.replace("c", "")
        cell = cell.split(".")
        #row_index = int(cell[0])
        #column_index = int(cell[1])
        # incorrect logic switching row and column indicies... DO
        # reason: y coordinate is row_index and x coordinate is col index
        row_index = int(cell[1])
        column_index = int(cell[0])
        point = self.grid[row_index][column_index]
        # print 'in apply_enemy_action...'
        # print 'point[0] =', point[0]
        # print 'point[1] =', point[1]
        message = [b"Vehicle", b"point = " + str(point[0]) + "," + str(point[1]) + "# speed= 1.0"]
        #time.sleep(0.1)
        self.publisher_enemy.send_multipart(message)
        #time.sleep(0.1)

    # Sends enemy to waypoint and loops until arrival - higher level than
    # message sending in apply_enemy_action DO
    #changed waypoint to waypoints
    def enemy_waypoint_behavior(self, waypoints, layer):
        """
        :param way_point: List of way_points enemy should travel
        :return:
        """
        #so each is just the typical cell coordinate string, since
        # way_points is a list of such coordinates
        for each in waypoints:
            #abort if pirate is captured
            if (self.world.pirate_flag == True):
                return
            ###0.1)
            # So this sends the message to move to the waypoint... DO
            # self.apply_enemy_action(each)
            # x=0
            # y=0
            # And so this loops until enemy ship arrives... DO
            # Corrected use of dangerous calculate_cell method DO
            #while not (self.calculate_cell(x, y) == each):
            while self.world.vessels["fisher4"].cell != each:
                """
                try:
                    enemy_pos = self.subscriber_enemy.recv()
                    x, y, speed, direction, status = enemy_pos.split(",")
                    x = float(x.split(":")[1])
                    y = float(y.split(":")[1])
                except:
                    # print 'stuck in enemy loop...'
                    # print 'x_enemy =', x
                    # print 'y_enemy =', y
                    # print 'self.sim_to_grid(x, y) =', self.sim_to_grid(x, y)
                    # print 'each =', each
                    ###1)
                    pass
                """
                self.apply_enemy_action(each)
                self.update_world()
            
            x, y = utils.to_coord(self.world.vessels["fisher4"].cell)
            if x in range(20) and y in range(20):
                self.pirate_traversal[y, x] = 1

            flip = np.random.choice(2, 1, p=[1 - self.mine_prob, self.mine_prob])
            if flip == 1:
                print("\nlaying mines")
                x, y = utils.to_coord(each)
                mean = self.grid[y][x]
                layer.set_mean(mean)
                layer.send_message()

    # Sends each friendly ship to waypoints
    # message sending here DO
    #waypoints
    def ship_way_points_behavior(self, publisher, way_points, speed, delay=0):
        """
        :param publisher : publisher associated for a ship
        :param way_point: List of way_points enemy should travel
        :return:
        """
        #so each is just the typical cell coordinate string, since
        # way_points is a list of such coordinates
        # points variable is to accumulate all the points to send
        # example repr of points  "points = pts={60,-40:60,-160:150,-160:180,-100:150,-40}"
        points = b"points = pts={"
        for cell in way_points:
            # get the grid indexes from the cell
            cell = cell.replace("c", "")
            cell = cell.split(".")
            #row_index = int(cell[0])
            #column_index = int(cell[1])
            # incorrect logic switching row and column indicies... DO
            # reason: y coordinate is row_index and x coordinate is col index
            row_index = int(cell[1])
            column_index = int(cell[0])
            point = self.grid[row_index][column_index]
            points = points + str(point[0]) + "," + str(point[1]) + ":"

        # remove the column from the end of the points string and add flower braces
        points = points[:-1] + "}"

        # create message
        message = [b"Vehicle", points + "# speed= " + str(speed)]

        # send the message
        #time.sleep(0.1)
        publisher.send_multipart(message)
        #time.sleep(0.1)
        publisher.send_multipart(message)

        time.sleep(delay)

    # Currently 3 hard-coded Guassian distributions are placed
    def enemy_movement(self):
        """
        The enemy movement and mine laying activity
        :return:
        """
        # generate random waypoints

        # changed waypoint to waypoints DO
        #way_points = ["c2.19", "c3.19", "c4.19", "c4.18", "c4.17", "c4.16", "c5.16", "c5.15", "c5.14",
             #"c5.13", "c5.12", "c5.11", "c5.10"]
        # way_points = ["c18.1", "c18.2", "c17.2", "c16.2", "c16.3", "c15.3", "c14.3"]

        #  pass mine_layer to the function
        layer = mine_layer.Minelayer(mine_dict=self.world.mines)

        while not self.world.pirate_flag:
            current = self.world.vessels["fisher4"].cell
            destination = utils.to_cell(np.random.randint(20), np.random.randint(5, 15))
            waypoints = utils.build_waypoints(current, destination, [])
            print("\nEnemy waypoints:")
            print(waypoints)
            self.enemy_waypoint_behavior(waypoints, layer)

        # This effectively defines the trajectory to get to the mean of the
        # Guassian DO
        # travel to all the way_points (one by one)
        

        #abort if pirate is captured
        # if (self.world.pirate_flag == True):
        #     return

        # lay mines
        # cell = way_points[-1]
        # cell = cell.replace("c", "")
        # cell = cell.split(".")
        # So parameters of this Guassian are hard coded... DO
        # ideally would have more realistic way of "mining an area" with a
        # Guassian distribution DO
        #layer = mine_layer.Minelayer(self.grid[int(cell[0])][int(cell[1])])
        #corrected indexing into grid logic DO
        # layer = mine_layer.Minelayer(self.grid[int(cell[1])][int(cell[0])])
        # layer.send_message()

        # 2nd Guassian Code
        # way_points = ["c13.3", "c13.4", "c12.4", "c12.5", "c11.5", "c11.6", "c10.6"]
        # self.enemy_way_point_behavior(way_points, layer)

        #abort if pirate is captured
        # if (self.world.pirate_flag == True):
        #     return

        # cell = way_points[-1]
        # cell = cell.replace("c", "")
        # cell = cell.split(".")
        # mean = self.grid[int(cell[1])][int(cell[0])]
        # layer.set_mean(mean)
        # layer.send_message()

        # 3rd Guassian
        # way_points = ["c10.6", "c10.7", "c10.8", "c10.9", "c10.10", "c10.11", "c11.11", "c12.11", "c13.11"]
        # self.enemy_way_point_behavior(way_points, layer)

        #abort if pirate is captured
        # if (self.world.pirate_flag == True):
        #     return
        # cell = way_points[-1]
        # cell = cell.replace("c", "")
        # cell = cell.split(".")
        # mean = self.grid[int(cell[1])][int(cell[0])]
        # layer.set_mean(mean)
        # layer.send_message()

        # Code for pirate ship to "exit" (ie move off screen) simulation
        # way_points = ["c13.11", "c13.12", "c13.13"]
        # self.enemy_way_point_behavior(way_points, layer)

        # return to its original path
        # Why are we looping this trajectory ? DO
        # while True:
        #     way_points.reverse()
        #     self.enemy_way_point_behavior(way_points)

    def get_ship_count(self):
        """
        :return: the number of ships that are active
        :functionality: iterate over the vessels and check their status
        """
        count = 0
        self.update_world()
        for vessel in self.world.vessels:
            # get just the ships
            if vessel.startswith("ship") and not self.world.vessels[vessel].status == "Wreck":
                count += 1
        return count

    def check_experiment_completed(self):
        # see if the shipping vessels have finished traversing
        count = 0
        no_of_vessels = 0
        for vessel in self.world.vessels:
            # get just the ships
            if vessel.startswith("ship"):
                no_of_vessels +=1
                if self.world.vessels[vessel].status == "Wreck" or self.world.vessels[vessel].speed == 0:
                    count += 1
        if count == no_of_vessels:
            return True
        else:
            return False

    def ship_movement(self):
        """
        Ships movement
        :return:
        """
        # please adjust the sleep for the delay
        time.sleep(self.delay)
        # this is for calculating way_points
        # Daniel please write your own code for the way_points or move it somewhere
        # self.way_points_friendly_vessels contains the list in lists
        # each list contains the way_points for each vehicle
        # for example
        # [["c1.2", "c1.3"], ["c2.2", "c2.3"]....]
        for y in range(5, 15):
            waypoints = []
            for x in range (1, 20):
                cell = utils.to_cell(x, y)
                waypoints.append(cell)
            self.way_points_friendly_vessels.append(waypoints)

        # this is to publish the way_points 1 is the speed
        speed = 0.5
        for i in range(0, len(self.publisher_friendly_vessels)):
            self.ship_way_points_behavior(self.publisher_friendly_vessels[i],
                                          self.way_points_friendly_vessels[i], speed)

        # see if the ships have reached the other end of the shore
        
        while True:
            time.sleep(2)
            if (self.check_experiment_completed()):

                # compute the total number of mines cleared
                mines_cleared = 0

                for item in self.world.clears:
                    mines_cleared += item[1]
            
                # write results to a file
                # file_object = open('results.txt', 'a')
                # file_object.write(str(self.get_ship_count()) + "\n")
                # file_object.close()
                # break
                os._exit(1)

    def fisher_movement(self):
        """
        fisher movement
        :return:
        """
        # this is for calculating way_points
        # Daniel please write your own code for the way_points or move it somewhere
        # self.way_points_fisher_vessels contains the list in lists
        # each list contains the way_points for each vehicle
        # for example
        # [["c1.2", "c1.3"], ["c2.2", "c2.3"]....]

        #  get current location of the fishers and move vertically
        for i in range(1, 4):
            boat = "fisher" + str(i)
            x0, y0 = utils.to_coord(self.world.vessels[boat].cell)
            waypoints = []
            for y in range(20):
                cell = utils.to_cell(x0, y)
                waypoints.append(cell)
            self.way_points_fisher_vessels.append(waypoints)

        # for i in range(13,16):
        #     way_points = []
        #     for j in range (1, 20):
        #         way_points.append("c"+str(i)+"."+str(j))
            
        # this is to publish the way_points 1 is the speed
        speed = 0.5
        while True:
            for i in range(0, len(self.publisher_fisher_vessels)):
                self.ship_way_points_behavior(self.publisher_fisher_vessels[i],
                                          self.way_points_fisher_vessels[i], speed)

            #time.sleep(0.2)




def main():

    # 5 second delay requested by Sampath
    # keep it 10 for better initial communication (by sampath)
    #time.sleep(10)

    #begin added code DO

    print 'pid =', os.getpid()
    declare_ops()

    #end added code DO

    friendly_delay = 20

    state = State('state')
    state.vessels = {}

    state.agent = Vehicle("c0.0")
    #state.mines = {} DO
    state.mines = []


    # state.mine_dict = {}
    # pirate flag is indicates whether pirate is arrested
    # pirate is intially not arrested so flag is initially False
    state.pirate_flag = False

    # flag indicates whether moving according to guassian or
    # moving between guassians
    state.guass_flag = False

    state.clears = []
    


    mine_prob = np.random.choice([0.1], 1)[0]
    # True parameter runs the thread for the movement of enemy
    w = MoosWorld(state, friendly_delay, mine_prob, True, True, True)
    #w = MoosWorld(state, False) won't work DO


    # empirically observed takes remus (seems to extend to friendly vessels
    # -- got time of about 2.5 as well) about 2.58s to move through a cell
    # and friendlies take about 5 cells to get to Guassians so 5 x 2.58 =~ 13
    # other_delay = 13
    # state.time_limit = w.delay + other_delay

    # w.apply_agent_action("c9.1")
    # while (w.world.agent.cell != "c9.1"):
        ###0.2)
        # print 'cell =', w.world.agent.cell
        #w.update_agent(verbose = 2)
        # w.update_world()
        # w.apply_agent_action("c9.1")
    # time1 = time.time()
    # w.apply_agent_action("c9.2")
    # while (w.world.agent.cell != "c9.2"):
    #     ###0.2)
    #     #print 'cell =', w.world.agent.cell
    #     w.update_agent()
    # time2 = time.time()
    # print 'Sucess: cell =', w.world.agent.cell
    print '-----------------------------'
    print ("The Ship Count is :"),
    print (w.get_ship_count())
    # print 'time was', (time2 - time1)

    # by reversing, we can use pop and append to make the list function
    # like a stack when traj is passed around in methods
    # t_l =  w.delay + other_delay
    # t_s = 2.58
    # start = "c9.1"
    # mu = ["c14.3",  "c10.6", "c13.11"]
    # traj = generate_traj(t_l, t_s, start, mu)

    # print traj

    # traj.reverse()

    #build = [('wait_arrest_test', w)]
    # build = [('move_traj', w, traj)]

    print("the methods are")
    print_methods()
    print("\n")

    build = [("random_moves",)]

    critic = Critic()
    
    #  load the saved array for data if it exists

    # A thread to collect data
    # t = threading.Thread(target=collect_data, args=(w, critic, 5, mine_prob))
    # t.start()

    Info = pyhopT(w, build, critic, verbose=0)
    #plan = Info[0]

    print("tasks done")
    #print (plan)

    # to make sure that the program is successfully executing
    #file_object = open('test.txt', 'a')
    #file_object.write('Experiment status: True\n')
    #file_object.close()

    #os._exit(1)

    

    '''
    To update the world (This updates dictionaries)
    w.update_world()
    
    To know how many ships are active
    w.get_ship_count()

    To move remus
    w.apply_agent_action(cx.y)

    To remove mines
    w.remove_mine(mine)

    To adjust the way_points of the enemy vessel
    modify the list way_point from the function enemy_movement
    Note.. enemy_movement is a thread that runs when you initialize the MoosWorld


    '''




#####################################
# Internal helper functions go here

# t_l is the total we have to work with
# start - starting cell
# mu is a list containing the means of the guassians
# t_s time is takes to traverse a square
def generate_traj(t_l, t_s, start, mu):
    # number of Guassians to be cleared -- 3 as of current
    n_guass = len(mu)
    n_squares = float(t_l) / float(t_s)
    print 'n_squares =', n_squares
    n_squares = math.ceil(n_squares)
    transit = 0
    current1 = start
    for i in range(n_guass):
        current2 = mu[i]
        transit += dist(current1, current2)
        current1 = current2
    # total # of squares spent in guassians
    # ACTION NEEDED - note if this is negative then no time for transit
    total = n_squares - transit
    # squares per Guassian
    per_guass = math.ceil(float(total) / float(n_guass))
    print 'per_guass =', per_guass

    traj = []

    current1 = start
    for i in range(n_guass):
        current2 = mu[i]
        traj.extend(transit_traj(current1, current2))
        # the 11 should really be per_guass -- change later
        traj.extend(guass_traj(current2, 11))
        current1 = traj[len(traj)-1]

    return traj

# mu is the mean of the Guassian
# per_guass is the number of squares we are allowed to traverse
def guass_traj(mu, n):
    cell = mu
    cell = cell.replace("c", "")
    cell = cell.split(".")
    y = int(cell[1])
    x = int(cell[0])

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

def transit_traj(start, end):
    cell = start
    cell = cell.replace("c", "")
    cell = cell.split(".")
    y0 = int(cell[1])
    x0 = int(cell[0])

    cell = end
    cell = cell.replace("c", "")
    cell = cell.split(".")
    y1 = int(cell[1])
    x1 = int(cell[0])

    build = []

    if (y0 == y1):
        pass
    elif (y0 < y1):
        d = y1 - y0
        for i in range (1, d+1):
            y0 += 1
            cell = "c" + str(x0) + "." + str(y0)
            build.append(cell)
    else:
        d = y0 - y1
        for i in range (1, d+1):
            y0 -= 1
            cell = "c" + str(x0) + "." + str(y0)
            build.append(cell)

    # Here y0 and y1 should have the same value
    if (x0 == x1):
        pass
    elif (x0 < x1):
        d = x1 - x0
        for i in range (1, d+1):
            x0 += 1
            cell = "c" + str(x0) + "." + str(y0)
            build.append(cell)
    else:
        d = x0 - x1
        for i in range (1, d+1):
            x0 -= 1
            cell = "c" + str(x0) + "." + str(y0)
            build.append(cell)
    #print 'about to return build:'
    #print build
    return build


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





def collect_data(w, critic, frequency, mine_prob):
    main_alive = True
    while main_alive:
        time.sleep(frequency)

        mine_locs = np.zeros((20, 20))

        # mine_dict has keys of the form "cx.y" and the value is a Mine object
        # print("in collecting data")
        # print(w.world.mine_dict)
        # if w.world.mine_dict = {}
        for mine in w.world.mines:
            # print("in collecting data")
            # print(mine)
            mine_cell = utils.sim_to_grid(mine.x, mine.y)
            x, y = utils.to_coord(mine_cell)
            mine_locs[y, x] = 1
        survival = critic.compute_expected_survival(mine_locs)

        merged = np.concatenate((critic.boat_traversals[3], critic.agent_traversal)).flatten()
        datapoint = np.concatenate((merged, [mine_prob * 100, survival]))
        datapoint = np.expand_dims(datapoint, axis=0)

        with open('data.txt', 'a') as f:
            np.savetxt(f, datapoint, fmt='%d', delimiter=" ")

        for i in threading.enumerate():
            if i.name == "MainThread":
                main_alive = i.is_alive()




# this must go at end otherwise main method does not see helper functions
if __name__ == '__main__':
    main()
