import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram
def main():
    # Load the raw analog signals from the two CSV files
    data_signal1 = pd.read_csv('adc1.csv', header=None)
    data_signal2 = pd.read_csv('adc2.csv', header=None)

    # Extract the two signals from the dataframes
    signal1 = data_signal1[0]  # Assuming data is in the first column
    signal2 = data_signal2[0]  # Assuming data is in the first column
    fs = 1e9  # Sampling frequency of 1 GHz

    # Plot the two signals in one figure
    plt.figure(figsize=(10, 6))
    plt.plot(signal1, label='Pickup')
    plt.plot(signal2, label='Output')
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

    low_limit=0 #find_index_under_limit(frequencies_psd1, 1e6)
    limit1 = find_index_under_limit(frequencies_psd1, 10e6)


    fig1, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=True)
    ratio=psd2/psd1[0:len(psd2)]
    ax1.loglog(frequencies_psd1[low_limit:limit1]/1e6 , psd1[low_limit:limit1], label='PSD Pickup')
    ax1.grid(True)
    ax2.loglog(frequencies_psd2[low_limit:limit1]/1e6 , psd2[low_limit:limit1], label='PSD Output')
    #plt.plot(frequencies_psd1[low_limit:limit1], ratio[low_limit:limit1], label='ratio')
    #plt.plot(difference[0:limit1]/1e6, label='PSD Signal difference')
    ax1.set_ylim(1e-22, 1e-12)
    ax2.set_ylim(1e-22, 1e-12)
    ax1.set_ylabel('PSD')
    ax2.set_xlabel('Frequency (MHz)')
    ax1.set_title('PSD Pickup')
    ax2.set_title('PSD Output')
    #fig.legend()
    ax2.grid(True)
    plt.show()

    fig2, ax3 = plt.subplots()
    ax3.loglog(frequencies_psd1[low_limit:limit1]/1e6 , psd1[low_limit:limit1], label='PSD terminated')
    ax3.loglog(frequencies_psd2[low_limit:limit1]/1e6 , psd2[low_limit:limit1], label='PSD Output')
    ax3.set_ylim(1e-23, 1e-12)
    ax3.set_title('PSD')
    ax3.set_xlabel('Frequency (MHz)')
    ax3.set_ylabel('PSD')
    ax3.set_title('PSD noise comparison (Termination vs Output line)')
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

