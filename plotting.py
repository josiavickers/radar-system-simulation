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

def plot_am_am_curve(input, output, gain):
    am_in = np.abs(input)
    am_out = np.abs(output)

    plt.figure()
    plt.plot(am_in, am_out, label="Rapp AM/AM")
    plt.plot(am_in, gain * am_in, "--", label="Ideal linear gain")
    # plt.axhline(A_sat, linestyle=":", label=r"$A_{sat}$")

    plt.xlabel("Input amplitude |x|")
    plt.ylabel("Output amplitude |y|")
    plt.title("Rapp Model AM/AM Characteristic")
    plt.grid(True)
    plt.legend()
    plt.show()