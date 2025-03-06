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
# Total duration of the measurement
total_integration_time = int(160 * u.ms)  # 100ms
# Duration of a single chunk. Needed because the OPX cannot measure for more than ~1ms
sit = 50
pause_sit = 100
single_integration_time_ns = int(sit * u.ns)  # 500us
pause_single_integration_time_ns = int(pause_sit * u.ns)
single_integration_time_cycles = single_integration_time_ns // 4
pause_single_integration_time_cycles = pause_single_integration_time_ns // 4
# Number of chunks to get the total measurement time
n_count = 200000# int(total_integration_time / single_integration_time_ns)
 
with program() as counter:
      # QUA vector for storing the time-tags
    counts = declare(int)  # variable for number of counts of a single chunk
    total_counts = declare(int)  # variable for the total number of counts
    n = declare(int)  # number of iterations


    counts_st = declare_stream()  # stream for counts
    times_st = declare_stream()  # stream for time-tags

    ###################### just fot raw adc
    # adc_str = declare_stream(adc_trace=True)   
    # measure("readout", "signal", adc_str)  
    # play("const", "AOM", duration=single_integration_time_cycles)


   # Infinite loop to allow the user to work on the experimental set-up while looking at the counts
    #with infinite_loop_():
        # Loop over the chunks to measure for the total integration time

    

    # measure("readout", "SPCM", None, time_tagging.analog(times, single_integration_time_ns, counts))
    # play("const", "AOM", duration= single_integration_time_ns) 
    # with for_(n, 0, n < n_count, n + 1):
    #     with if_(n>150):
    #         measure("readout", "SPCM", None, time_tagging.analog(times, single_integration_time_cycles, counts))
    #         play("gauss" *amp(1.9), "AOM", duration= single_integration_time_cycles) 
    #     with elif_(n>100):
    #         measure("readout", "SPCM", None, time_tagging.analog(times, single_integration_time_cycles, counts))
    #         play("const" *amp(0), "AOM", duration= single_integration_time_cycles)
    #     with elif_(n>50):
    #         measure("readout", "SPCM", None, time_tagging.analog(times, single_integration_time_cycles, counts))
    #         play("const" *amp(1.9), "AOM", duration= single_integration_time_cycles)
    #     with else_():
    #         measure("readout", "SPCM", None, time_tagging.analog(times, single_integration_time_cycles, counts))
    #         play("const" *amp(0), "AOM", duration= single_integration_time_cycles)
    #     save(counts, counts_st)
    #     assign(counts, 0)
    k= declare(int, 1)
    i = declare(int)
    # times_cont = declare(Variable)
    with for_(n, 0, n < n_count, n + 6):
        times = declare(int, size=1000)
        # measure("readout", "SPCM", None, time_tagging.analog(times, single_integration_time_cycles, counts))
        # play("const"*amp(1.9), "AOM", duration=single_integration_time_cycles)

        # with for_(i, 0, i < counts, i + 1):
        # # times_cont[i] = times[i]+single_integration_time_ns*n
        #     save(times[i], times_st)
        #     assign(times[i], 0)

        # save(counts, counts_st)
        # assign(counts, 0)
        # measure("readout", "SPCM", None, time_tagging.analog(times, single_integration_time_cycles, counts))
        # play("const"*amp(0), "AOM", duration=single_integration_time_cycles)



        # with for_(i, 0, i < counts, i + 1):
        #     # times_cont[i] = times[i]+single_integration_time_ns*n
        #     save(times[i], times_st)
        #     assign(times[i], 0)

        # save(counts, counts_st)
        # assign(counts, 0)

        #BEGINNING OF WHAT WORKS
        measure("readout", "SPCM", None, time_tagging.analog(times, single_integration_time_cycles, counts))
        play("const"*amp(0), "AOM", duration= pause_single_integration_time_cycles)
        play("const"*amp(amplitude), "AOM", duration= single_integration_time_cycles)
        play("const"*amp(0), "AOM", duration=pause_single_integration_time_cycles)
        play("const"*amp(amplitude), "AOM", duration= single_integration_time_cycles)
        play("const"*amp(0), "AOM", duration= pause_single_integration_time_cycles)\


        with for_(i, 0, i < counts, i + 1):
            # times_cont[i] = times[i]+single_integration_time_ns*n
            save(times[i], times_st)
            assign(times[i], 0)

        save(counts, counts_st)
        assign(counts, 0)
        # END OF WHAT WORKS
   

    with stream_processing():
        counts_st.with_timestamps().save_all("counts")
        times_st.save_all("times")
        ##################### just for raw adc
        # adc_str.input1().save("adc1")
        # adc_str.input2().save("adc2")   



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
    job = qm.execute(counter)
    res = job.result_handles


    counts_handle = res.get("counts")
    times_handle = res.get("times")
    times_handle.wait_for_values()
    counts_handle.wait_for_values()

    ############### just for raw adc
    #adc_1 = u.raw2volts(res.get("adc1").fetch_all())

    res.wait_for_all_values() # needed for not infinite loop measurement
    
    
    # time = []
    # counts = []
   
    fig = plt.figure()
    counts_1 = counts_handle.fetch_all()
    times_1 = times_handle.fetch_all()
    print([counts_1["value"], times_1["value"]])

    values = counts_1["value"]
    times = times_1["value"] 
    #plt.bar(times_1, data=values)
    # plt.plot(times, values)
    # plt.hist(times_1, bins=n_count, weights=values)
    # # plt.xticks(times_1)


    arr1 = values[::2]
    arr2 = values[1::2]
    # np.save('./data/arr1_'+str(sit)+'_d', arr1)
    # np.save('./data/arr2_'+str(sit)+'_d', arr2)

    plt.hist(arr1, bins=np.arange(30), alpha=0.5)
    plt.hist(arr2, bins=np.arange(30), alpha=0.5)


    fig2 = plt.figure()
    # np.save('SPCM\data\pulses_rect_gauss\\kugfv\\#pulses_6_pulse_d'+str(sit)+'pause_d'+str(pause_sit)+'_nk_'+str(n_count//1000)+'k', times)
    plt.hist(times, bins=100)
    plt.xlim(500, 2000)
    plt.xticks(np.arange(500, 2000, 100))
    plt.grid()

    # interrupt_on_close(fig, job)  # Interrupts the job when closing the figure
    # while res.is_processing():
    #     new_counts = counts_handle.fetch_all()
    #     counts.append(new_counts["value"] / total_integration_time / 1000) # Umrechnung der Einheiten
    #     time.append(new_counts["timestamp"] / u.s)  # Convert timestamps to seconds
    #     plt.cla()
    #     if len(time) > 50:
    #         plt.plot(time[-50:], counts[-50:])
    #     else:
    #         plt.plot(time, counts)

    #     plt.xlabel("Time [s]")
    #     plt.ylabel("Counts [kcps]")
    #     plt.title("Counter")
    #     plt.pause(0.1)

    # fig, axs = plt.subplots(1)
    # fig.suptitle("Inputs from down conversion 1")

    # # Get data and average over the 10 pulses we generated earlier
    # adc_1 = u.raw2volts(res.get("adc1").fetch_all())
    # adc_1_cut = adc_1[800:126000+800]
    # data_adc_1 = np.reshape(adc_1_cut, (100, 1260))
    # data_avg = np.mean(data_adc_1, axis=0) #The averaged data of the 1000 pulsen in an array
    # print(len(adc_1_cut))
    # axs.plot(adc_1) # plot the averaged data
    


    #adc_str.buffer(int(100e6)).average().save('irgendwieanders')
    # Speichern als Textdatei in das angegebene Verzeichnis
    #np.savetxt('C:\\Users\\admin\\Nextcloud\\nanophotonics (2)\\AOM_Pulses_Mara\\Tisa\\averaged\\rectangular_simultanuous_pulse_break\\52_376.txt', data_avg)
    #adc_2 = u.raw2volts(res.get("adc2").fetch_all())
    # for i in range(10):
    #     axs[i].plot(data_adc_1[i,:])
    
    # ax1 = axs[0]
    # ax1.plot(adc_1, 'b', label="Signal")
    # #ax1.plot(adc_2, 'r', label="Signal", alpha=0.5)
    # ax1.set_title("amp VS time Input 1")
    # ax1.set_xlabel("Time [ns]")
    # ax1.set_ylabel("Signal amplitude [V]")
    # #ax1.plot(adc_2, 'r', label="Output")
    # ax1.legend()
    
    
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

