import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import os
from scipy.signal import periodogram
from time import sleep
from tqdm import tqdm

from time import sleep
from tqdm import tqdm

def main():
    # Load the raw analog signals from the two CSV files
    print(os.getcwd())
    data_signal1 = pd.read_csv("Noise_analysis/redPitaya/data_file_2021-04-02_03-47-30.csv", header=None)
    print('file read complete')
    #data_signal2 = pd.read_csv("Noise_analysis/data_zero_coil_adc2_terminated/adc2.csv", header=None)

    # Extract the two signals from the dataframes
    signal1 = data_signal1[0]  # Assuming data is in the first column
    # signal2 = data_signal2[0]  # Assuming data is in the first column
    fs = 1e9  # Sampling frequency of 1 GHz

    # Plot the two signals in one figure
    plt.figure(figsize=(10, 6))
    plt.plot(signal1, label='Pickup')
    # plt.plot(signal2, label='Output')
    plt.xlabel('Time (ns)')
    plt.ylabel('Amplitude [V]')
    plt.title('Analog Signals Analysis')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Calculate and plot the PSD of the signals in one Figure
    frequencies_psd1, psd1 = periodogram(signal1, fs)
    print('psd complete')
    #frequencies_psd2, psd2 = periodogram(signal2, fs)
    
    # difference = psd1 - psd2[0:len(psd1)]
=======
    print(os.getcwd())
    data_signal1 = pd.read_csv("Noise_analysis/redPitaya/data_file_2021-04-02_03-47-30.csv", header=None)
    print('file read complete')
    #data_signal2 = pd.read_csv("Noise_analysis/data_zero_coil_adc2_terminated/adc2.csv", header=None)

    # Extract the two signals from the dataframes
    signal1 = data_signal1[0]  # Assuming data is in the first column
    #signal2 = data_signal2[0]  # Assuming data is in the first column
    fs = 5e6  # Sampling frequency of 1 GHz #change to 50e8

    # Plot the two signals in one figure
    # plt.figure(figsize=(10, 6))
    # plt.plot(signal1, label='adc1')
    # #plt.plot(signal2, label='adc2')
    # plt.xlabel('Time (ns)')
    # plt.ylabel('Amplitude [V]')
    # plt.title('Analog Signals Analysis')
    # plt.legend()
    # plt.grid(True)
    # plt.show()

    # Calculate and plot the PSD of the signals in one Figure
    frequencies_psd1, psd1 = periodogram(signal1, fs)
    print('psd complete')
    #frequencies_psd2, psd2 = periodogram(signal2, fs)
    
    #difference = psd1 - psd2[0:len(psd1)]
>>>>>>> d6eb219f484697a053faf4c50fcb35c79285e51f

    low_limit=0 #find_index_under_limit(frequencies_psd1, 1e6)
    limit1 = find_index_under_limit(frequencies_psd1, 500e6)


    fig1, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=True)
<<<<<<< HEAD
    # ratio=psd2/psd1[0:len(psd2)]
    ax1.loglog(frequencies_psd1[low_limit:limit1]/1e6 , psd1[low_limit:limit1], label='PSD Pickup')
    ax1.grid(True)
    # ax2.loglog(frequencies_psd2[low_limit:limit1]/1e6 , psd2[low_limit:limit1], label='PSD Output')
=======
    #ratio=psd2/psd1[0:len(psd2)]
    ax1.plot(frequencies_psd1[low_limit:limit1]/1e6 , psd1[low_limit:limit1], label='PSD adc1')
    ax1.plot(True)
    ax1.grid(True)
    #ax2.loglog(frequencies_psd2[low_limit:limit1]/1e6 , psd2[low_limit:limit1], label='PSD adc2')
>>>>>>> d6eb219f484697a053faf4c50fcb35c79285e51f
    #plt.plot(frequencies_psd1[low_limit:limit1], ratio[low_limit:limit1], label='ratio')
    #plt.plot(difference[0:limit1]/1e6, label='PSD Signal difference')
    #ax1.set_ylim(1e-22, 1e-12)
    #ax2.set_ylim(1e-22, 1e-12)
    #ax1.set_ylim(1e-22, 1e-12)
    #ax2.set_ylim(1e-22, 1e-12)
    ax1.set_ylabel('PSD')
    #ax2.set_xlabel('Frequency (MHz)')
    ax1.set_title('PSD adc1')
    #ax2.set_title('PSD adc2')
    #ax2.set_xlabel('Frequency (MHz)')
    ax1.set_title('PSD adc1')
    #ax2.set_title('PSD adc2')
    #fig.legend()
    #ax2.grid(True)
    #ax2.grid(True)
    plt.show()

    fig2, ax3 = plt.subplots()
<<<<<<< HEAD
    ax3.loglog(frequencies_psd1[low_limit:limit1]/1e6 , psd1[low_limit:limit1], label='PSD terminated')
    # ax3.loglog(frequencies_psd2[low_limit:limit1]/1e6 , psd2[low_limit:limit1], label='PSD Output')
    # ax3.set_ylim(1e-23, 1e-12)
=======
    ax3.loglog(frequencies_psd1[low_limit:limit1]/1e6 , psd1[low_limit:limit1], label='PSD adc1')
    #ax3.loglog(frequencies_psd2[low_limit:limit1]/1e6 , psd2[low_limit:limit1], label='PSD adc2')
    #ax3.set_ylim(1e-23, 1e-12)
>>>>>>> d6eb219f484697a053faf4c50fcb35c79285e51f
    ax3.set_title('PSD')
    ax3.set_xlabel('Frequency (MHz)')
    ax3.set_ylabel('PSD')
    ax3.set_title('PSD noise comparison (adc2 is terminated, adc1 goes to coil)')
    ax3.set_title('PSD noise comparison (adc2 is terminated, adc1 goes to coil)')
    ax3.legend()
    ax3.grid(True)
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

