import numpy as np

# Low Noise Amplifier
def LNA_linear(rf_signal, gain):
    return rf_signal*gain

# Downconversion from real RF to complex IF
def RF_downconversion(rf_signal, num_samples, f_s, f_RF):
    n = np.arange(num_samples)
    cos_carrier = np.cos(2 * np.pi * f_RF * n / f_s)
    sin_carrier = np.sin(2 * np.pi * f_RF * n / f_s)

    I = rf_signal * cos_carrier
    Q = -rf_signal * sin_carrier   # neg sign to downcovert: cos - jsin = e^-jwt

    s_IF = I + 1j*Q
    return s_IF

# Downconversion to from IF to BB
def IF_downconversion(if_signal, num_samples, f_s, f_IF):
    n = np.arange(num_samples)
    lo = np.exp(-1j * 2 * np.pi * f_IF * n / f_s)
    bb = if_signal * lo
    return bb
