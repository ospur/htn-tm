import pyhop


def go_to(env, dest):
    if dest == "exit":
        dest_loc = env.exit
    elif dest == "beacon":
        dest_loc = env.beacon

    subtasks = []

    if env.agent == dest_loc:
        return subtasks
    
    if env.agent[0] < dest_loc[0]:
        direction = 'd'
    elif env.agent[0] > dest_loc[0]:
        direction = 'u'

    if env.agent[1] < dest_loc[1]:
        direction = 'r'
    elif env.agent[1] > dest_loc[1]:
        direction = 'l'
    
    subtasks.append(("move", direction))
    subtasks.append(("go_to", dest))

    return subtasks


pyhop.declare_methods("go_to", go_to)