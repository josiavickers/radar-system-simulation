import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from load_config import *

def get_if_filter_coeff():
    return sos

config = load_config("config.yaml")
tx_sample_freq = config["params"]["tx_sample_freq"]

# ------------------------------------------------------------
# Filter parameters extracted from LTspice result
# ------------------------------------------------------------
ORDER = 10
FC_HZ = 24.03e6          # -3 dB cutoff frequency
FS_HZ = tx_sample_freq   # sampling frequency of signal

GAIN_DB = -0.54          # insertion loss
GAIN = 10**(GAIN_DB / 20)

# ------------------------------------------------------------
# 1. Design the digital filter directly
# ------------------------------------------------------------
sos = signal.butter(
    ORDER,
    FC_HZ,
    btype="low",
    fs=FS_HZ,
    output="sos"
)

# Apply insertion loss
sos[:, :3] *= GAIN

# # ------------------------------------------------------------
# # 2. Model the digital transfer function H(z)
# # ------------------------------------------------------------
# # Convert second-order sections to numerator/denominator form
# b, a = signal.sos2tf(sos)

# # The digital transfer function is:
# #
# #        b[0] + b[1] z^-1 + b[2] z^-2 + ... + b[N] z^-N
# # H(z) = ----------------------------------------------------
# #        a[0] + a[1] z^-1 + a[2] z^-2 + ... + a[N] z^-N
# #

# # Frequency response
# f, H = signal.freqz(
#     b,
#     a,
#     worN=4096,
#     fs=FS_HZ
# )

# mag_db = 20 * np.log10(np.abs(H))
# phase_deg = np.angle(H, deg=True)

# plt.figure()
# plt.plot(f / 1e6, mag_db)
# plt.grid(True)
# plt.xlabel("Frequency [MHz]")
# plt.ylabel("Magnitude [dB]")
# plt.title("Digital 10th-order low-pass filter")
# plt.show()

# # ------------------------------------------------------------
# # 3. Apply the filter to a signal array
# # ------------------------------------------------------------
# # Example input signal
# t = np.arange(0, 5e-6, 1 / FS_HZ)

# x = (
#     np.sin(2 * np.pi * 5e6 * t)      # passes
#     + 0.5 * np.sin(2 * np.pi * 20e6 * t)   # mostly passes
#     + 0.5 * np.sin(2 * np.pi * 35e6 * t)   # attenuated
# )

# # Apply filter
# y = signal.sosfilt(sos, x)

# plt.figure()
# plt.plot(t * 1e6, x, label="Input")
# plt.plot(t * 1e6, y, label="Filtered output")
# plt.grid(True)
# plt.xlabel("Time [µs]")
# plt.ylabel("Amplitude")
# plt.legend()
# plt.show()