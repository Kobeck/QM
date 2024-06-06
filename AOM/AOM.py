"""
chirp.py: Introduction to chirp
Author: Gal Winer - Quantum Machines
Created: 17/01/2021
Revised by Tomer Feld - Quantum Machines
Revision date: 04/04/2022
"""
import time
from qm import QuantumMachinesManager
from qm.qua import *
from qm import SimulationConfig
import numpy as np
import matplotlib.pyplot as plt
from qualang_tools import units as u
from configuration import *
from scipy.signal import periodogram

qop_ip = "192.168.1.106"
cluster_name = "Cluster_RR_Lab"
qmm = QuantumMachinesManager(host=qop_ip, cluster_name=cluster_name)

### First example - Linear chirp
simulate = False

amplitude = 0.5
with program() as prog:
    adc_str = declare_stream(adc_trace=True)
    measure("readout", "signal", adc_str)
    play("const" * amp(amplitude), "AOM") # play one pulse
    with stream_processing():
        adc_str.input1().save("adc1")
        adc_str.input2().save("adc2")

# The integration weights are, constant, of length 10*4*6 = 240
if simulate:
    job = qmm.simulate(config, prog, SimulationConfig(int(pulse_duration) // 4))  # duration in clock cycles, 4 ns
    samples = job.get_simulated_samples()
    x = samples.con1.analog["1"]

    ax1 = plt.subplot(111)
    fs = 1e9  # Sampling frequency of 1 GHz
    freqs, psd = periodogram(x, fs)
    ax1.plot(x)
    plt.xlabel("t [us]")
    plt.ylabel("Voltage [V]")
    plt.show()
else:
    print('Executing program')
    qm = qmm.open_qm(config)
    job = qm.execute(prog)
    res = job.result_handles
    # res.wait_for_all_values()
    time.sleep(5)
    job.halt()


    fig, axs = plt.subplots(2)
    # fig.suptitle("Inputs from down conversion 1")
    adc_1 = u.raw2volts(res.get("adc1").fetch_all())
    adc_2 = u.raw2volts(res.get("adc2").fetch_all())
    ax1 = axs[0]
    ax1.plot(adc_1, 'b', label="Pickup")
    ax1.set_title("amp VS time Input 1")
    ax1.set_xlabel("Time [ns]")
    ax1.set_ylabel("Signal amplitude [V]")
    ax1.plot(adc_2, 'r', label="Output")
    ax1.legend()
    
    
# signal processing, FFT
    fs = 1e9 # Sampling frequency of 1 GHz
    frequencies_psd1, psd1 = periodogram(adc_1, fs)
    frequencies_psd2, psd2 = periodogram(adc_2, fs)
    def find_index_under_limit(A, lim):
        ### Find the index of the first element in A that is under the limit lim
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
        # print(len(A), result, A[result])
        return result

    low_limit=0
    limit1 = find_index_under_limit(frequencies_psd1, 500e6)

    ax2 = axs[1]
    ax2.plot(frequencies_psd1[low_limit:limit1]/1e6 , psd1[low_limit:limit1], label='PSD Pickup')
    #plt.plot(frequencies_psd2[low_limit:limit1]/1e6 , psd2[low_limit:limit1], label='PSD Output')
    ax2.set_xlabel('Frequency (MHz)')
    ax2.set_ylabel('Power Spectral Density')
    ax2.set_title('PSD')
    ax2.legend()
    ax2.grid(True)
    plt.show()

