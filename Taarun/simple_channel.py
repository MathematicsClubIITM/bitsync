"""
Developer : EE24B069
Date : 19 March 2025
Purpose : To simulate a erroneous channel
Inputs : -
Outputs : 3 graphs (similar to the rows of channel matrix)
Comments : Sorry, due to less time i haven't documented this code properly.
"""

import numpy as np
import random
import matplotlib.pyplot as plt
#channel_matrix = np.array(eval(input("enter the channel matrix as nested list : ")))
channel_matrix = np.array([[0.1, 0.1, 0.8], [0.1, 0.9, 0.0], [0.4, 0.3, 0.3]])
n = np.shape(channel_matrix)[0]
#input_seq = str(input("input : "))
output_seq = ""
p_tuple = (0,1,2)
no_of_iterations = 10000
for i in p_tuple:
    freq_list = [0,0,0]
    for k in range(no_of_iterations):
        running_sum = 0.0
        previous_running_sum = 0.0
        rand_num = random.random()
        for j in range(n):
            running_sum += channel_matrix[i,j]
            if running_sum>rand_num>=previous_running_sum:
                output_seq += str(j)
            previous_running_sum = running_sum
        freq_list[int(output_seq[-1])] += 1
    plt.subplot(1, 3, i+1)
    plt.plot(p_tuple, np.array(freq_list)/no_of_iterations)
plt.show()