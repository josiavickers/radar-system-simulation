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

def plot_mag_time(outputs, t, name):
    """
    outputs: dict {label: complex samples}, all drawn on the same axes
    t:       time vector shared by all cases
    """
    plt.figure()
    for label, samples in outputs.items():
        wave_amp = np.abs(samples)
        power_dbm = 10 * np.log10(wave_amp**2 + 1e-30) + 30 # convert to power

        line, = plt.plot(t*1e6, power_dbm, label=label)

        # Peak marker
        k = np.argmax(wave_amp)
        plt.plot(t[k]*1e6, power_dbm[k], 'o', color=line.get_color(),
                 label=f"{label} peak: |y| = {wave_amp[k]:.2f} ({power_dbm[k]:.2f} dBm)")

    plt.title(f"{name} Signal Magnitude")
    plt.xlabel("Time (us)")
    plt.ylabel("Magnitude (dBm)")
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

def plot_am_am_curve(input, outputs, gain, model_name):
    """
    Linear (|x| vs |y|) and logarithmic (dBm) AM/AM curves side by side.

    input:   PA-chain input used as the x axis for every case
    outputs: dict {label: output samples}, all drawn on the same axes
    gain:    linear gain the compression points are measured against, either
             one value for all cases or a dict {label: gain}
    """
    am_in = np.abs(input)
    in_dbm = 10*np.log10(am_in**2 + 1e-12) + 30

    fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(f"{model_name} Characteristic")

    for label, output in outputs.items():
        am_out = np.abs(output)
        out_dbm = 10*np.log10(am_out**2 + 1e-12) + 30

        ax_lin.plot(am_in, am_out, label=label)
        line, = ax_log.plot(in_dbm, out_dbm, label=label)
        case_gain = gain[label] if isinstance(gain, dict) else gain

        # P1dB: 1 dB compression point
        p1db = _compression_point_dbm(am_in, am_out, case_gain, 1.0)
        if p1db is not None:
            ax_log.plot(*p1db, 'o', color=line.get_color(), label=f"{label} P1dB ({p1db[0]:.1f}, {p1db[1]:.1f}) dBm")

        # P3dB: 3 dB compression point (standard datasheet convention, more
        # robust than the raw max sample, which just tracks the highest
        # amplitude this particular pulse happened to reach)
        p3db = _compression_point_dbm(am_in, am_out, case_gain, 3.0)
        if p3db is not None:
            ax_log.plot(*p3db, 'x', color=line.get_color(), label=f"{label} P3dB ({p3db[0]:.1f}, {p3db[1]:.1f}) dBm")
    # ax_lin.axhline(A_sat, linestyle=":", label=r"$A_{sat}$")

    ax_lin.set_xlabel("Input wave amplitude |x|")
    ax_lin.set_ylabel("Output wave amplitude |y|")
    ax_lin.set_title("Linear")
    ax_lin.grid(True)
    ax_lin.legend()

    ax_log.set_xlabel("Input power (dBm)")
    ax_log.set_ylabel("Output power (dBm)")
    ax_log.set_title("Logarithmic")
    ax_log.grid(True)
    ax_log.legend()

    fig.tight_layout()
    plt.show()

def plot_am_pm_curve(input, outputs, model_name):
    """
    AM/PM curves against linear input amplitude and against input power (dBm)
    side by side.

    input:   PA-chain input used as the x axis and phase reference for every case
    outputs: dict {label: output samples}, all drawn on the same axes
    """
    am_in = np.abs(input)
    in_dbm = 10*np.log10(am_in**2 + 1e-12) + 30

    fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(f"{model_name} Curve")

    for label, output in outputs.items():
        # Phase difference
        phase_in = np.angle(input)
        phase_out = np.angle(output)
        am_pm = np.degrees(np.angle(np.exp(1j * (phase_out - phase_in))))

        ax_lin.plot(am_in, am_pm, '.', markersize=2, label=label)
        ax_log.plot(in_dbm, am_pm, '.', markersize=2, label=label)

    ax_lin.set_xlabel("Input wave amplitude |x|")
    ax_lin.set_ylabel("Phase distortion (deg)")
    ax_lin.set_title("Linear")
    ax_lin.grid(True)
    ax_lin.legend(markerscale=5)

    ax_log.set_xlabel("Input power (dBm)")
    ax_log.set_ylabel("Phase distortion (deg)")
    ax_log.set_title("Logarithmic")
    ax_log.grid(True)
    ax_log.legend(markerscale=5)

    fig.tight_layout()
    plt.show()

def plot_pulse_compression(outputs, fs, name):
    """
    outputs: dict {label: pulse compression output}, all drawn on the same axes
    """
    fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle(f"{name} Pulse Compression Output")

    for label, y in outputs.items():
        t_mf = np.arange(len(y)) / fs # time axis
        power = np.abs(y)**2
        power_dbm = 10 * np.log10(power + 1e-30) + 30

        ax_lin.plot(t_mf*1e6, power, label=label)
        ax_log.plot(t_mf*1e6, power_dbm, label=label)

    ax_lin.set_ylabel("Power (W)")
    ax_lin.set_title("Linear")
    ax_lin.set_xlabel("Time (us)")
    ax_lin.grid(True)
    ax_lin.legend()

    ax_log.set_ylabel("Power (dBm)")
    ax_log.set_title("Logarithmic")
    ax_log.set_xlabel("Time (us)")
    ax_log.grid(True)
    ax_log.legend()

    fig.tight_layout()
    plt.show()