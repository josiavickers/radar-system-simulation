import numpy as np

class Signal:
    samples: np.ndarray # complex envelope
    fs: float # sample rate
    fc: float = 0.0 # nominal carrier frequency
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
        self.t = np.arange(len(samples))/self.fs

    def get_time_samples(self):
        return self.samples, self.t
    
    def get_freq_samples(self, span=None):
        spectrum = np.fft.fftshift(np.fft.fft(self.samples)) # freq spectrum envelope
        N = len(self.samples) # number of samples

        spectrum_watts = (np.abs(spectrum) / N)**2 # spectrum in Watts

        # Generate frequency axis (true frequencies, samples are physically mixed)
        f = np.fft.fftshift(np.fft.fftfreq(N, d=1/self.fs))

        # Convert to dBm
        power_dbm = 10 * np.log10(spectrum_watts) + 30

        # Only return bins within fc +/- span/2 around the nominal carrier
        if span is not None:
            mask = np.abs(f - self.fc) <= span / 2
            power_dbm, f = power_dbm[mask], f[mask]

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
        # Complex mixing
        self.samples = self.samples * np.exp(1j * 2 * np.pi * fc * self.t)
        self.fc = self.fc + fc
    
    def downconversion(self, fc):
        # Complex mixing
        self.samples = self.samples * np.exp(-1j * 2 * np.pi * fc * self.t)
        self.fc = self.fc - fc

    def iq_modulator(self, f_lo, lo_dbc=None):
        # Split the IF signal into its I and Q lines
        I = np.real(self.samples)
        Q = np.imag(self.samples)

        # LO leakage
        if lo_dbc is not None:
            d = 10**(lo_dbc / 20) * np.max(np.abs(np.fft.fft(self.samples))) / len(self.samples)
            I = I + d

        # Gain and phase mismatch 4*IRR = g^2 + p^2
        g = 0.0141
        p = 0.0141

        # Multiply each line with its LO and sum: real RF signal at f_IF + f_lo
        self.samples = (1+g) * I * np.cos(2 * np.pi * f_lo * self.t + p) - Q * np.sin(2 * np.pi * f_lo * self.t)
        self.fc = self.fc + f_lo

    def iq_demodulator(self, f_lo):
        # Multiply the real RF signal with the I and Q LOs. The factor 2 restores the
        # amplitude (mean of cos^2 = 1/2). The 2*f_lo products are removed by the IF
        # low-pass filter that follows.
        I = 2 * self.samples * np.cos(2 * np.pi * f_lo * self.t)
        Q = -2 * self.samples * np.sin(2 * np.pi * f_lo * self.t)
        self.samples = I + 1j * Q
        self.fc = self.fc - f_lo