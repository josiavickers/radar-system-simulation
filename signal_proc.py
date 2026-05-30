import numpy as np
import matplotlib.pyplot as plt

def window_function(samples, kaiser_beta):
    window = np.kaiser(len(samples), kaiser_beta)
    I = np.real(samples)*window
    Q = np.imag(samples)*window

    samples = I + 1j*Q # windowed signal

    return samples

def linear_gain(samples, gain_dB):
    gain_amp = 10**(gain_dB / 20)
    samples *= gain_amp

    return samples

def apply_time_delay(samples, delay_samples):
    zeros = np.zeros(delay_samples, dtype=samples.dtype)
    samples = np.concatenate([zeros, samples])
    
    return samples

def apply_channel(samples, gain_dB, delay_samples):
    samples = linear_gain(samples, gain_dB)
    samples = apply_time_delay(samples, delay_samples)

    # FORGET BELOW, JUST KEEP TX SAMPLE RATE
    # self.fs = fs # update to Rx sample rate
    # N = len(self.samples)
    # self.t = np.arange(N)/self.fs
    # self.t_sim = N/self.fs

    return samples

def pulse_compression(tx_samples, rx_samples, fs, name, plot=True):
    h = np.conj(tx_samples[::-1]) # time-reversed complex conjugate of Tx signal
    y = np.convolve(rx_samples, h, mode="full")
    mag = np.abs(y)

    if plot:
        t_mf = np.arange(len(y)) / fs # time axis
        plt.figure()
        plt.plot(t_mf*1e6, mag)
        plt.title(f"{name} Pulse Compression Output")
        plt.xlabel("Time (us)")
        plt.ylabel("Magnitude (Wave amplitude)") # ASK THOMAS WHAT THE UNIT FOR WAVE AMPLITUDE SHOULD BE?
        plt.grid(True)
        plt.show()

