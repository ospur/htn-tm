import numpy as np
import utils

class Critic:
    def __init__(self):
        self.rain_list = []
        self.call_num = 0
        
    def ruminate(self, env, tasks):
        self.call_num += 1
        self.observe(env)
        # self.estimate_boats()
        # mine_probabilities = self.estimate_mines()
        # print("in ruminate", self.call_num)
        # rain_prob = env.rain_prob
        rain_prob = 0.5
        # rain_prob = 0
        # if self.rain_list:
        #     num_rain = 0
        #     for i in self.rain_list:
        #         if i == True:
        #             num_rain += 1
        #     rain_prob = num_rain / len(self.rain_list)

        # expected_survival = self.compute_expected_survival(mine_probabilities)

        
        # print("\n~~~ Ruminating ~~~")

        # print("Rain probability:", rain_prob)

        # to compute the expected cost of moving,
        # first estimate the probability of raining using saved data.
        # then use the following sum to compute the cost of a single move:
        #    (1- prob) *  1  +  (1 - prob) prob 2 + (1 - prob) prob ^2 3 + (1 - prob) prob ^ 3 4 +...
        #    a = 1, d = 1
        #  b = (1-prob), r = prob
        # ab/(1-r) + dbr/(1-r)^2
        #  b/(1-r) +  br/(1-r)^2
        # (1 - prob) / (1 - prob) + (1-prob) * prob / (1-prob)^2
        if rain_prob == 1:
            rain_prob = 0.999999
        move_cost = 1 + rain_prob / (1 - rain_prob) 

        

        #  next compute distance between 1. agent and beacon 2. agent and exit

        beacon_dist = abs(env.agent[0] - env.beacon[0]) + abs(env.agent[1] - env.beacon[1])
        exit_dist = abs(env.agent[0] - env.exit[0]) + abs(env.agent[1] - env.exit[1])
        beacon_to_exit_dist = abs(env.beacon[0] - env.exit[0]) + abs(env.beacon[1] - env.exit[1])

        # cost 1 is directly to exit
        cost1 = exit_dist * move_cost

        # cost 2 is go to beacon then go to exit
        cost2 = beacon_dist * move_cost + beacon_to_exit_dist

        # Something wrong with this removal
        # for t in tasks:
        #     if t[0] == "go_to":
        #         tasks.remove(t)
        tasks = []

        if cost1 < cost2:
            tasks.insert(0, ("go_to", "exit"))
            # print("Replanning: go to exit")
        else:
            tasks.insert(0, ("go_to", "exit"))
            tasks.insert(0, ("go_to", "beacon"))
            # print("Replanning: go to beacon then exit")
        
        if env.rain_stop == True:
            tasks = [("go_to", "exit")]

        return tasks


    def observe(self, env):
        """
        Save the current weather (rainy or not)
        """

        self.rain_list.append(env.is_rainy)