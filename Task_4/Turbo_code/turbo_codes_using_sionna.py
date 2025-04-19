"""
Developer : EE24B069
Date : 19 April 2025
Purpose : To implement turbo codes using sionna library's bcjr decoder function
Inputs : -
Outputs :Encoded list
        Only hard channel output
        Original message with 0 padding
        Decoded message list
        No of bit errors
        No of bit errors without any encoding
"""

import numpy as np
from copy import copy
from sionna.phy.fec.conv.decoding import BCJRDecoder
from sionna.phy.fec.conv.utils import Trellis
import tensorflow as tf

def gaussian_channel_simulator(encoded_message_list, std_dev_of_error):     #simulates gaussian channel
    encoded_message_arr = np.array(encoded_message_list)
    encoded_message_arr = (2.0 * encoded_message_arr) - 1.0
    return np.random.normal(0, std_dev_of_error, encoded_message_arr.shape) + encoded_message_arr
#gaussian_channel_simulator([1, 0,0,0,0, 1,1], 0.1)

def zero_padding(message_list, no_of_info_bits_in_block):    #pads zeros to the end of message list as the message list may not have length divisible by codeword length
    no_of_zeros_to_be_appended = no_of_info_bits_in_block - (len(message_list) % no_of_info_bits_in_block)
    if no_of_zeros_to_be_appended != no_of_info_bits_in_block:
        message_list.extend([0]*no_of_zeros_to_be_appended)

def rs_encoder(message_list, no_of_info_bits_in_block, extra_bits_added_to_make_final_state_00 = False):    #no_of_info_bits_in_block should be of the form prime-2
    zero_padding(message_list, no_of_info_bits_in_block)
    no_of_blocks = int(len(message_list)/no_of_info_bits_in_block)          #(7,5) recursive sytematic convolutional code has been implemented
    parity_bits_list = []
    info_blocks_list = []
    info_block_start_index = 0
    info_block_end_index = 0
    for i in range(no_of_blocks):
        a_k_minus_1 = 0
        a_k_minus_2 = 0
        info_block_end_index += no_of_info_bits_in_block
        info_block = message_list[info_block_start_index:info_block_end_index]
        info_block_start_index = info_block_end_index
        parity_bits_list_for_a_block = []
        for j in range(no_of_info_bits_in_block+2):
            info_bit = info_block[j]
            a_k = info_bit ^ a_k_minus_1 ^ a_k_minus_2
            v_k = a_k ^ a_k_minus_2
            parity_bits_list_for_a_block.append(v_k)
            #print(info_block)
            #print(info_bit, a_k, a_k_minus_1, a_k_minus_2, v_k)
            a_k_minus_2 = a_k_minus_1
            a_k_minus_1 = a_k
            if j == no_of_info_bits_in_block-1:     #two extra bits would get added to force it to go to state 0.
                if not extra_bits_added_to_make_final_state_00:
                    if (a_k_minus_1, a_k_minus_2) == (0, 0):
                        info_block.extend([0, 0])
                    elif (a_k_minus_1, a_k_minus_2) == (0, 1):
                        info_block.extend([1, 0])
                    elif (a_k_minus_1, a_k_minus_2) == (1, 0):
                        info_block.extend([1, 1])
                    else:
                        info_block.extend([0, 1])
                else:
                    break
        parity_bits_list.extend(parity_bits_list_for_a_block[:])
        info_blocks_list.extend(info_block[:])
    return info_blocks_list+parity_bits_list            #first half would be the message bits while the second half is the parity bits

def interleaver(number, no_of_info_bits_per_block_plus_two, list_or_array):      #no_of_info_bits_per_block + 2 should be prime,
    if type(list_or_array) is list:
        length = len(list_or_array)            # number should not be divisible by no_of_info_bits_per_block_plus_two
    else:
        length = list_or_array.shape[0]
    new_list = copy(list_or_array)       #length of a list should be divisible by no_of_info_bits_per_block_plus_two
    for j in range(int(round(length/no_of_info_bits_per_block_plus_two))):
        for i in range(0, no_of_info_bits_per_block_plus_two-1):  #for de-interleaver just replace number with inverse of the number in the particular field of remainders of no_of_info_bits_per_block_plus_two
            rem = ((i+1)*number) % no_of_info_bits_per_block_plus_two
            new_list[(j*no_of_info_bits_per_block_plus_two) + rem - 1] = list_or_array[ (j*no_of_info_bits_per_block_plus_two) + i]
    return new_list
#print(interleaver(4,7,np.array([1,-1,-1,-1,1,1,-1])))

def turbo_encoder_without_puncturing(message_list, no_of_info_bits_per_block, number):      #encodes the message
    rs_encoded_list = rs_encoder(message_list, no_of_info_bits_per_block)
    half_of_length_of_rs_encoded_list = len(rs_encoded_list)//2
    message_list_with_bits_to_force_final_state_to_00 = rs_encoded_list[0:half_of_length_of_rs_encoded_list]
    interleaved_message_list_with_bits_to_force_final_state_to_00 = interleaver(number, no_of_info_bits_per_block+2, message_list_with_bits_to_force_final_state_to_00)
    interleaved_rs_encoded_list = rs_encoder(interleaved_message_list_with_bits_to_force_final_state_to_00, no_of_info_bits_per_block+2, True)
    return rs_encoded_list + interleaved_rs_encoded_list[half_of_length_of_rs_encoded_list:]

def mix_sys_parity(sys, parity):        #sionna's bcjr function requires the first input as alternating sys and parity data
    sys = sys.numpy()           #this function generates a tensor alternating sys and parity data.
    parity = parity.numpy()
    combined = np.zeros(tuple(np.array(sys.shape) + np.array(parity.shape)), dtype=sys.dtype)
    combined[0::2] = sys
    combined[1::2] = parity
    combined = tf.convert_to_tensor(combined, dtype=tf.float32)
    return combined

def turbo_decode(systematic, parity1, parity2, interleaver_number, inverse_of_interleaver_number, block_len, num_iter=6):
    generator_tuple = ("111", "101")
    # Create Trellis
    trellis = Trellis(generator_tuple, rsc=True)
    length_of_message_llr_arr = systematic.shape[0]     #decodes the encoded message.
    llr_max = 10        #to prevent overflows
    no_of_blocks = int(length_of_message_llr_arr/block_len)

    bcjr = BCJRDecoder(gen_poly=generator_tuple, trellis=trellis, hard_out=False, rsc = True, terminate=True, algorithm="maxlog")

    for i in range(no_of_blocks):
        system = systematic[i*block_len:i*block_len+block_len]
        par1 = parity1[i*block_len:i*block_len+block_len]
        par2 = parity2[i*block_len:i*block_len+block_len]
        sys = tf.convert_to_tensor(system, dtype=tf.float32)
        p1 = tf.convert_to_tensor(par1, dtype=tf.float32)
        p2 = tf.convert_to_tensor(par2, dtype=tf.float32)
        # Initialize LLR to zeros
        intrinsic_llr1 = tf.zeros_like(sys, dtype=tf.float32)
        intrinsic_llr2 = tf.zeros_like(sys, dtype=tf.float32)
        extrinsic_llr2 = tf.zeros_like(sys, dtype=tf.float32)
        extrinsic_llr1 = tf.zeros_like(sys, dtype=tf.float32)
        input1 = mix_sys_parity(sys, p1)
        sys_int = tf.convert_to_tensor(interleaver(interleaver_number, block_len, sys.numpy()), dtype=tf.float32)
        input2 = mix_sys_parity(sys_int, p2)
        sys_term_bits = sys[block_len-2:block_len]
        sys_int_term_bits = sys_int[block_len-2:block_len]
        for j in range(num_iter):
            # First decoder

            intrinsic_llr1 = bcjr(input1, llr_a = extrinsic_llr2)
            extrinsic_llr1 = intrinsic_llr1 - sys[0:block_len-2] - extrinsic_llr2[0:block_len-2]
            extrinsic_llr1 = tf.squeeze(tf.concat([extrinsic_llr1, sys_term_bits], axis = -1))
            extrinsic_llr1 = tf.clip_by_value(extrinsic_llr1, clip_value_min=-1*llr_max, clip_value_max=llr_max)
            #print(sys, intrinsic_llr1, extrinsic_llr1)

            # Interleave
            interleaved_extrinsic_llr1 = tf.convert_to_tensor(interleaver(interleaver_number, block_len, extrinsic_llr1.numpy()), dtype=tf.float32)

            # Second decoder
            intrinsic_llr2 = bcjr(input2, llr_a = interleaved_extrinsic_llr1)
            extrinsic_llr2 = intrinsic_llr2 - sys_int[0:block_len-2] - interleaved_extrinsic_llr1[0:block_len-2]
            extrinsic_llr2 = tf.squeeze(tf.concat([extrinsic_llr2, sys_int_term_bits], axis = -1))

            #Deinterleave
            extrinsic_llr2 = tf.convert_to_tensor(interleaver(inverse_of_interleaver_number, block_len, extrinsic_llr2.numpy()), dtype=tf.float32)
            extrinsic_llr2 = tf.clip_by_value(extrinsic_llr2, clip_value_min=-1*llr_max, clip_value_max=llr_max)
            #print(sys_int, interleaved_llr1, extrinsic_llr1)

        intrinsic_llr2 = tf.squeeze(tf.concat([intrinsic_llr2, sys_int_term_bits], axis = -1))
        intrinsic_llr2_deintleaved = interleaver(inverse_of_interleaver_number, block_len, intrinsic_llr2.numpy())
        if i == 0:
            output_llrs = list(intrinsic_llr2_deintleaved)
        else:
            output_llrs.extend(list(intrinsic_llr2_deintleaved))
    # Final LLRs
    return output_llrs

def hard_message_output(final_message_llr, no_of_info_bits_per_block): #This function takes llrs as input and uses it to give hard output(0 or 1),
    # it also removes the two extra bits added to each block to make its final state (0,0)
    # But it doesn't remove the padded zeros
    count = 0
    decoded_message_list = []
    for i in final_message_llr:
        if count != no_of_info_bits_per_block and count != no_of_info_bits_per_block+1:
            if i>0:
                decoded_message_list.append(1)
            else:
                decoded_message_list.append(0)
        elif count == no_of_info_bits_per_block+1:
            count = -1
        count+=1
    return decoded_message_list

def no_of_bit_errors_finder(message_list, decoded_message_list):
    no_of_bit_errors = 0
    for i in range(len(message_list)):
        if message_list[i] != decoded_message_list[i]:
            no_of_bit_errors += 1
    return no_of_bit_errors

message_list1 = list(np.random.randint(0,2,(1000,)))        #message list without zero padding
no_of_info_bits_per_block1 = 111
no_of_info_bits_per_block_plus_two1 = no_of_info_bits_per_block1+2      #no_of_info_bits_per_block_plus_two1 must be prime
number1 = 19 #Note : number1*inverse_of_number_in_the_field1 must give remainder 1 when divided by no_of_info_bits_per_block_plus_two1
inverse_of_number_in_the_field1 = 6
std_dev_of_error1 = 1.0
variance_of_error1 = std_dev_of_error1*std_dev_of_error1
no_of_iterations1 = 10

encoded_list1 = turbo_encoder_without_puncturing(message_list1, no_of_info_bits_per_block1, number1)
print("Encoded list: ", encoded_list1)
channel_output_arr1 = gaussian_channel_simulator(encoded_list1, std_dev_of_error1)
length_of_message_llr_arr1 = int(round(channel_output_arr1.shape[0] / 3))
#channel_output_arr1 = scale_and_shift(channel_output_arr1)
final_message_llr1 = turbo_decode(channel_output_arr1[:length_of_message_llr_arr1], channel_output_arr1[length_of_message_llr_arr1:2*length_of_message_llr_arr1 ], channel_output_arr1[2*length_of_message_llr_arr1:], number1, inverse_of_number_in_the_field1, no_of_info_bits_per_block_plus_two1,no_of_iterations1)

decoded_message_list1 = hard_message_output(final_message_llr1, no_of_info_bits_per_block1)
just_hard_channel_output1 = hard_message_output(channel_output_arr1[0:length_of_message_llr_arr1], no_of_info_bits_per_block1)
print("Only hard channel output        :", just_hard_channel_output1)
print("Original message with 0 padding :", message_list1)
print("Decoded message list            :", decoded_message_list1)
no_of_bit_errors1 = no_of_bit_errors_finder(message_list1, decoded_message_list1)
no_of_bit_errors_without_encoding_decoding1 = no_of_bit_errors_finder(message_list1, just_hard_channel_output1)
print("No of bit errors :", no_of_bit_errors1)
print("No of bit errors without any encoding :", no_of_bit_errors_without_encoding_decoding1)
