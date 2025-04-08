"""
Developer : EE24B069
Date : 4 April 2025
Purpose : Given a gaussian channel, finding its mean and standard deviation
Inputs : Number of iterations
Outputs : Approximate mean
        Approximate variance
        Approximate standard deviation
"""
import random
import math

def gaussian_channel(mean_error, std_dev_of_error, input_value):
    u1 = random.random()    #using box-muller transform
    u2 = random.random()
    z = (math.sqrt(-2*math.log(u1)) * math.sin(2*math.pi*u2) * std_dev_of_error) + mean_error + input_value
    return z

def gaussian_channel_metrics_estimator(no_of_iterations):
    sum_of_outputs = 0
    sum_of_squares_of_outputs = 0
    for i in range(no_of_iterations):
        output = gaussian_channel(0.5, 1, 0) #let us give the input value to be zero
        #This causes the channel to give out random erroneous outputs sampled from the gaussian distribution
        sum_of_outputs += output
        sum_of_squares_of_outputs += output*output
    approx_mean = sum_of_outputs/no_of_iterations
    approx_variance = (sum_of_squares_of_outputs/no_of_iterations) - approx_mean*approx_mean
    approx_std_dev = math.sqrt(approx_variance)
    return approx_mean, approx_variance, approx_std_dev

no_of_iterations1 = int(input("Number of iterations : "))
approx_mean1, approx_variance1, approx_std_dev1 = gaussian_channel_metrics_estimator(no_of_iterations1)
print("Approximate mean :",  approx_mean1)
print("Approximate variance:", approx_variance1)
print("Approximate standard deviation :", approx_std_dev1)