import numpy as np
import pandas as pd
import math

import pickle

matrix = [] # Enter matrix here

input_file = 'input_file.bin'
# Reading the binary file
with open(input_file, 'rb') as f:
    contents = pickle.load(f)

def write(decoded_text): 
    out = 'output_file.bin'
    with open(out, 'wb') as f:
        pickle.dump(decoded_text, f)

CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVXYZ., '

ENCODER = {char:i for i, char in enumerate(CHARACTERS)}
DECODER = {i:char for i, char in enumerate(CHARACTERS)}

def encode(text):
    x = [ENCODER[char.upper()] if char.upper() in CHARACTERS else 27 for char in text]
    return x

def decode(code):
    x = ''.join([DECODER[round(symb)] for symb in code])
    return x

def noisy_channel(code, matrix):
    try: 
        r, c = matrix.shape # rows, columns
    except:
        r, c = len(matrix), len(matrix[0])

    # Sampling random noise from Normal distribution
    rng = np.random.default_rng()
    # abs() because rng.normal() will generate negative values as well
    noisy_code = [abs(np.random.choice(range(c), p=matrix[num]) + rng.normal()) for num in code]
    return noisy_code

# Operations
code = encode(contents)
output_from_channel = noisy_channel(code, matrix)
decoded_text = decode(output_from_channel)
write(decoded_text)