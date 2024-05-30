import os
import numpy as np
from qm.octave import QmOctaveConfig 
from set_octave import OctaveUnit, octave_declaration
from qualang_tools.units import unit
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.loops import from_array
from qualang_tools.config.waveform_tools import *

u = unit(coerce_to_integer=True)

###########
# Network #
###########

qop_ip = "192.168.1.106"
cluster_name = "Cluster_RR_Lab"
qop_port = None

octave_port = 11241
octave_1 = OctaveUnit("octave1", qop_ip, port=octave_port, con="con1")
octaves = [octave_1]
octave_config = octave_declaration(octaves)


#############
# Variables #
#############

#Frequencies
SiV_LO_freq = 13e9 #spin spin transition 
LO = SiV_LO_freq
SiV_IF_freq = 3.1e6 #RF Frequency for nuclear spins
#pulse lenghts
pulse_len = 1000
initializazion_len = 3000 * u.ns
readout_pulse_len = 10000 * u.ns

delay_len = 200 * u.ns #time between pi pulses
pi_half_len = 16 * u.ns
pi_len = 32 * u.ns 

rf_length = 1  # in ns
half_flat_length = int( pi_half_len - 2 * rf_length)  # in ns
flat_length = int( pi_len - 2 * rf_length)
gauss_half_pulse_duration = int(2*rf_length + flat_length )
# Flattop Gaussian
flattop_half_gauss = flattop_gaussian_waveform(0.5, half_flat_length, rf_length)
flattop_gauss = flattop_gaussian_waveform(0.5, flat_length, rf_length)
##########
# LIMITS #
##########
#max pulse length = 2^31-1 = 1e9.3319...
#max pulse length = 1 ms (for some reason... reference qua-libs NV scripts)
#possible values in steps of 4 because 4ns = 1clock cycle

trigger_delay = 87  # 57ns with QOP222 and above otherwise 87ns
trigger_buffer = 15  # 18ns with QOP222 and above otherwise 15ns
detection_delay = 87 

signal_threshold = -2.000 #ADC Units


octave = "octave1"
con = "con1"
config = {
    "version": 1,
    "controllers": {
        con: {
            "analog_outputs": {
                1: {"offset": 0.0},
                2: {"offset": 0.0}, 
                3: {"offset": 0.0}, 
                4: {"offset": 0.0},
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
            "RF_inputs": {"port": (octave, 1)},
            "RF_outputs": {"port": (octave, 1)},
            "intermediate_frequency": SiV_IF_freq,
            "operations": {
                "cw": "constPulse",
                "readout": "readoutPulse",
                "pi": "piPulse",
                "pi_half": "piHalfPulse",
            },
            "digitalInputs": {
                "switch": {
                    "port": ("con1", 1),
                    "delay": trigger_delay,
                    "buffer": trigger_buffer,
                },
            },
            "time_of_flight": 24,
            "smearing": 0,
        },
        # "SPCM": {
        #     "singleInput": {"port": ("con1", 1)},
        #     "digitalInputs": {  # for visualization in simulation
        #         "switch": {
        #             "port": ("con1", 1),
        #             "delay": 87,
        #             "buffer": 15,
        #         },
        #     },
        #     "operations": {
        #         "readout": "readoutPulse",
        #     },
        #     "outputs": {"out1": ("con1", 1)},
        #     "outputPulseParameters": {
        #         "signalThreshold": signal_threshold,  # ADC units
        #         "signalPolarity": "Below",
        #         "derivativeThreshold": -2_000,
        #         "derivativePolarity": "Above",
        #     }, 
        #     "intermediate_frequency": SiV_IF_freq,
        #     "time_of_flight": detection_delay,
        #     "smearing": 0,
        # },
        "signal": {
            "RF_inputs": {
                "port": (octave, 2),
            },
            "RF_outputs": {
                "out1": (octave, 2),
            },
            "digitalInputs": {  # for visualization in simulation
                "switch": {
                    "port": (con, 3),
                    "delay": 87,
                    "buffer": 15,
                },
            },
            "time_of_flight":  24,
            "smearing": 0,
            "intermediate_frequency": SiV_IF_freq,
            "operations": {
                "readout": "readoutPulse",
            },
        },
    },
    "octaves": {
        octave: {
            "RF_outputs": {
                1: {
                    "LO_frequency": LO,
                    "LO_source": "internal",  # can be external or internal. internal is the default
                    "output_mode": "always_on",  # can be: "always_on" / "always_off"/ "triggered" / "triggered_reversed". "always_off" is the default
                    "gain": 0,  # can be in the range [-20 : 0.5 : 20]dB
                },
                2: {
                    "LO_frequency": LO,
                    "LO_source": "internal",
                    "output_mode": "always_on",
                    "gain": 0,
                },
            },
            "RF_inputs": {
                1: {
                    "LO_frequency": LO,
                    "LO_source": "internal",  # internal is the default
                    "IF_mode_I": "direct",  # can be: "direct" / "mixer" / "envelope" / "off". direct is default
                    "IF_mode_Q": "direct",
                },
                2: {
                    "LO_frequency": LO,
                    "LO_source": "external",  # external is the default
                    "IF_mode_I": "direct",
                    "IF_mode_Q": "direct",
                },
            },
            "connectivity": con,
        }
    },
    "pulses": {
        "constPulse": {
            "operation": "control",
            "length": pulse_len,  # in ns
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "piPulse": {
            "operation": "control",
            "length": pi_len,  # in ns
            "waveforms": {
                "I": "gauss_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "piHalfPulse": {
            "operation": "control",
            "length": pi_half_len,  # in ns
            "waveforms": {
                "I": "gauss_half_wf",
                "Q": "zero_wf",
            },
            "digital_marker": "ON",
        },
        "readoutPulse": {
            "operation": "measurement",
            "length": readout_pulse_len,
            "digital_marker": "ON",
            "waveforms": {"I": "readout_wf", "Q": "zero_wf",},
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
        "gauss_half_wf": {
            "type": "arbitrary",
            "samples": flattop_half_gauss,
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