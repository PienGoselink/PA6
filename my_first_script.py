
import numpy as np

def nerdy_computation(x):
    # """Returns the sum of the squares of the first x natural numbers using numpy."""
    if isinstance(x, int) and x > 0:
        antw= np.sum(np.arange(1, x + 1) ** 2)
    else:
        antw = 0
    return antw 

print("Hello MUDE! Let's compute something nerdy:")
result = nerdy_computation(10)
print(f"The sum of the squares of the first 10 natural numbers is {result}")

