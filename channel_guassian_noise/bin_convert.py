import pickle

text = '' # Enter text to be converted to binary file

with open('input_file.bin', 'wb') as f:
    pickle.dump(text, f)