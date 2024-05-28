from qualang_tools.config.waveform_tools import *
drag_len = 500  # length of pulse in ns
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

flattop_gaussian = flattop_gaussian_waveform(0.5, drag_len, 20)
print(len(flattop_gaussian))
#print(flattop_gaussian)
