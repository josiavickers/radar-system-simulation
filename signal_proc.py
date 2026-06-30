import numpy as np
import matplotlib.pyplot as plt

def zero_pad(signal, target_length):
    pad_total = target_length - len(signal)
    pad_left = pad_total // 2
    pad_right = pad_total - pad_left

    signal_padded = np.pad(signal, (pad_left, pad_right), mode='constant')
    return signal_padded

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

    # FORGET BELOW, JUST KEEP TX SAMPLE RATE
    # self.fs = fs # update to Rx sample rate
    # N = len(self.samples)
    # self.t = np.arange(N)/self.fs
    # self.t_sim = N/self.fs

    return samples

def pulse_compression(tx_samples, rx_samples, fs, name, plot=True):
    h = np.conj(tx_samples[::-1]) # time-reversed complex conjugate of Tx signal
    y = np.convolve(rx_samples, h, mode="full")
    power = np.abs(y)**2
    power_dbm = 10 * np.log10(power + 1e-12) + 30

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

