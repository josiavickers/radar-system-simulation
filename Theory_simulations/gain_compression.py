"""Gain compression from the third-order term of the power series.

Odd-order-only nonlinearity, i.e. the second-order term of
harmonic_distortion.py is dropped:

    y(t) = a1*A*cos(wt) + a3*A^3*cos^3(wt)
         = (a1*A + 3*a3*A^3/4)*cos(wt)      (compressed fundamental)
         + a3*A^3/4 * cos(3wt)              (3rd harmonic)

With a3 < 0 the 3*a3*A^3/4 term subtracts from the fundamental: the gain
drops as the drive level rises, which is gain compression. Because no
even-order term is present there is no DC offset and no 2nd harmonic, so
the waveform stays symmetric and the compression is visible directly as
flattened peaks.
"""

import numpy as np
import matplotlib.pyplot as plt

# Shared FFT helper - same scaling as the harmonic-distortion script.
from harmonic_distortion import harmonic_amplitudes

# --- Signal and nonlinearity parameters -------------------------------------
A = 1.0         # input amplitude
F0 = 1.0        # normalised fundamental frequency [Hz]
FS = 100.0      # sample rate [Hz]
N_PERIODS = 20  # integer number of periods -> harmonics land on exact FFT bins
N_HARMONICS = 3

ALPHA_1 = 1.0   # small-signal gain
ALPHA_3 = -0.3  # negative -> compression (positive would be gain expansion)

C_OUTPUT = "#eb6834"
C_REFERENCE = "#898781"


def transfer(x, a1=ALPHA_1, a3=ALPHA_3):
    """Apply y = a1*x + a3*x^3 to the input samples."""
    return a1 * x + a3 * x**3


def fundamental_amplitude(amplitude, a1=ALPHA_1, a3=ALPHA_3):
    """Amplitude of the cos(wt) term: a1*A + 3*a3*A^3/4."""
    return a1 * amplitude + 3 * a3 * amplitude**3 / 4


def third_harmonic_amplitude(amplitude, a3=ALPHA_3):
    """Amplitude of the cos(3wt) term: a3*A^3/4."""
    return a3 * amplitude**3 / 4


def compression_db(amplitude, a1=ALPHA_1, a3=ALPHA_3):
    """Fundamental gain relative to the small-signal gain a1, in dB."""
    return 20 * np.log10(np.abs(fundamental_amplitude(amplitude, a1, a3)) / (a1 * amplitude))


def input_1db_compression(a1=ALPHA_1, a3=ALPHA_3):
    """Input amplitude at which the fundamental gain has dropped by 1 dB."""
    # a1 + 3*a3*A^2/4 = a1 * 10^(-1/20)  ->  solve for A
    return np.sqrt(4 * a1 * (1 - 10 ** (-1 / 20)) / (3 * abs(a3)))


def fold_over_amplitude(a1=ALPHA_1, a3=ALPHA_3):
    """Input amplitude where dy/dx = 0, i.e. where the cubic model stops
    being monotonic and no longer represents a real amplifier."""
    return np.sqrt(a1 / (3 * abs(a3)))


SAT_SHARPNESS = 2.0  # knee sharpness of the schematic saturating curve


def plot_am_am():
    """Schematic AM-AM curve on log-log (dB) axes, with P1dB marked.

    Standalone illustration - it does not use the cubic model above, which
    folds over instead of saturating. The curve is a soft limiter,
    out = a / (1 + a^2p)^(1/2p) with the saturation level as the unit, so
    it follows the slope-1 ideal at low drive and flattens at high drive.
    The axes carry no values: only the shape and P1dB matter here.
    """
    p = SAT_SHARPNESS
    drive_db = np.linspace(-10.0, 8.0, 400)
    drive = 10 ** (drive_db / 20)
    output_db = 20 * np.log10(drive / (1 + drive ** (2 * p)) ** (1 / (2 * p)))

    # (10/p)*log10(1 + a^2p) = 1 dB  ->  a = (10^(p/10) - 1)^(1/2p)
    a_1db = (10 ** (p / 10) - 1) ** (1 / (2 * p))
    x_1db = 20 * np.log10(a_1db)
    y_1db = x_1db - 1.0

    fig, ax = plt.subplots(figsize=(6, 5))
    fig.canvas.manager.set_window_title("AM-AM / P1dB")

    ax.plot(drive_db, drive_db, color=C_REFERENCE, linewidth=1.5, linestyle="--",
            label="ideal (slope 1)")
    ax.plot(drive_db, output_db, color=C_OUTPUT, linewidth=2.0, label="actual")

    ax.plot(x_1db, y_1db, "o", color="#0b0b0b", markersize=8, zorder=3)
    ax.annotate("", xy=(x_1db, x_1db), xytext=(x_1db, y_1db),
                arrowprops=dict(arrowstyle="<->", color="#0b0b0b", linewidth=1.2))
    ax.annotate("1 dB", (x_1db, y_1db + 0.5), textcoords="offset points",
                xytext=(-8, 0), ha="right", va="center")
    ax.annotate("$P_{1dB}$", (x_1db, y_1db), textcoords="offset points",
                xytext=(8, -12))

    # Drop the compression point onto the input axis.
    y_bottom = -10.5
    ax.vlines(x_1db, y_bottom, y_1db, color=C_REFERENCE, linewidth=1.0,
              linestyle=":")

    ax.set_xlim(drive_db.min(), drive_db.max())
    ax.set_ylim(y_bottom, 3.0)
    ax.set_xticks([x_1db])
    ax.set_xticklabels(["$A_{in,1dB}$"])
    ax.set_yticks([])
    ax.set_xlabel("$20\\log A_{in}$")
    ax.set_ylabel("$20\\log A_{out}$")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, loc="upper left")

    fig.suptitle("AM-AM response and 1 dB compression point")
    fig.tight_layout()


def main():
    n_samples = int(round(N_PERIODS * FS / F0))
    t = np.arange(n_samples) / FS
    x = A * np.cos(2 * np.pi * F0 * t)

    y = transfer(x)
    amplitudes = harmonic_amplitudes(y, FS, F0, N_HARMONICS)

    print(f"a1 = {ALPHA_1}, a3 = {ALPHA_3}, A = {A}")
    print(f"  analytic  [DC, w, 2w, 3w] = "
          f"{np.abs([0.0, fundamental_amplitude(A), 0.0, third_harmonic_amplitude(A)]).round(4)}")
    print(f"  from FFT  [DC, w, 2w, 3w] = {amplitudes.round(4)}")
    print(f"  gain compression = {compression_db(A):+.2f} dB")
    print(f"  input 1 dB compression point = {input_1db_compression():.3f}")
    print(f"  cubic model valid up to A = {fold_over_amplitude():.3f}")

    fig, (ax_time, ax_freq) = plt.subplots(1, 2, figsize=(11, 4))
    title = (f"Gain compression from the third-order term  "
             f"($\\alpha_1 = {ALPHA_1}$, $\\alpha_3 = {ALPHA_3}$)")
    fig.canvas.manager.set_window_title("Gain compression")

    # Two periods of the waveform; the FFT above still uses the full record.
    n_show = int(round(2 * FS / F0)) + 1
    ax_time.plot(t[:n_show] * F0, ALPHA_1 * x[:n_show], color=C_REFERENCE,
                 linewidth=1.5, linestyle="--", label="linear, $\\alpha_3 = 0$")
    ax_time.plot(t[:n_show] * F0, y[:n_show], color=C_OUTPUT, linewidth=2.0,
                 label="with $\\alpha_3 x^3$")
    ax_time.set_xlabel("Time $t \\cdot f_0$ (periods)")
    ax_time.set_ylabel("Amplitude $y(t)$")
    ax_time.legend(frameon=False, loc="upper right")

    orders = np.arange(N_HARMONICS + 1)
    ax_freq.axhline(ALPHA_1 * A, color=C_REFERENCE, linewidth=1.5, linestyle="--",
                    label="linear, $\\alpha_3 = 0$")
    ax_freq.vlines(orders, 0.0, amplitudes, color=C_OUTPUT, linewidth=2.0)
    ax_freq.plot(orders, amplitudes, "o", color=C_OUTPUT, markersize=8,
                 label="with $\\alpha_3 x^3$")
    ax_freq.set_xticks(orders)
    ax_freq.set_xticklabels(["$0$", "$\\omega$", "$2\\omega$", "$3\\omega$"])
    ax_freq.set_xlabel("Frequency")
    ax_freq.set_ylabel("Amplitude")
    ax_freq.legend(frameon=False, loc="upper right")

    # Headroom above the linear reference level keeps the legends clear of it.
    y_limit = 1.45 * ALPHA_1 * A
    ax_time.set_ylim(-y_limit, y_limit)
    ax_freq.set_ylim(0.0, y_limit)
    for ax in (ax_time, ax_freq):
        ax.axhline(0.0, color="#c3c2b7", linewidth=1.0)
        ax.grid(True, color="#e1e0d9", linewidth=0.8)
        ax.set_axisbelow(True)

    fig.suptitle(title)
    fig.tight_layout()

    plot_am_am()
    plt.show()


if __name__ == "__main__":
    main()
