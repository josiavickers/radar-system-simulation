import numpy as np

def apply_attenuation(signal, gain):
    return signal*gain

# NEED TO CHECK IF THIS IS WORKING PROPERLY - PLOT PHASE FUNCTION NEEDED!
def apply_time_delay(signal, tau, f_s):
    N = len(signal)

    # Frequency vector
    f = np.fft.fftfreq(N, 1/f_s)

    # FFT of the signal
    S = np.fft.fft(signal)

    # Apply phase shift for delay
    phase_shift = np.exp(-1j * 2 * np.pi * f * tau)
    S_delayed = S * phase_shift

    # IFFT back to time domain
    s_delayed = np.fft.ifft(S_delayed)
    return np.real(s_delayed)