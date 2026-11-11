import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve

def apply_window(samples, kaiser_beta):
    window = np.kaiser(len(samples), kaiser_beta)
    I = np.real(samples)*window
    Q = np.imag(samples)*window

    return I + 1j*Q # windowed signal

def linear_gain(samples, gain_dB):
    gain_amp = 10**(gain_dB / 20)
    return samples * gain_amp

def apply_time_delay(samples, delay_samples):
    zeros = np.zeros(delay_samples, dtype=samples.dtype)
    samples = np.concatenate([zeros, samples])
    
    return samples

def apply_channel(samples, gain_dB, delay_samples):
    samples = linear_gain(samples, gain_dB)
    samples = apply_time_delay(samples, delay_samples)

    return samples

def pulse_compression(tx_samples, rx_samples, fs, name, plot=True):
    h = np.conj(tx_samples[::-1]) # time-reversed complex conjugate of Tx signal
    y = fftconvolve(rx_samples, h, mode="full")
    power = np.abs(y)**2
    power_dbm = 10 * np.log10(power) + 30

    if plot:
        t_mf = np.arange(len(y)) / fs # time axis
        fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(8, 6))
        fig.suptitle(f"{name} Pulse Compression Output")

        ax_lin.plot(t_mf*1e6, power)
        ax_lin.set_ylabel("Power (W)")
        ax_lin.set_title("Linear")
        ax_lin.set_xlabel("Time (us)")
        ax_lin.grid(True)

        ax_log.plot(t_mf*1e6, power_dbm)
        ax_log.set_ylabel("Power (dBm)")
        ax_log.set_title("Logarithmic")
        ax_log.set_xlabel("Time (us)")
        ax_log.grid(True)

        fig.tight_layout()
        plt.show()

    return y
