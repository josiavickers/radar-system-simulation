import numpy as np

class Signal:
    samples: np.ndarray # complex envelope
    fs: float # sample rate
    fc: float = 0.0 # carrier frequency
    t_sim: float # duration time
    t: np.array # time vector

    def __init__(self, fs, fc, t_sim):  
        self.fs = fs
        self.fc = fc
        self.t_sim = t_sim

        N = int(fs*t_sim) # number of samples
        self.t = np.arange(N)/fs # time vector
        self.samples = np.zeros(N, dtype=complex) # samples

    def update_samples(self, samples):
        self.samples = samples

    def get_time_samples(self):
        return self.samples, self.t
    
    def get_freq_samples(self):
        spectrum = np.fft.fftshift(np.fft.fft(self.samples)) # freq spectrum envelope
        N = len(self.samples) # number of samples
        spectrum_amp = 2*spectrum/N # corrected spectrum amplitudes # IS THIS RIGHT?

        # Generate frequency axis
        f = np.fft.fftshift(np.fft.fftfreq(N, d=1/self.fs)) + self.fc

        # Convert to dBm
        power_dbm = 20 * np.log10(np.abs(spectrum_amp) + 1e-12) + 30 # small epsilon to avoid log(0)

        return power_dbm, f

class Pulse(Signal):
    name: str # signal name

    def __init__(self, fs, fc, t_sim, amp, bandwidth, name):
        super().__init__(fs, fc, t_sim)
        self.name = name

        # Initialise pulse
        k = bandwidth / t_sim # linear chirp rate in Hz/s
        phi = 2 * np.pi * (0.5 * k * self.t**2) # linear chirp phase

        self.samples = amp*np.exp(1j*phi)

    def upconversion(self, fc):
        self.fc = self.fc + fc
    
    def downconversion(self, fc):
        self.fc = self.fc - fc
