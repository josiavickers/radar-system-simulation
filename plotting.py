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

    plt.xlabel("Input wave amplitude |x|")
    plt.ylabel("Output wave amplitude |y|")
    plt.title(f"{model_name} Characteristic")
    plt.grid(True)
    plt.legend()
    plt.show()

def _compression_point_dbm(am_in, am_out, gain, threshold_db):
    """
    Returns (in_dbm, out_dbm) where the output falls threshold_db below the
    ideal linear-gain line, searching from low to high drive and linearly
    interpolating across the bracketing samples for a precise crossing.
    Returns None if the data never reaches that much compression.
    """
    in_dbm = 10*np.log10(am_in**2 + 1e-12) + 30
    out_dbm = 10*np.log10(am_out**2 + 1e-12) + 30
    ideal_dbm = 10*np.log10((gain * am_in)**2 + 1e-12) + 30

    order = np.argsort(am_in)
    in_dbm_s, out_dbm_s, ideal_dbm_s = in_dbm[order], out_dbm[order], ideal_dbm[order]
    compression_db = ideal_dbm_s - out_dbm_s
    above = np.where(compression_db >= threshold_db)[0]
    if len(above) == 0 or above[0] == 0:
        return None
    idx = above[0]
    frac = (threshold_db - compression_db[idx-1]) / (compression_db[idx] - compression_db[idx-1])
    p_in = in_dbm_s[idx-1] + frac * (in_dbm_s[idx] - in_dbm_s[idx-1])
    p_out = out_dbm_s[idx-1] + frac * (out_dbm_s[idx] - out_dbm_s[idx-1])
    return p_in, p_out

def plot_am_am_curve_dbm(input, output, gain, model_name):
    am_in = np.abs(input)
    am_out = np.abs(output)

    in_dbm = 10*np.log10(am_in**2 + 1e-12) + 30
    out_dbm = 10*np.log10(am_out**2 + 1e-12) + 30
    ideal_dbm = 10*np.log10((gain * am_in)**2 + 1e-12) + 30

    plt.figure()
    plt.plot(in_dbm, out_dbm, label=model_name)
    plt.plot(in_dbm, ideal_dbm, "--", label="Ideal linear gain")

    # P1dB: 1 dB compression point
    p1db = _compression_point_dbm(am_in, am_out, gain, 1.0)
    if p1db is not None:
        plt.plot(*p1db, 'o', color='red', label=f"P1dB ({p1db[0]:.1f}, {p1db[1]:.1f}) dBm")

    # P3dB: 3 dB compression point (standard datasheet convention, more
    # robust than the raw max sample, which just tracks the highest
    # amplitude this particular pulse happened to reach)
    p3db = _compression_point_dbm(am_in, am_out, gain, 3.0)
    if p3db is not None:
        plt.plot(*p3db, 'x', color='green', label=f"P3dB ({p3db[0]:.1f}, {p3db[1]:.1f}) dBm")

    plt.xlabel("Input power (dBm)")
    plt.ylabel("Output power (dBm)")
    plt.title(f"{model_name} Characteristic (dBm)")
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

    plt.xlabel("Input wave amplitude |x|")
    plt.ylabel("Phase distortion (deg)")
    plt.title(f"{model_name} Curve")
    plt.grid(True)

    plt.show()

def plot_am_pm_curve_dbm(input, output, model_name):
    am_in = np.abs(input)
    in_dbm = 10*np.log10(am_in**2 + 1e-12) + 30

    phase_in = np.angle(input)
    phase_out = np.angle(output)
    am_pm = np.degrees(np.angle(np.exp(1j * (phase_out - phase_in))))

    plt.figure()
    plt.plot(in_dbm, am_pm, '.', markersize=2)

    plt.xlabel("Input power (dBm)")
    plt.ylabel("Phase distortion (deg)")
    plt.title(f"{model_name} Curve (dBm)")
    plt.grid(True)

    plt.show()