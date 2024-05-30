import os
import numpy as np
from qm.octave import QmOctaveConfig 
from qualang_tools.units import unit
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.loops import from_array
from qualang_tools.config.waveform_tools import *

u = unit(coerce_to_integer=True)

#############
# Variables #
#############

#Frequencies
SiV_freq = 13.6 * u.GHz #spin spin transition 
SiV_IF_freq = 3.1 * u.MHz #RF Frequency for nuclear spins

#pulse lenghts
pulse_len = 300 * u.ns
initializazion_len = 3000 * u.ns
readout_pulse_len = 1e6 * u.ns
delay_len = 200 * u.ns #time between pi pulses
pi_half_len = 15 * u.ns
pi_len = 30 * u.ns 
##########
# LIMITS #
##########
#max pulse length = 2^31-1 = 1e9.3319...
#max pulse length = 1 ms (for some reason... reference qua-libs NV scripts)
#possible values in steps of 4 because 4ns = 1clock cycle

##gaussian rise and fall
rf_length = 10 # in ns
flat_length = int( pulse_duration - 2 * rf_length)  
gauss_pulse_duration = int(2*rf_length + flat_length )

# Flattop Gaussian
flattop_gauss = flattop_gaussian_waveform(0.5, flat_length, rf_length)  #tool to create samples

####
ocatve_config = QmOctaveConfig()
ocatve_config.set_calibration_db(os.getcwd())
ocatve_config.add_device_info("octave1", octave_ip, octave_port)

trigger_delay = 87  # 57ns with QOP222 and above otherwise 87ns
trigger_buffer = 15  # 18ns with QOP222 and above otherwise 15ns

config = {
    "version": 1,
    "controllers": {
        "con1": {
            "analog_outputs": {
                1: {"offset": 0.0, "delay": 0},
                2: {"offset": 0.0, "delay": 0}, 
                3: {"offset": 0.0, "delay": 0}, 
            },
            "digital_outputs": {
                1: {},  # AOM/Laser
                2: {},  # AOM/Laser
                3: {},  # SPCM1 - indicator
                4: {},  # SPCM2 - indicator
            },
            "analog_inputs": {
                1: {"offset": 0},
                2: {"offset": 0},
            },

        },
    },
    "elements": {
        "SiV": {
            "RF_inputs": {"port": ("octave1", 1)},
            "intermediate_frequency": SiV_IF_freq,
            "operations": {
                "cw": "constPulse",
                "pi_half": "pi_half_pulse",
                "pi": "pi_pulse",
            },
            "digitalInputs": {
                "marker": {
                    "port": ("con1", 1),
                "delay": trigger_delay,
                "buffer": trigger_buffer,
                },
            },
        },
        "SPCM": {
            "singleInput": {"port": ("con1", 1)},
            "digitalInputs": {  # for visualization in simulation
                "marker": {
                    "port": ("con1", 3),
                    "delay": detection_delay,
                    "buffer": 0,
                },
            },
            "operations": {
                "readout": "readout_pulse",
            },
            "outputs": {"out1": ("con1", 1)},
            "outputPulseParameters": {
                "signalThreshold": signal_threshold_1,  # ADC units
                "signalPolarity": "Below",
                "derivativeThreshold": -2_000,
                "derivativePolarity": "Above",
            }, 
            "time_of_flight": detection_delay,
            "smearing": 0,
        },
        "signal": {
            "singleInput": {"port": ("con1", 1)},  # not used
            "outputs": {
                "out1": ("con1", 1), # output channel 1
                "out2": ("con1", 2)
            }, 
            "digitalInputs": {  # for visualization in simulation
                "marker": {
                    "port": ("con1", 3),
                    "delay": 0,
                    "buffer": 0,
                },
            },
            "outputPulseParameters": {
                "signalThreshold": -2_000,  # ADC units
                "signalPolarity": "Below",
                "derivativeThreshold": -2_000,
                "derivativePolarity": "Above",
            },
            "time_of_flight":  24,
            "smearing": 0,
            "intermediate_frequency": IF_freq,
            "operations": {
                "readout": "readout_pulse",
            },
        },
    },
    "octaves": {
        "octave1": {
            "RF_outputs": {
                1: {
                    "LO_frequency": SiV_freq,
                    "LO_source": "internal",  # can be external or internal. internal is the default
                    "output_mode": "always_on",  # can be: "always_on" / "always_off"/ "triggered" / "triggered_reversed". "always_off" is the default
                    "gain": 0,  # can be in the range [-20 : 0.5 : 20]dB
                },
            },
            "connectivity": "con1",
        },
    },

    "pulses": {
        "constPulse": {
            "operation": "control",
            "length": pulse_len,  # in ns
            "waveforms": {"single": "const_wf"},
        },
        "gaussPulse": {
            "operation": "control",
            "length":  gauss_pulse_duration, # in ns
            "waveforms": {"single": "gauss_wf"},
        },
        "readout_pulse": {
            "operation": "measurement",
            "length": readout_pulse_duration,
            "digital_marker": "ON",
            "waveforms": {"single": "zero_wf"},
        },
    },
    "waveforms": {
        "zero_wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "const_wf": {
            "type": "constant", "sample": 0.2
        },
        "gauss_wf": {
            "type": "arbitrary",
            "samples": flattop_gauss,
        },
        "readout_wf": {
            "type": "constant",
            "sample": 0.2,
        },
    },
    "digital_waveforms": {
        "ON": {"samples": [(1, 0)]},  # [(on/off, ns)]
        "OFF": {"samples": [(0, 0)]},  # [(on/off, ns)]
    },
    "integration_weights": {
        "cosine_weights": {
            "cosine": [(1.0, 1000)],
            "sine": [(0.0, 1000)],
        },
        "sine_weights": {
            "cosine": [(0.0, 1000)],
            "sine": [(1.0, 1000)],
        },
        "minus_sine_weights": {
            "cosine": [(0.0, 1000)],
            "sine": [(-1.0, 1000)],
        },
    },
}