import numpy as np

# Generate a random location [row, col]
def generate_loc(num_rows):
    return [np.random.randint(num_rows), np.random.randint(num_rows)]