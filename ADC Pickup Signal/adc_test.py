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
from scipy.fft import fft, ifft, fftfreq

qop_ip = "192.168.1.106"
cluster_name = "Cluster_RR_Lab"
qmm = QuantumMachinesManager(host=qop_ip, cluster_name=cluster_name)

### First example - Linear chirp
simulate = False
#pulse_duration = 1e6  # in ns = 1ms
rate = int(50e6 / pulse_duration) #4MHz in pulse duration
units = "Hz/nsec"


with program() as prog:
    #
    #f = declare(int)
    #with infinite_loop_():
    #with for_(*from_array(f, f_vec)):
        #update_frequency("qe1", f)
        #print("Playing at {f} Hz")
        #play("const" * amp(1), "qe1", chirp=(rate, units)) #for chirp the pulse duration has to be below 4e7 to work, else it defaults to IF
        #time.sleep(1e-3)
    #with infinite_loop_():
    adc_st = declare_stream(adc_trace=True)
    
    #with infinite_loop_():
    
    #time.sleep(1e-8)
    
    measure("readout", "signal", adc_st)
    #wait(25) #25 clock cycles = 100 ns

    play("const" * amp(0), "qe1", duration=1e5)#, duration=1e9 * u.ns)
    #reset_phase("qe1")
    #play("const", "qe1")
    #play("const" * amp(1), "qe1", chirp=(rate, units))
    play("gauss", "qe1")
    play("const" * amp(0), "qe1", duration=1e5)
    #play("const" * amp(0), "qe1")
    #play("gauss" * amp(1), "qe1")
    #play("const" * amp(0), "qe1")
    #play("gauss" * amp(1), "qe1")
    #play("const" * amp(0), "qe1")

    
    with stream_processing():
        adc_st.input1().save("adc1")
        adc_st.input2().save("adc2")
        adc_st.input1().fft(output="abs").save("adc1_fft")
        adc_st.input2().fft(output="abs").save("adc2_fft")
    
# The integration weights are, constant, of length 10*4*6 = 240
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
    print('Executing program')
    qm = qmm.open_qm(config)
    job = qm.execute(prog)
    res = job.result_handles
    res.wait_for_all_values()

    #plot results
    adc1 = u.raw2volts(res.get("adc1").fetch_all())
    adc2 = u.raw2volts(res.get("adc2").fetch_all())
    
    fft1 = res.get("adc1_fft").fetch_all()
    fft2 = res.get("adc2_fft").fetch_all()
    np.savetxt("C:/Users/admin/QM/adc1.csv", adc1, delimiter=",")
    np.savetxt("C:/Users/admin/QM/adc2.csv", adc2, delimiter=",")
    np.savetxt("C:/Users/admin/QM/fft1.csv", fft1, delimiter=",")
    np.savetxt("C:/Users/admin/QM/fft2.csv", fft2, delimiter=",")

    #figures
    fig, ax1= plt.subplots()   
    plt.xlabel("Time [ns]")
    plt.title("Single run")
    plt.ylabel("Signal amplitude [V]")
    ax1.plot(adc1, label="Pickup")
    
    ax1.tick_params(axis='y', labelcolor='blue')
    ax2 = ax1.twinx()
    ax2.plot(adc2, label="Pulse", color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')
    ax2.set_ybound(-0.5,0.5)
    ax1.set_ybound(ax2.get_ybound())
    fig.legend(["Pickup", "Pulse"])

    plt.show()
    #ax2.ylabel("Signal amplitude [V]")
## FFT
    N = len(adc2)
    # sample spacing
    T = 1e-9 #1 readout every 4 ns
    x = np.linspace(0.0, N*T, N, endpoint=False)
    y1 = adc1
    y2 = adc2
    yf1 = fft(y1)
    yf2 = fft(y2)

    xf = fftfreq(N, T)[:N//2]
    plt.plot(xf, 2.0/N * np.abs(yf1[0:N//2]))
    plt.plot(xf, 2.0/N * np.abs(yf2[0:N//2]))
    plt.grid()
    #fig2, ax3 = plt.subplots()
    plt.title("FFT")
    plt.xlabel("Frequency [Hz]")
    plt.xlim(-1e3, 1e4)
    #plt.ylim(0, 0.05)
    plt.legend(["Pickup", "Pulse"])
    #ax3.plot(fft2)
    #ax4 = ax3.twinx()
    #ax4.plot(fft2)
    plt.show()

    # time.sleep(10)
    job.halt()

