import matplotlib.pyplot as plt
import numpy as np
 
# Plot I and Q versus sample index (time domain)
def plot_IQ_time_domain(I, Q, signal_name):
    plt.figure()
    plt.plot(I, label="I (In-phase)")
    plt.plot(Q, label="Q (Quadrature)")
    plt.title(f"{signal_name}: I and Q Lines")
    plt.xlabel("Sample index n")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()
 
# Plot constellation diagram
def plot_IQ_constellation(I, Q):
    plt.scatter(I, Q)
    plt.title("IQ Constellation Plot")
    plt.xlabel("I")
    plt.ylabel("Q")
    plt.axis("equal")
    plt.grid(True)
    plt.show()
 
# Plot magnitude and phase versus smaple index
def plot_mag_and_phase_time_domain(complex_signal, signal_name):
    # Plot magnitude
    plt.figure()
    plt.plot(np.abs(complex_signal))
    plt.title(f"{signal_name} Magnitude")
    plt.grid(True)
    plt.show()
 
    # Plot phase
    plt.figure()
    plt.plot(np.angle(complex_signal))
    plt.title(f"{signal_name} Phase")
    plt.grid(True)
    plt.show()
 
# Plot amplitude of frequency spectrum
def plot_mag_spectrum(complex_signal, num_samples, f_s, signal_name):
    s = np.fft.fft(complex_signal)
    s_shifted = np.fft.fftshift(s)
 
    # Frequency axis
    freqs = np.fft.fftfreq(num_samples, 1/f_s)
    freqs_shifted = np.fft.fftshift(freqs)
 
    # Plot magnitude
    plt.figure()
    plt.plot(freqs_shifted/1e6, 20*np.log10(np.abs(s_shifted)))
    plt.title(f"{signal_name} Magnitude Spectrum")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Magnitude (dBV)")
    plt.grid(True)
    plt.show()

def plot_power_spectrum(complex_signal, num_samples, f_s, signal_name):
    # FFT
    s = np.fft.fft(complex_signal)
    s_shifted = np.fft.fftshift(s)

    # Frequency axis
    freqs = np.fft.fftfreq(num_samples, 1 / f_s)
    freqs_shifted = np.fft.fftshift(freqs)

    # Power spectrum
    power = np.abs(s_shifted) ** 2

    # Convert to dB 
    power_db = 10 * np.log10(power + 1e-12) # add small epsilon to avoid log(0)

    # Plot
    plt.figure()
    plt.plot(freqs_shifted / 1e6, power_db)
    plt.title(f"{signal_name} Power Spectrum")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Power (dBW)")
    plt.grid(True)
    plt.show()

def plot_AM_AM_curve(Pin_dB, Pout_dB):
    plt.figure()
    plt.plot(Pin_dB, Pout_dB, 'o-', label="PA Transfer Curve")
    plt.plot(Pin_dB, Pin_dB, '--', label="Ideal Linear PA")

    plt.xlabel("Input Power (dBW)")
    plt.ylabel("Output Power (dBW)")
    plt.title("PA AM/AM Curve")
    plt.grid(True)
    plt.legend()
    plt.show()
