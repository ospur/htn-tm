import numpy as np
import utils, pyhop, critic
import operators, methods
from datetime import datetime

class RainyGrid:

   def __init__(self, prob):
      
      self.num_rows = 10
      self.max_row = self.num_rows - 1
      self.rain_prob = prob
      print("rain prob = ", self.rain_prob)

   def reset(self):
      self.exit = [9, 9]
      self.rain_stop = False

      self.beacon = utils.generate_loc(self.num_rows)
      while self.beacon == self.exit:
         self.beacon = utils.generate_loc(self.num_rows)
      self.agent = utils.generate_loc(self.num_rows)
      while self.agent == self.beacon or self.agent == self.exit:
         self.agent = utils.generate_loc(self.num_rows)

      # random location [row, col]
      self.is_rainy = False
      self.view = np.zeros((self.num_rows, self.num_rows))
      self.steps = 0
      self.done = False

      return self.visualize()

   def step(self, action):
      # At every step, flip a coin; if head (rain_prob), it rains
      flip = np.random.choice(2, 1, p=[1 - self.rain_prob, self.rain_prob])

      # Check if it is rainy before taking an action
      # if not rainy
      if flip == 0 or self.rain_stop:
         self.is_rainy = False
         # Right
         if action == 0:
            self.agent[1] = min(self.agent[1] + 1, self.max_row)
         # Up
         if action == 1:
            self.agent[0] = max(self.agent[0] - 1, 0)    
         # Left
         if action == 2:
            self.agent[1] = max(self.agent[1] - 1, 0)
         # Down
         if action == 3:
            self.agent[0] = min(self.agent[0] + 1, self.max_row)
         
      else:
         self.is_rainy = True
         self.steps += 4
      
      self.steps += 1

      if self.agent == self.beacon:
         self.rain_stop = True
      elif self.agent == self.exit:
         self.done = True


   def visualize(self):
      self.view[self.agent[0], self.agent[1]] = 1
      self.view[self.exit[0], self.exit[1]] = 2
      self.view[self.beacon[0], self.beacon[1]] = 3

      if self.agent == self.exit:
         self.view[self.exit[0], self.exit[1]] = -2
         
      if self.agent == self.beacon:
         self.view[self.beacon[0], self.beacon[1]] = -3

      return self.view


def main():

   for j in range(17):
         
      rain_prob = (10 + j * 5) / 100
      rain_prob_int = 10 + j * 5

      env = RainyGrid(rain_prob)
      
      print(f"run = {j} prob = rain_prob")
      print(env.reset())
      

      pyhop.print_methods()

      runs = 2000

      # baseline 1: go to the exit
      for i in range(runs):
         no_critic = empty_critic.Critic()
         env.reset()
         task_list = [("go_to", "exit")]
         plan = pyhop.pyhopT(env, task_list, no_critic, verbose=0)
         total_reward = -env.steps

         with open(f'baseline1-{rain_prob_int}.txt', 'a') as f:
            f.write(str(total_reward) + "\n")


      # baseline 2: go to the beacon then the exit
      for i in range(runs):
         env.reset()
         task_list = [("go_to", "beacon"), ("go_to", "exit")]
         plan = pyhop.pyhopT(env, task_list, no_critic, verbose=0)
         total_reward = -env.steps

         with open(f'baseline2-{rain_prob_int}.txt', 'a') as f:
            f.write(str(total_reward) + "\n")
      
      # agent: go to exit is the initial task, then dynamically change the task list.
      for i in range(runs):
         # agent_critic = critic.Critic()
         agent_critic = critic.Critic()
         # print("\n Run", i)
         env.reset()
         # print("agent loc", env.agent)
         # print("exit loc", env.exit)
         # print("beacon loc", env.beacon)
         task_list = [("go_to", "exit")]
         plan = pyhop.pyhopT(env, task_list, agent_critic, verbose=0)
         total_reward = -env.steps
         # print(i)
         # print(env.steps)
         with open(f'agent-{rain_prob_int}.txt', 'a') as f:
            f.write(str(total_reward) + "\n")
   


  
if __name__=="__main__": 
    main() 