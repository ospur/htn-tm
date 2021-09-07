import numpy as np
import utils

# Random Agent's Task Modifier

class Critic:
    def __init__(self):
        # status
        # 0 - not clearing
        # 1 - clearing mines
        self.status = 0
        self.agent_traversal = np.zeros((21, 21))
        # self.boat_traversals = np.zeros((4, 20, 20))
        # self.boat_directions = {"fisher" + str(i) : [] for i in range(1, 5)}
        # self.layer_probability = 0.2
        
        
    def ruminate(self, w, tasks):
        self.observe(w)
        # self.estimate_boats()
        # mine_probabilities = self.estimate_mines()

        # expected_survival = self.compute_expected_survival(mine_probabilities)

        print("\n~~~ Ruminating ~~~")

        # print("boat_probabilities:")
        # print(self.boat_probabilities)

        # print("pirate arrested:")
        # print(w.world.pirate_flag)

        # print("expected_survival:")
        # print(expected_survival)
    
        # if w.world.clears and w.world.clears[-1][1] == 0 and self.status == 1:
        #     self.status = 0
 
        # if w.world.clears and w.world.clears[-1][1] > 0 and self.status == 0:
        #     cell = w.world.clears[-1][0]
        #     list_of_cells = utils.build_spiral(cell)
        #     x0, y0 = utils.to_coord(cell)
        #     hypo_mine_probabilities_0 = self.estimate_mines()
        #     hypo_mine_probabilities_0[y0, x0] = 0
        #     hypo_mine_probabilities_1 = self.estimate_mines()
        #     hypo_mine_probabilities_1[y0, x0] = 0
        #     for e in list_of_cells:
        #         x, y = utils.to_coord(e)
        #         hypo_mine_probabilities_0[y, x] = 0
        #         hypo_mine_probabilities_1[y, x] = 1
        #     survival0 = self.compute_expected_survival(hypo_mine_probabilities_0)
        #     survival1 = self.compute_expected_survival(hypo_mine_probabilities_1)

        #     if survival0 - survival1 > 0.2:
        #         tasks.insert(0, ("search_near", cell, self.agent_traversal))
        #         self.status = 1
        #         print("Replanning: search_near added")

        # if tasks[0][0] == "follow":
        #     tasks.remove(tasks[0])

        # if w.world.pirate_flag == False and self.status == 0:
        #     agent_loc = w.world.agent.cell
        #     sus = "fisher" + str(self.boat_probabilities.argmax() + 1)
        #     sus_loc = w.world.vessels[sus].cell

        #     if utils.is_adjacent(agent_loc, sus_loc) and sus == "fisher4":
        #         tasks.insert(0, ("arrest", sus))
        #         print("Replanning: arrest added")                
        #     else:
        #         tasks.insert(0, ("follow", sus))

        if tasks[0][0] == "follow":
            tasks.remove(tasks[0])

        flip = np.random.choice(3, 1)
        if flip == 0:
            destination = utils.to_cell(np.random.randint(20), np.random.randint(5, 15))
            tasks.insert(0, ("search_near", destination, self.agent_traversal))
        elif flip == 1:
            sus = "fisher" + str(np.random.randint(1, 5))
            tasks.insert(0, ("follow", sus))
        elif flip == 2:
            sus = "fisher" + str(np.random.randint(1, 5))
            tasks.insert(0, ("arrest", sus))

        print("current tasks:")
        for t in tasks:
            print(t[0])
                
        return tasks


    def observe(self, w):
        """
        Save the current locations of the agent.
        """

        x, y = utils.to_coord(w.world.agent.cell)
        if x in range(20) and y in range(20):
            self.agent_traversal[y, x] = 1

    
    # def estimate_boats(self):
    #     """
    #     The enemy probability is based on the area visited, horizontal area reach, 
    #     and directional standard deviations.
    #     """
        
    #     visits = np.zeros((4))
    #     reach = np.zeros((4))
    #     direction_std = np.zeros((4))

        
    #     for i in range(4):
    #         boat = "fisher" + str(i + 1)
    #         visits[i] = self.boat_traversals[i].sum()
    #         reach[i] = np.amax(self.boat_traversals[i], axis=0).sum()
    #         direction_std[i] = np.std(self.boat_directions[boat])

    #     visits = visits / visits.sum()
    #     reach = reach / reach.sum()
    #     if direction_std.sum() == 0:
    #         direction_std = np.full((4), 0.25)
    #     else:
    #         direction_std = direction_std / direction_std.sum()

    #     self.boat_probabilities = 0.2 * visits + 0.6 * reach + 0.2 * direction_std
    

    # def estimate_mines(self):
    #     return (self.boat_traversals.T * self.boat_probabilities).T.sum(axis=0) * self.layer_probability


    # def compute_expected_survival(self, probabilities):
    #     survival = 0
    #     x_range = (0, 20)
    #     y_range = (5, 15)
    #     for y in range(y_range[0], y_range[1]):
    #         row_survival = 1
    #         for x in range(x_range[0], x_range[1]):
    #             row_survival *= 1 - probabilities[y, x]
    #         survival += row_survival

    #     return survival