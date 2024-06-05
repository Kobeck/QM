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
simulate = True


with program() as prog:
    with infinite_loop_():
        play("const" * amp(0.5), "AOM")#, duration=1e9 * u.ns)
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
    job.halt()

