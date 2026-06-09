import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# 10th order FEC IF Filter X-Band
ORDER = 10
FC_HZ = 24.03e6
GAIN_DB = -0.54
GAIN = 10**(GAIN_DB / 20)

# Design analog Butterworth filter
b, a = signal.butter(
    ORDER,
    2 * np.pi * FC_HZ,
    btype="low",
    analog=True
)

# Apply insertion loss
b = GAIN * b

# Frequency vector
f = np.logspace(6, np.log10(40e6), 1000)
w = 2 * np.pi * f

# Evaluate transfer function H(jw)
_, H = signal.freqs(b, a, worN=w)

# Convert to magnitude and phase
mag_db = 20 * np.log10(np.abs(H))
phase_deg = np.angle(H, deg=True)

plt.figure()
plt.semilogx(f / 1e6, mag_db)
plt.grid(True, which="both")
plt.xlabel("Frequency [MHz]")
plt.ylabel("Magnitude [dB]")
plt.title("10th-order low-pass transfer function")
plt.show()