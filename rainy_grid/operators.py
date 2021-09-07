import pyhop


def move(env, direction):
    if env.done == False:
        # Right
        if direction == 'r':
            env.step(0)
        # Up
        if direction == 'u':
            env.step(1)   
        # Left
        if direction == 'l':
            env.step(2)
        # Down
        if direction == 'd':
            env.step(3)
        
        return env
    else:
        # print("dead move")
        return False

pyhop.declare_operators(move)