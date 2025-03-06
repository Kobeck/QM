import numpy as np
from qualang_tools.units import unit
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.loops import from_array
from qualang_tools.config.waveform_tools import *
import matplotlib.pyplot as plt

flat_length = 160
rf_length = 4

flattop_gauss = flattop_gaussian_waveform(0.5, flat_length, rf_length)
flattop_gauss = np.array(flattop_gauss)
plt.plot(-flattop_gauss)
plt.show()