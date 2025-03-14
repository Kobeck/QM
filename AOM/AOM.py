"""
chirp.py: Introduction to chirp
Author: Gal Winer - Quantum Machines
Created: 17/01/2021
Revised by Tomer Feld - Quantum Machines
Revision date: 04/04/2022
"""
import os.path
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

amplitude = 1.9
with program() as prog:
    adc_str = declare_stream(adc_trace=True)
    #counts = declare(int)
    #counts_stream = declare_stream(adc_trace=True)
    n = declare(int)

    pulse_d = 100 * u.ns

    pause_d = 25 * u.ns

    # pause_d = 400 * u.ns
    total_length = int(400*1000)
    total_length_div_loop = int(total_length/1000)
    shift = 850

    pause_d1 = 100 * u.ns
    # pulse_d1 = 300 * u.ns



    measure("readout", "signal", adc_str)
    with infinite_loop_():
       play("const" * amp(amplitude), "AOM", duration=100)
       play("const" * amp(0), "AOM", duration=30)  
    
    # with infinite_loop_():
    #    play("const" * amp(0), "AOM", duration=pause_d) 
    #    play("const" * amp(amplitude), "AOM", duration=pulse_d)
    #    play("const" * amp(0), "AOM", duration=pause_d) 
    #    play("const" * amp(amplitude), "AOM", duration=pulse_d)
    #    play("const" * amp(0), "AOM", duration=pause_d1) 

    # # const    
    

    # with for_(n, 0, n < 1000, n + 1):
    #     #immer auf 750 insgesamt kommen
    #     play("zero", "AOM", duration=pause_d1)
    #     #play("gauss", "AOM") # play one pulse
    #     play("const"*amp(amplitude), "AOM", duration=pulse_d) # play one pulse
    #     play("zero", "AOM", duration=pause_d) # play one pulse
    #     #play("gauss", "AOM") # play one pulse
    #     play("const"*amp(amplitude), "AOM", duration=pulse_d)
        # play("zero", "AOM", duration=pause_d1) # play one pulse
        # play("gauss" , "AOM") # play one pulse in clock cycles [4ns]
        # play("gauss" , "AOM") # play one pulse in clock cycles [4ns]



    # gauss
    # with for_(n, 0, n < 10, n + 1):
    #     #immer auf 750 insgesamt kommen
    #     play("const" * amp(0), "AOM", duration=pd)
    #     play("gauss", "AOM") # play one pulse in clock cycles [4ns]
    #     play("const" * amp(0), "AOM", duration=pd) # play one pulse
    #     play("gauss", "AOM") # play one pulse in clock cycles [4ns]
    #     play("const" * amp(0), "AOM", duration=pd) # play one pulse

    #    play("const" * amp(amplitude), "AOM", duration=12.5)
        # save(counts,counts_stream)

  
    with stream_processing():
        #counts_stream.input1().buffer(1000).average().save("counts")
        #counts_stream.input1().buffer(1000).average().save_all("all_counts")
        adc_str.input1().save("adc1")
        adc_str.input2().save("adc2")

# The integration weights are, constant, of length 10*4*6 = 240g
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
    qm = qmm.open_qm(config)    
    job = qm.execute(prog)
    res = job.result_handles
    # res.wait_for_all_values() # needed for not infinite loop measurement
    time.sleep(600) # needed for infinite loop measurement
    job.halt()
    


    fig, axs = plt.subplots(10)
    # fig, axs = plt.subplots(1)
    # fig.suptitle("Inputs from down conversion 1")

    # Get data and average over the 10 pulses we generated earlier
    adc_1 = u.raw2volts(res.get("adc1").fetch_all())
    adc_1_cut = adc_1[shift:total_length+shift] #cut the readout pulse
    data_adc_1 = np.reshape(adc_1_cut, (1000, total_length_div_loop)) #reshape the data to 20 pulses
    data_avg = np.mean(data_adc_1[1:-1,:], axis=0) #The averaged data of the 1000 pulsen in an array
    print(len(adc_1_cut))
    # axs.set_xticks(np.arange(0, total_length_div_loop, step=50))
    # axs.plot(data_avg) # plot the averaged data
    # plt.grid(True)

    pulse_d_ns = int(pulse_d*4)
    pause_d_ns = int(pause_d*4)    
    # np.save('data\\Extra_Mara_15_11_2024\\adjust_2025_dl_pro_rect\\after_adjust_2025_pause_d'+str(pause_d_ns)+'pulse_d'+str(pulse_d_ns)+'__readout_length'+str(total_length_div_loop)+'k', data_avg)
    # rf_length'+str(rf_length)+'__flat_top_l_'+str(flat_length)+

    #adc_str.buffer(int(100e6)).average().save('irgendwieanders')
    # Speichern als Textdatei in das angegebene Verzeichnis
    # np.savetxt('C:\\Users\\admin\\Nextcloud\\nanophotonics (2)\\AOM_Pulses_Mara\\DLPro\\random\\20nspulse_break100ns_onepuls.txt', data_avg)
    #adc_2 = u.raw2volts(res.get("adc2").fetch_all())
 
# for first 10 plots 
    for i in range(10):
        axs[i].plot(data_adc_1[i,:])
        # axs[i].set_xticks(np.arange(0, total_length_div_loop, step=50))
        # axs[i].set_xticks(np.arange(0, total_length//20, step=5))
    
    # ax1 = axs[0]
    # ax1.plot(adc_1, 'b', label="Signal")
    # #ax1.plot(adc_2, 'r', label="Signal", alpha=0.5)
    # ax1.set_title("amp VS time Input 1")
    # ax1.set_xlabel("Time [ns]")
    # ax1.set_ylabel("Signal amplitude [V]")
    # #ax1.plot(adc_2, 'r', label="Output")
    # # ax1.legend()
    
    
# # signal processing, FFT
#     fs = 1e9 # Sampling frequency of 1 GHz
#     frequencies_psd1, psd1 = periodogram(adc_1, fs)
#     frequencies_psd2, psd2 = periodogram(adc_2, fs)
#     def find_index_under_limit(A, lim):
#         ### Find the index of the first element in A that is under the limit lim
#         left = 0
#         right = len(A) - 1
#         result = -1
#         while left < right:
#             mid = (left + right)//2
#             print(A[mid])
#             if A[mid] <lim:
#                 result = mid
#                 left = mid+1
#             else:
#                 right = mid - 1
#         # print(len(A), result, A[result])
#         return result

#     low_limit=0
#     limit1 = find_index_under_limit(frequencies_psd1, 500e6)

#     ax2 = axs[1]
#     #ax2.plot(frequencies_psd1[low_limit:limit1]/1e6 , psd1[low_limit:limit1], label='PSD Pickup')
#     #plt.plot(frequencies_psd2[low_limit:limit1]/1e6 , psd2[low_limit:limit1], label='PSD Output')
#     # ax2.set_xlabel('Frequency (MHz)')
#     # ax2.set_ylabel('Power Spectral Density')
#     # ax2.set_title('PSD')
#     # ax2.legend()
#     ax2.grid(True)
    plt.show()

