
import numpy as np
from qualang_tools.units import unit
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.loops import from_array
from qualang_tools.config.waveform_tools import *
u = unit(coerce_to_integer=True)
pulse_duration = 1e5 # in ns 
readout_pulse_duration = 1e6# in ns
#max pulse length = 2^31-1 = 1e9.3319...
#possible values in steps of 4 because 4ns = 1clock cycle

# in ns
IF_freq = 3.1e6 # in Hz 5 MHz

drag_len = pulse_duration  # length of pulse in ns
drag_amp = 0.1  # amplitude of pulse in Volts
drag_del_f = 3e6  # Detuning frequency in Hz
drag_alpha = 1  # DRAG coefficient
drag_delta = -200e6 * 2 * np.pi  # in Hz


# DRAG Gaussian envelope:
drag_gauss_I_wf, drag_gauss_Q_wf = drag_gaussian_pulse_waveforms(drag_amp, drag_len, drag_len / 5, drag_alpha, drag_delta, drag_del_f, subtracted=False)  # pi pulse

# DRAG Cosine envelope:
drag_cos_I_wf, drag_cos_Q_wf = drag_cosine_pulse_waveforms(drag_amp, drag_len, drag_alpha, drag_delta, drag_del_f)  # pi pulse

# Flattop Cosine
flattop_cosine = flattop_cosine_waveform(0.2, 100, 5)

rf_length = 100  # in ns
flat_length = int( pulse_duration - 2 * rf_length)  # in ns
gauss_pulse_duration = int(2*rf_length + flat_length )
# Flattop Gaussian
flattop_gauss = flattop_gaussian_waveform(0.5, flat_length, rf_length)

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
        "qe1": {
            "singleInput": {
                "port": ("con1", 1)
            },
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
            "operations": {
                "const": "constPulse",
                "readout": "readout_pulse",
                "gauss": "gaussPulse",
            },
            "time_of_flight":  24,
            "smearing": 0,
            "intermediate_frequency": IF_freq,
            
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
        }
    },
    "pulses": {
        "constPulse": {
            "operation": "control",
            "length": pulse_duration,  # in ns
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