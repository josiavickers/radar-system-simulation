import numpy as np
import matplotlib.pyplot as plt

class BasebandSignal:
    samples: np.ndarray # complex envelope
    fs: float # sample rate
    fc: float = 0.0 # carrier frequency
    t_sim: float # duration time
    t: np.array # time vector
    name: str # signal name
    tx_samples_ref: np.ndarray # reference Tx for matched filter

    def __init__(self, amp, fs, fc, t_sim, bandwidth, kaiser_beta, name):  
        self.amp = amp
        self.fs = fs
        self.fc = fc
        self.t_sim = t_sim
        self.bandwidth = bandwidth
        self.name = name

        N = int(fs*t_sim) # number of samples
        self.t = np.arange(N)/fs # time vector
        k = bandwidth / t_sim # linear chirp rate in Hz/s
        phi = 2 * np.pi * (0.5 * k * self.t**2) # linear chirp phase

        self.samples = amp*np.exp(1j*phi)

        # Apply window
        self.__window_function(kaiser_beta)
        self.tx_samples_ref = self.samples # remember tx ref for matched filter

    def __window_function(self, kaiser_beta):
        window = np.kaiser(len(self.samples), kaiser_beta)
        I = np.real(self.samples)*window
        Q = np.imag(self.samples)*window

        self.samples = I + 1j*Q # windowed signal

    def upconversion(self, fc):
        self.fc = self.fc + fc
    
    def downconversion(self, fc):
        self.fc = self.fc - fc

    def apply_channel(self, gain_dB, delay_samples, fs):
        self.linear_gain(gain_dB)
        self.__apply_time_delay(delay_samples)

        self.fs = fs # update to Rx sample rate
        N = len(self.samples)
        self.t = np.arange(N)/self.fs
        self.t_sim = N/self.fs

    def linear_gain(self, gain_dB):
        gain_amp = 10**(gain_dB / 20)
        self.samples = self.samples*gain_amp
    
    def __apply_time_delay(self, delay_samples):
        zeros = np.zeros(delay_samples, dtype=self.samples.dtype)
        self.samples = np.concatenate([zeros, self.samples])

    def matched_filter(self, plot=True):
        h = np.conj(self.tx_samples_ref[::-1]) # time-reversed complex conjugate of Tx signal
        y = np.convolve(self.samples, h, mode="full")
        mag = np.abs(y)

        if plot:
            t_mf = np.arange(len(y)) / self.fs # time axis
            plt.figure()
            plt.plot(t_mf, mag)
            plt.title(f"{self.name} Matched Filter Output")
            plt.xlabel("Time [s]")
            plt.ylabel("Magnitude")
            plt.grid(True)
            plt.show()

    def plot_bb_time_signal(self): 
        I = np.real(self.samples)
        Q = np.imag(self.samples)

        plt.figure()
        plt.plot(self.t, I, label="I (In-phase)")
        plt.plot(self.t, Q, label="Q (Quadrature)")
        plt.title(f"{self.name} Signal I and Q Lines")
        plt.xlabel("Time [s]")
        plt.ylabel("Wave Amplitude")
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_power_spectrum(self):
        spectrum = np.fft.fftshift(np.fft.fft(self.samples)) # freq spectrum envelope
        N = len(self.samples) # number of samples
        spectrum_amp = 2*spectrum/N # corrected spectrum amplitudes # IS THIS RIGHT?

        # Generate frequency axis
        f_bb = np.fft.fftshift(np.fft.fftfreq(N, d=1/self.fs))
        f_rf = f_bb + self.fc # centred at fc

        # Convert to dBm
        power_dbm = 20 * np.log10(np.abs(spectrum_amp) + 1e-12) + 30 # small epsilon to avoid log(0)

        # Plot
        plt.figure()
        plt.plot(f_rf/1e6, power_dbm)
        plt.title(f"{self.name} Power Spectrum")
        plt.xlabel("Frequency (MHz)")
        plt.ylabel("Power (dBm)")
        plt.grid(True)
        plt.show()
