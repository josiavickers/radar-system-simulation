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

def plot_power_spectrum_grid(subplot_groups, title, ncols=2):
    """
    subplot_groups: list where each element is a list of (f, power_dbm, label)
                    tuples to draw on one subplot. A group with 2+ tuples
                    overlays those curves (with a legend); a group with 1
                    tuple is a plain single-curve subplot.
    """
    n = len(subplot_groups)
    ncols = min(ncols, n)
    nrows = -(-n // ncols) # ceil division

    fig, axes = plt.subplots(nrows, ncols, figsize=(6*ncols, 4*nrows), squeeze=False)
    flat_axes = axes.flatten()

    for ax, group in zip(flat_axes, subplot_groups):
        for f, power_dbm, label in group:
            ax.plot(f/1e6, power_dbm, label=label)

        ax.set_title(group[0][2] if len(group) == 1 else " vs ".join(g[2] for g in group))
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("Power (dBm)")
        ax.grid(True)
        if len(group) > 1:
            ax.legend()

    for ax in flat_axes[n:]:
        ax.set_visible(False)

    fig.suptitle(title)
    fig.tight_layout()
    plt.show()

def plot_am_am_curve(input, output, gain, model_name):
    am_in = np.abs(input)
    am_out = np.abs(output)

    plt.figure()
    plt.plot(am_in, am_out, label=model_name)
    plt.plot(am_in, gain * am_in, "--", label="Ideal linear gain")
    # plt.axhline(A_sat, linestyle=":", label=r"$A_{sat}$")

    plt.xlabel("Input amplitude |x|")
    plt.ylabel("Output amplitude |y|")
    plt.title(f"{model_name} Characteristic")
    plt.grid(True)
    plt.legend()
    plt.show()

def plot_am_pm_curve(input, output, model_name):
    # Magnitudes
    am_in = np.abs(input)

    # Phase difference
    phase_in = np.angle(input)
    phase_out = np.angle(output)
    am_pm = np.degrees(np.angle(np.exp(1j * (phase_out - phase_in))))

    plt.figure()
    plt.plot(am_in, am_pm, '.', markersize=2)

    plt.xlabel("Input amplitude |x|")
    plt.ylabel("Phase distortion (deg)")
    plt.title(f"{model_name} Curve")
    plt.grid(True)

    plt.show()