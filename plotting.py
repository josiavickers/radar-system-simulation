import numpy as np
import matplotlib.pyplot as plt

def plot_time_signal(samples, t, name): 
    I = np.real(samples)
    Q = np.imag(samples)

    plt.figure()
    plt.plot(t*1e6, I, label="I (In-phase)")
    plt.plot(t*1e6, Q, label="Q (Quadrature)")
    plt.title(f"{name} Signal I and Q Lines")
    plt.xlabel("Time (us)")
    plt.ylabel("Wave Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_power_spectrum(samples, f, name):
    plt.figure()
    plt.plot(f/1e6, samples)
    plt.title(f"{name} Power Spectrum")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Power (dBm)")
    plt.grid(True)
    plt.show()