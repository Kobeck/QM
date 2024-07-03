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

qop_ip = "192.168.1.106"
cluster_name = "Cluster_RR_Lab"
qmm = QuantumMachinesManager(host=qop_ip, cluster_name=cluster_name)

simulate = False


with program() as prog:

    adc_st = declare_stream(adc_trace=True)
    
    measure("readout", "signal", adc_st)
    wait(25) #25 clock cycles = 100 ns
    play("const" * amp(0), "qe1")
    
    with stream_processing():
        adc_st.input1().save("adc1")
        adc_st.input2().save("adc2")
    
if simulate:
    job = qmm.simulate(config, prog, SimulationConfig(int(pulse_duration) // 4))  # duration in clock cycles, 4 ns
    samples = job.get_simulated_samples()
    x = samples.con1.analog["1"]
    NFFT = 2**10
    Fs = 1e9
    ax1 = plt.subplot(111)
    Pxx, freqs, bins, im = plt.specgram(x, NFFT=NFFT, Fs=Fs, noverlap=100, cmap=plt.cm.gist_heat)
    
    ax1.set_xticklabels((ax1.get_xticks() * 1e6).astype(int))
    ax1.set_yticklabels((ax1.get_yticks() / 1e6).astype(int))
    plt.xlabel("t [us]")
    plt.ylabel("f [MHz]")
    plt.show()
else:
    qm = qmm.open_qm(config)
    job = qm.execute(prog)
    res = job.result_handles
    res.wait_for_all_values()

    #plot results
    print(type(res.get("adc1")))
    adc1 = u.raw2volts(res.get("adc1").fetch_all())
    adc2 = u.raw2volts(res.get("adc2").fetch_all())

    np.savetxt("adc1.csv", adc1, delimiter=",")
    np.savetxt("adc2.csv", adc2, delimiter=",")

    #figures
    # fig, ax1= plt.subplots()   
    # plt.xlabel("Time [ns]")
    # plt.title("Single run")
    # plt.ylabel("Signal amplitude [V]")
    # ax1.plot(adc1, label="Pickup")
    
    # ax1.tick_params(axis='y', labelcolor='blue')
    # ax2 = ax1.twinx()
    # ax2.plot(adc2, label="Pulse", color='orange')
    # ax2.tick_params(axis='y', labelcolor='orange')
    # ax2.set_ybound(-0.5,0.5)
    # ax1.set_ybound(ax2.get_ybound())
    # fig.legend(["Pickup", "Pulse"])
    # plt.show()

    # time.sleep(10)
    job.halt()