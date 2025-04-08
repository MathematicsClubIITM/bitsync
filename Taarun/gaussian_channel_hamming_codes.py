"""
Developer : EE24B069
Date : 4 April 2025
Purpose : Simulating a gaussian channel and implementing hamming encoding decoding algorithm
Inputs :
        Mean error of gaussian channel
        Standard deviation of error of channel
        Average power constraint
        Number of iterations(to find parameters of the gaussian channel)
        File name of the text file containing information in the form of 0's and 1's
        Number of redundant bits per block

Outputs : Approximate mean
        Approximate variance
        Approximate standard deviation
        Encoded message
        Received message
        Original message
        Decoded message
        Rate of information sent using hamming codes
        Channel capacity
        Theoretical Probability of no error using hamming code
        Experimental Probability of no error using hamming code
        Theoretical Probability of no error without any encoding

"""

import random
import math

"""
mean_error1 = float(input("Mean error of gaussian channel : "))
std_dev_of_error1 = float(input("Standard deviation of error of channel : "))
avg_power1 = float(input("Average power constraint : "))
no_of_iterations1 = int(input("Number of iterations : "))
file_name1 = str(input("File name : "))
no_of_redundant_bits_per_block = int(input("Number of redundant bits per block"))
"""

mean_error1 = 1
std_dev_of_error1 = 2
avg_power1 = 25
no_of_iterations1 = 10000
file_name1 = "binary_file.txt"
no_of_redundant_bits_per_block1 = 3

def gaussian_channel(mean_error, std_dev_of_error, input_value):
    u1 = random.random()    #using box-muller transform
    u2 = random.random()
    z = (math.sqrt(-2*math.log(u1)) * math.sin(2*math.pi*u2) * std_dev_of_error) + mean_error + input_value
    return z

def gaussian_channel_metrics_estimator(no_of_iterations, mean_error, std_dev_of_error):
    sum_of_outputs = 0
    sum_of_squares_of_outputs = 0
    for i in range(no_of_iterations):
        output = gaussian_channel(mean_error, std_dev_of_error, 0) #let us give the input value to be zero
        #This causes the channel to give out random erroneous outputs sampled from the gaussian distribution
        sum_of_outputs += output
        sum_of_squares_of_outputs += output*output
    approx_mean = sum_of_outputs/no_of_iterations
    approx_variance = (sum_of_squares_of_outputs/no_of_iterations) - approx_mean*approx_mean
    approx_std_dev = math.sqrt(approx_variance)
    return approx_mean, approx_variance, approx_std_dev

def message_list_extractor(file_name):
    file_ptr = open(file_name, "r")
    file_contents_str = file_ptr.read()
    for i in [" ", ",", "\n", ":", "\t"]:
        file_contents_str = file_contents_str.replace(i, "")
    message_list = []
    for i in file_contents_str:
        message_list.append(int(i))
    return message_list

def hamming_message_encoder(message_list, no_of_redundant_bits):
    no_of_bits = len(message_list)
    len_of_chunk = 2**no_of_redundant_bits - 1
    no_of_info_bits_in_chunk = len_of_chunk - no_of_redundant_bits
    no_of_full_chunks = no_of_bits//no_of_info_bits_in_chunk
    encoded_message_list = []
    index = 0
    next_index = 0
    for i in range(no_of_full_chunks):
        next_index += no_of_info_bits_in_chunk
        relevant_info_chunk = message_list[index:next_index]
        index = next_index
        temp = 1
        count_of_redundant_bits_added_in_the_chunk = 0
        chunk = []
        temp2 = (len_of_chunk+1)*2
        j = 1
        while True:
            if j == temp:
                temp = temp*2
                if temp2 == temp:
                    break
                count_of_redundant_bits_added_in_the_chunk += 1
                chunk.append(0)
            else:
                chunk.append(relevant_info_chunk[j-1-count_of_redundant_bits_added_in_the_chunk])
            j+=1
        temp2 = 0
        for i in range(1, len_of_chunk+1):
            if chunk[i-1] == 1:
                temp2 = temp2^i
        temp = 1
        for i in range(no_of_redundant_bits):
            chunk[temp-1] = temp2%2
            temp2 = temp2//2
            temp *= 2
        encoded_message_list.extend(chunk)
    encoded_message_list.extend(message_list[index:])       #to include the leftover bits, the leftover bits are passed without error checking
    return encoded_message_list

def channel_simulator(encoded_message_list, avg_power_constraint, mean_error, std_dev_of_error):
    sqrt_power = math.sqrt(avg_power_constraint)
    minus_sqrt_power = -1 * sqrt_power
    continuous_message_received_list = []
    for i in encoded_message_list:
        if i == 0:
            continuous_message_received_list.append(gaussian_channel(mean_error, std_dev_of_error, minus_sqrt_power))
        else:
            continuous_message_received_list.append(gaussian_channel(mean_error, std_dev_of_error, sqrt_power))
    return continuous_message_received_list

def continuous_message_to_discrete_message_converter(continuous_message_received_list, approx_mean_error):
    received_message_list = []
    for i in continuous_message_received_list:
        if i>approx_mean_error:
            received_message_list.append(1)
        else:
            received_message_list.append(0)
    return received_message_list

def hamming_message_decoder(received_message_list, no_of_redundant_bits):
    len_of_chunk = 2 ** no_of_redundant_bits - 1
    no_of_full_chunks = len(received_message_list)//len_of_chunk
    decoded_message_list = []
    index = 0
    next_index = 0
    for i in range(no_of_full_chunks):
        next_index += len_of_chunk
        chunk = received_message_list[index:next_index]
        index = next_index
        temp2 = 0
        for i in range(1, len_of_chunk + 1):
            if chunk[i - 1] == 1:
                temp2 = temp2 ^ i
        if temp2 != 0:
            chunk[temp2-1] = 1 - chunk[temp2-1]
        temp1 = (len_of_chunk+1)//2
        for i in range(no_of_redundant_bits):
            chunk.pop(temp1-1)
            temp1 = temp1//2
        decoded_message_list.extend(chunk)
    decoded_message_list.extend(received_message_list[index:])
    return decoded_message_list

def probability_of_no_error_using_hamming_code(power_constraint, approx_variance_of_error, no_of_redundant_bits, len_of_received_message):
    probability_of_a_bit_flip = 0.5 - math.erf(math.sqrt(power_constraint/(2*approx_variance_of_error)))/2
    len_of_chunk = 2 ** no_of_redundant_bits - 1
    probability_of_no_bit_flip_in_a_chunk = (1 - probability_of_a_bit_flip) ** len_of_chunk     #if there is no bit flip or one bit flip hamming codes could correct it
    probability_of_one_bit_flip_in_a_chunk = len_of_chunk * probability_of_a_bit_flip * (1 - probability_of_a_bit_flip) ** (len_of_chunk - 1)
    no_of_full_chunks = len_of_received_message//len_of_chunk
    answer = (probability_of_no_bit_flip_in_a_chunk + probability_of_one_bit_flip_in_a_chunk) ** no_of_full_chunks * ((1 - probability_of_a_bit_flip) ** (len_of_received_message - no_of_full_chunks*len_of_chunk))
    return answer

def probability_of_no_error_without_any_encoding(power_constraint, approx_variance_of_error, len_of_message):
    probability_of_a_bit_flip = 0.5 - math.erf(math.sqrt(power_constraint / (2*approx_variance_of_error))) / 2
    answer = (1 - probability_of_a_bit_flip) ** len_of_message
    return answer

def experimental_probability_of_no_error_using_hamming_code(message_list, no_of_redundant_bits_per_block, no_of_iterations, avg_power, mean_error, std_dev_of_error, approx_mean_error, approx_std_dev_of_error):
    count = 0
    for i in range(no_of_iterations):
        encoded_message_list = hamming_message_encoder(message_list, no_of_redundant_bits_per_block)
        continuous_message_received_list = channel_simulator(encoded_message_list, avg_power, mean_error, std_dev_of_error)
        received_message_list = continuous_message_to_discrete_message_converter(continuous_message_received_list, approx_mean_error)
        decoded_message_list = hamming_message_decoder(received_message_list, no_of_redundant_bits_per_block)
        if decoded_message_list == message_list:
            count+=1
    return count/no_of_iterations

def channel_capacity_calculator(avg_power, variance_of_error):
    return 0.5 * math.log2(1 + avg_power/variance_of_error)

approx_mean_error1, approx_variance_of_error1, approx_std_dev_of_error1 = gaussian_channel_metrics_estimator(no_of_iterations1, mean_error1, std_dev_of_error1)
print("Approximate mean :",  approx_mean_error1)
print("Approximate variance:", approx_variance_of_error1)
print("Approximate standard deviation :", approx_std_dev_of_error1)
message_list1 = message_list_extractor(file_name1)
encoded_message_list1 = hamming_message_encoder(message_list1, no_of_redundant_bits_per_block1)
print("Encoded message list  :", encoded_message_list1)
continuous_message_received_list1 = channel_simulator(encoded_message_list1, avg_power1, mean_error1, std_dev_of_error1)
received_message_list1 = continuous_message_to_discrete_message_converter(continuous_message_received_list1, approx_mean_error1)
print("Received message list :", received_message_list1)
decoded_message_list1 = hamming_message_decoder(received_message_list1, no_of_redundant_bits_per_block1)
print("Original message      :", message_list1)
print("Decoded message list  :", decoded_message_list1)
print("Rate of information sent using hamming codes :", len(message_list1)/len(encoded_message_list1), "bits per channel use")
print("Channel capacity :", channel_capacity_calculator(avg_power1, std_dev_of_error1*std_dev_of_error1), "bits per channel use")
print("Theoretical Probability of no error using hamming code :", probability_of_no_error_using_hamming_code(avg_power1, approx_variance_of_error1, no_of_redundant_bits_per_block1, len(received_message_list1)))
print("Experimental Probability of no error using hamming code :", experimental_probability_of_no_error_using_hamming_code(message_list1, no_of_redundant_bits_per_block1, no_of_iterations1, avg_power1, mean_error1, std_dev_of_error1, approx_mean_error1, approx_std_dev_of_error1))
print("Theoretical Probability of no error without any encoding :", probability_of_no_error_without_any_encoding(avg_power1, approx_variance_of_error1, len(message_list1)))
