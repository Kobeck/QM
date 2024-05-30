import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram
def main():
    # Load the raw analog signals from the two CSV files
    data_signal1 = pd.read_csv('data_pd1e7\\adc1.csv', header=None)
    data_signal2 = pd.read_csv('data_pd1e7\\adc2.csv', header=None)

    # Extract the two signals from the dataframes
    signal1 = data_signal1[0]  # Assuming data is in the first column
    signal2 = data_signal2[0]  # Assuming data is in the first column
    fs = 1e9  # Sampling frequency of 1 GHz

    # Plot the two signals in one figure
    plt.figure(figsize=(10, 6))
    plt.plot(signal1[int(3.90e5):int(4.2e5)], label='Pickup')
    plt.plot(signal2[int(3.90e5):int(4.2e5)], label='Output')
    plt.xlabel('Time (ns)')
    plt.ylabel('Amplitude [V]')
    plt.title('Analog Signals Analysis')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Calculate and plot the PSD of the signals in one Figure
    frequencies_psd1, psd1 = periodogram(signal1, fs)
    frequencies_psd2, psd2 = periodogram(signal2, fs)
    
    difference = psd1 - psd2[0:len(psd1)]

    low_limit=0# find_index_under_limit(frequencies_psd1, 1)
    limit1 = find_index_under_limit(frequencies_psd1, 500e6)

    plt.figure(figsize=(10, 6))
    # plt.plot(frequencies_psd1[low_limit:limit1]/1e6 , psd1[low_limit:limit1], label='PSD Pickup')
    # plt.plot(frequencies_psd2[low_limit:limit1]/1e6 , psd2[low_limit:limit1], label='PSD Output')
    plt.plot(difference[0:limit1]/1e6, label='PSD Signal difference')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Power Spectral Density')
    plt.title('PSD ')
    plt.legend()
    plt.grid(True)
    plt.show()

def find_index_under_limit(A, lim):


    left = 0
    right = len(A) - 1
    result = -1
    while left < right:
        mid = (left + right)//2
        print(A[mid])
        if A[mid] <lim:
            result = mid
            left = mid+1
        else:
            right = mid - 1
    print(len(A), result, A[result])
    return result

main()

