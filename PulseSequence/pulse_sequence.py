"""
chirp.py: Introduction to chirp
Author: Gal Winer - Quantum Machines
Created: 17/01/2021
Revised by Tomer Feld - Quantum Machines
Revision date: 04/04/2022
"""
import os
import time
from qm import QuantumMachinesManager
from qm.qua import *
from qm import SimulationConfig
from qm.octave import *
from qm.octave.octave_manager import ClockMode
import numpy as np
import matplotlib.pyplot as plt
from qualang_tools import units as u
from configuration import *
from scipy.fft import fft, ifft, fftfreq
from scipy.signal import periodogram


con = "con1"
octave = "octave1"
octave_config = QmOctaveConfig() # creates an octave config object
octave_config.add_device_info(octave, qop_ip, octave_port)
opx_port = None

qop_ip = "192.168.1.106"
cluster_name = "Cluster_RR_Lab"
octave_port = 11241

qmm = QuantumMachinesManager(host=qop_ip, port=opx_port, cluster_name=cluster_name, octave=octave_config, log_level="DEBUG")
qm = qmm.open_qm(config)
simulate = False

qm.octave.set_rf_output_gain("SiV", -10)
with program() as sequence:
    adc_str = declare_stream(adc_trace=True)
    measure("readout", "Meas", adc_str)
    print(type(adc_str))
    amplitude = 0.5


    # initializazation delay
    play("cw" * amp(0), "SiV", duration=delay_len)

    reset_phase("SiV")
    play("pi_half" * amp(amplitude), "SiV")
    # 8 pulses
    for i in range(8):
        play("cw"* amp(0), "SiV", duration=delay_len)
        reset_phase("SiV")
        play("pi" * amp(amplitude), "SiV",)
        play("cw"* amp(0), "SiV", duration=delay_len)
    
    reset_phase("SiV")
    play("pi_half" * amp(amplitude), "SiV")

    with stream_processing():
        adc_str.input1().save("adc1")
        adc_str.input2().save("adc2")

# The integration weights are, constant, of length 10*4*6 = 240
if simulate:
    job = qmm.simulate(config, sequence, SimulationConfig(int(pulse_len) // 4))  # duration in clock cycles, 4 ns
    samples = job.get_simulated_samples()
    x = samples.con1.analog["1"]
    plt.plot(x)
else:
    print('Executing program')
    qm = qmm.open_qm(config)
    job = qm.execute(sequence)
    # time.sleep(10)
    res = job.result_handles
    res.wait_for_all_values()
    job.halt()
    #fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1 = plt.subplot()
    # fig.suptitle("Inputs from down conversion 1")
    adc_1 = u.raw2volts(res.get("adc1").fetch_all())
    adc_2 = u.raw2volts(res.get("adc2").fetch_all())
    ax1.plot(adc_1, 'b', label="Pickup")
    ax1.set_title("amp VS time Input 1")
    ax1.set_xlabel("Time [ns]")
    ax1.set_ylabel("Signal amplitude [V]")
    ax1.plot(adc_2, 'r', label="Output")
    ax1.legend()
    plt.show()
