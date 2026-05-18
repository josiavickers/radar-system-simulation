import numpy as np
import matplotlib.pyplot as plt

class BasebandSignal:
    samples: np.ndarray # complex envelope
    fs: float # sample rate
    fc: float = 0.0 # carrier frequency
    t_sim: float # duration time
    t: np.array # time vector

    def __init__(self, amp, fs, fc, t_sim):  
        self.amp = amp
        self.fs = fs
        self.fc = fc
        self.t_sim = t_sim

        N = int(fs*t_sim) # number of samples
        self.t = np.linspace(0,t_sim,N) # time vector
        w = 2*np.pi*5000000 # omega vector (FIXED AT 50HZ NOW)

        self.samples = amp*np.exp(1j*w*self.t)

    def plot_time_signal(self):
        I = np.real(self.samples)
        Q = np.imag(self.samples)

        plt.figure()
        plt.plot(self.t, I, label="I (In-phase)")
        plt.plot(self.t, Q, label="Q (Quadrature)")
        plt.title("Signal I and Q Lines")
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_power_spectrum(self):
        spectrum = np.fft.fftshift(np.fft.fft(self.samples))


    # def plot_power_spectrum(signal, f_s, f_c, signal_name):
    #     N = len(signal)

    #     # FFT
    #     S = np.fft.fftshift(np.fft.fft(signal))

    #     # Frequency axis
    #     freqs = np.fft.fftshift(np.fft.fftfreq(N, d=1/f_s))

    #     f_upconverted = freqs + f_c # plot relative to carrier 

    #     # Correct wave amplitudes
    #     S_normalised = 2*S/N

    #     # Convert wave amplitude to dBm 
    #     power_dbm = 20 * np.log10(S_normalised + 1e-12) + 30 # add small epsilon to avoid log(0)

    #     # Plot
    #     plt.figure()
    #     plt.plot(f_upconverted / 1e6, power_dbm)
    #     plt.title(f"{signal_name} Power Spectrum")
    #     plt.xlabel("Frequency (MHz)")
    #     plt.ylabel("Power (dBm)")
    #     plt.grid(True)
    #     plt.show()
