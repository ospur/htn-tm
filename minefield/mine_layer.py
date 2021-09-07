import numpy as np
import zmq
import time
import utils


class Mine:
    """
    attributes for the mine detected
    """

    def __init__(self, label, x_coord, y_coord):
        self.label = label
        self.x = x_coord
        self.y = y_coord
        #begin added code DO
        #self.cell = cell
        #end added coode


class Minelayer:

    def __init__(self, mine_dict, mean=[72, -53], cov=[[100, 0], [0, 100]], total_mines=20):
        # for Zmq
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.connect("tcp://127.0.0.1:4003")
        self.mine_dict = mine_dict
        # Mean and the covariance
        self.mean = mean
        self.cov = cov  # diagonal covariance
        self.total_mines = total_mines
        # we dont want to have the mines with the same lables
        self.label_count = 0 # for the mine labels

    def send_message(self):
        print "total_mines =', self.total_mines
        print '----------------------'
        # distribution of the x and the y
        x, y = np.random.multivariate_normal(self.mean, self.cov, self.total_mines).T
        for i in range(x.shape[0]):
            new_mine = Mine(self.label_count, x[i], y[i])
            self.mine_dict.append(new_mine)
            message = [b"AddHazard", b"x=" + str(x[i]) + ",y=" + str(y[i]) + ",label= " + str(self.label_count) + ", type=hazard"]
            self.publisher.send_multipart(message)
            time.sleep(0.1)
            self.label_count +=1

    # Method added by DO
    # change the mean so that pirate ship can move to a new location and lay
    # mines according to a new mean
    def set_mean(self, mean):
        self.mean = mean