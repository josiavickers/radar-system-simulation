"""Harmonic distortion of a memoryless third-order nonlinearity.

Time-domain waveform and amplitude spectrum of

    y(t) = a1*A*cos(wt) + a2*A^2*cos^2(wt) + a3*A^3*cos^3(wt)

which expands (via the power-reduction identities) into

    y(t) = a2*A^2/2                          (DC)
         + (a1*A + 3*a3*A^3/4)*cos(wt)       (fundamental)
         + a2*A^2/2 * cos(2wt)               (2nd harmonic)
         + a3*A^3/4 * cos(3wt)               (3rd harmonic)

Each case gets its own window: the undistorted amplifier (a2 = a3 = 0) and
the distorted one. a3 is negative here, which is the physical sign for gain
compression - it subtracts from the fundamental term.
"""

import numpy as np
import matplotlib.pyplot as plt

# --- Signal and nonlinearity parameters -------------------------------------
A = 1.0         # input amplitude
F0 = 1.0        # normalised fundamental frequency [Hz]
FS = 100.0      # sample rate [Hz]
N_PERIODS = 20  # integer number of periods -> harmonics land on exact FFT bins
N_HARMONICS = 3

ALPHA_LINEAR = (1.0, 0.0, 0.0)      # (a1, a2, a3) ideal
ALPHA_DISTORTED = (1.0, 0.4, -0.3)  # (a1, a2, a3) with 2nd/3rd order terms

C_LINEAR = "#2a78d6"
C_DISTORTED = "#eb6834"


def transfer(x, alpha):
    """Apply y = a1*x + a2*x^2 + a3*x^3 to the input samples."""
    a1, a2, a3 = alpha
    return a1 * x + a2 * x**2 + a3 * x**3


def analytic_terms(alpha, amplitude=A):
    """Closed-form coefficients of eq. (harmonic_terms): DC, f0, 2f0, 3f0."""
    a1, a2, a3 = alpha
    return np.array([
        a2 * amplitude**2 / 2,                          # DC
        a1 * amplitude + 3 * a3 * amplitude**3 / 4,     # fundamental
        a2 * amplitude**2 / 2,                          # 2nd harmonic
        a3 * amplitude**3 / 4,                          # 3rd harmonic
    ])


def harmonic_amplitudes(y, fs, f0, n_harmonics=N_HARMONICS):
    """Single-sided amplitudes at DC and the first n harmonics of f0."""
    n = len(y)
    spectrum = np.abs(np.fft.rfft(y)) / n
    spectrum[1:] *= 2.0  # fold the negative frequencies onto the positive ones
    freqs = np.fft.rfftfreq(n, 1 / fs)

    wanted = f0 * np.arange(n_harmonics + 1)
    bins = [int(np.argmin(np.abs(freqs - f))) for f in wanted]
    return spectrum[bins]


def plot_case(title, alpha, color, y_limit, t, x):
    y = transfer(x, alpha)
    amplitudes = harmonic_amplitudes(y, FS, F0)

    fig, (ax_time, ax_freq) = plt.subplots(1, 2, figsize=(11, 4))
    fig.canvas.manager.set_window_title(title)

    # Two periods of the waveform; the FFT above still uses the full record.
    n_show = int(round(2 * FS / F0)) + 1
    ax_time.plot(t[:n_show] * F0, y[:n_show], color=color, linewidth=2.0)
    ax_time.set_ylim(-y_limit, y_limit)
    ax_time.set_xlabel("Time $t \\cdot f_0$ (periods)")
    ax_time.set_ylabel("Amplitude $y(t)$")

    orders = np.arange(N_HARMONICS + 1)
    ax_freq.vlines(orders, 0.0, amplitudes, color=color, linewidth=2.0)
    ax_freq.plot(orders, amplitudes, "o", color=color, markersize=8)
    ax_freq.set_xticks(orders)
    ax_freq.set_xticklabels(["$0$", "$\\omega$", "$2\\omega$", "$3\\omega$"])
    ax_freq.set_ylim(0.0, y_limit)
    ax_freq.set_xlabel("Frequency")
    ax_freq.set_ylabel("Amplitude")

    for ax in (ax_time, ax_freq):
        ax.axhline(0.0, color="#c3c2b7", linewidth=1.0)
        ax.grid(True, color="#e1e0d9", linewidth=0.8)
        ax.set_axisbelow(True)

    fig.suptitle(title)
    fig.tight_layout()
    return y, amplitudes


def main():
    n_samples = int(round(N_PERIODS * FS / F0))
    t = np.arange(n_samples) / FS
    x = A * np.cos(2 * np.pi * F0 * t)

    _, a2, a3 = ALPHA_DISTORTED
    cases = [
        ("Without harmonic distortion  ($\\alpha_2 = \\alpha_3 = 0$)",
         ALPHA_LINEAR, C_LINEAR),
        (f"With harmonic distortion  ($\\alpha_2 = {a2}$, $\\alpha_3 = {a3}$)",
         ALPHA_DISTORTED, C_DISTORTED),
    ]

    # Common limit so the two windows can be compared side by side.
    y_limit = 1.2 * max(np.max(np.abs(transfer(x, alpha)))
                        for _, alpha, _ in cases)

    for title, alpha, color in cases:
        _, amplitudes = plot_case(title, alpha, color, y_limit, t, x)
        print(f"alpha = {alpha}")
        print(f"  analytic  [DC, w, 2w, 3w] = {np.abs(analytic_terms(alpha)).round(4)}")
        print(f"  from FFT  [DC, w, 2w, 3w] = {amplitudes.round(4)}\n")

    plt.show()


if __name__ == "__main__":
    main()
