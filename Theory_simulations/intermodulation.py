"""Intermodulation products of a two-tone input, up to third order.

Two equal-amplitude tones drive the same power series used by the
harmonic-distortion script:

    x(t) = A*cos(w1 t) + A*cos(w2 t)
    y(t) = a1*x + a2*x^2 + a3*x^3

Expanding the products gives, per order:

    2nd:  DC = a2*A^2, f2-f1 and f1+f2 = a2*A^2, 2f1 and 2f2 = a2*A^2/2
    3rd:  f1 and f2 = a1*A + 9*a3*A^3/4   (self- plus cross-compression)
          2f1-f2, 2f2-f1, 2f1+f2, f1+2f2 = 3*a3*A^3/4
          3f1, 3f2 = a3*A^3/4

The 2f1-f2 and 2f2-f1 pair is what makes third order matter: unlike the
harmonics, those land right next to f1 and f2 and cannot be filtered out.

Left panel: spectrum of the two-tone input. Right panel: spectrum of the
nonlinear output, both referenced to the input tone amplitude A.
"""

import numpy as np
import matplotlib.pyplot as plt

# --- Signal and nonlinearity parameters -------------------------------------
A = 0.5           # amplitude of each input tone
F1 = 1.0          # lower tone, normalised frequency
F2 = 1.3          # upper tone
FS = 10.0         # sample rate - Nyquist above the highest 3rd-order product
N_SAMPLES = 1000  # every product lands on an exact FFT bin (bin = 0.01)

ALPHA = (1.0, 0.4, -0.3)  # (a1, a2, a3)

DB_FLOOR = -60.0  # display floor [dBc]

C_INPUT = "#2a78d6"
C_OUTPUT = "#eb6834"

# Every mixing product up to third order, in ascending frequency.
PRODUCTS = [
    (0.0, "DC"),
    (F2 - F1, "$\\omega_2-\\omega_1$"),
    (2 * F1 - F2, "$2\\omega_1-\\omega_2$"),
    (F1, "$\\omega_1$"),
    (F2, "$\\omega_2$"),
    (2 * F2 - F1, "$2\\omega_2-\\omega_1$"),
    (2 * F1, "$2\\omega_1$"),
    (F1 + F2, "$\\omega_1+\\omega_2$"),
    (2 * F2, "$2\\omega_2$"),
    (3 * F1, "$3\\omega_1$"),
    (2 * F1 + F2, "$2\\omega_1+\\omega_2$"),
    (F1 + 2 * F2, "$\\omega_1+2\\omega_2$"),
    (3 * F2, "$3\\omega_2$"),
]
PRODUCT_FREQS = np.array([f for f, _ in PRODUCTS])
PRODUCT_LABELS = [label for _, label in PRODUCTS]


def transfer(x, alpha=ALPHA):
    """Apply y = a1*x + a2*x^2 + a3*x^3 to the input samples."""
    a1, a2, a3 = alpha
    return a1 * x + a2 * x**2 + a3 * x**3


def analytic_products(alpha=ALPHA, amplitude=A):
    """Closed-form amplitude of each entry of PRODUCTS."""
    a1, a2, a3 = alpha
    second = a2 * amplitude**2
    fundamental = a1 * amplitude + 9 * a3 * amplitude**3 / 4
    imd3 = 3 * a3 * amplitude**3 / 4
    third_harmonic = a3 * amplitude**3 / 4
    return np.abs([
        second,           # DC
        second,           # f2 - f1
        imd3,             # 2f1 - f2
        fundamental,      # f1
        fundamental,      # f2
        imd3,             # 2f2 - f1
        second / 2,       # 2f1
        second,           # f1 + f2
        second / 2,       # 2f2
        third_harmonic,   # 3f1
        imd3,             # 2f1 + f2
        imd3,             # f1 + 2f2
        third_harmonic,   # 3f2
    ])


def line_amplitudes(y, fs, frequencies):
    """Single-sided amplitude of the spectrum at the given frequencies."""
    n = len(y)
    spectrum = np.abs(np.fft.rfft(y)) / n
    spectrum[1:] *= 2.0  # fold the negative frequencies onto the positive ones
    freqs = np.fft.rfftfreq(n, 1 / fs)

    bins = [int(np.argmin(np.abs(freqs - f))) for f in frequencies]
    return spectrum[bins]


def to_dbc(amplitudes, reference=A):
    """Amplitudes in dB relative to one input tone, clipped to the floor."""
    with np.errstate(divide="ignore"):
        dbc = 20 * np.log10(np.abs(amplitudes) / reference)
    return np.clip(dbc, DB_FLOOR, None)


def plot_spectrum(ax, dbc, color, title):
    visible = dbc > DB_FLOOR
    ax.vlines(PRODUCT_FREQS[visible], DB_FLOOR, dbc[visible],
              color=color, linewidth=2.0)
    ax.plot(PRODUCT_FREQS[visible], dbc[visible], "o", color=color, markersize=5)

    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Amplitude (dBc)")
    ax.set_xlim(-0.3, PRODUCT_FREQS.max() + 0.3)
    ax.set_ylim(DB_FLOOR, 6.0)
    # One tick per peak present, labelled with its mixing product. Rotated so
    # the panel stays narrow enough to fill \textwidth in the thesis.
    ax.set_xticks(PRODUCT_FREQS[visible])
    ax.set_xticklabels([label for label, shown in zip(PRODUCT_LABELS, visible) if shown],
                       rotation=90, fontsize=8)
    ax.grid(True, color="#e1e0d9", linewidth=0.8)
    ax.set_axisbelow(True)


def plot_ip3():
    """AM-AM view of the third-order intercept.

    On log-log axes the fundamental 20*log(a1*A) is a slope-1 line and the
    third-order product 20*log(3*a3*A^3/4) is a slope-3 line, so they meet
    at a single point. Extrapolating both to that crossing defines IIP3:

        a1*A = 3*|a3|*A^3/4  ->  A_IIP3 = sqrt(4*a1 / (3*|a3|))

    The real device saturates long before this level - the intercept is a
    figure of merit read off the small-signal asymptotes, not an operating
    point, which is why both lines are drawn straight all the way up.
    """
    a1, _, a3 = ALPHA
    drive_db = np.linspace(-8.0, 12.0, 400)
    a_in = 10 ** (drive_db / 20)

    fundamental_db = 20 * np.log10(a1 * a_in)
    imd3_db = 20 * np.log10(3 * abs(a3) * a_in**3 / 4)

    a_iip3 = np.sqrt(4 * a1 / (3 * abs(a3)))
    x_iip3 = 20 * np.log10(a_iip3)
    y_iip3 = 20 * np.log10(a1 * a_iip3)

    print(f"\nA_IIP3 = {a_iip3:.3f}  ->  {x_iip3:.2f} dB in, {y_iip3:.2f} dB out")

    fig, ax = plt.subplots(figsize=(6.5, 5))
    fig.canvas.manager.set_window_title("Third-order intercept")

    ax.plot(drive_db, fundamental_db, color=C_INPUT, linewidth=2.0,
            label="$20\\log(\\alpha_1 A)$")
    ax.plot(drive_db, imd3_db, color=C_OUTPUT, linewidth=2.0,
            label="$20\\log(\\frac{3}{4}\\alpha_3 A^3)$")

    y_bottom = -20.0
    ax.plot(x_iip3, y_iip3, "o", color="#0b0b0b", markersize=8, zorder=3)
    ax.annotate("IIP3", (x_iip3, y_iip3), textcoords="offset points",
                xytext=(10, -4))
    ax.vlines(x_iip3, y_bottom, y_iip3, color="#898781", linewidth=1.0,
              linestyle=":")

    ax.set_xlim(drive_db.min(), drive_db.max())
    ax.set_ylim(y_bottom, 14.0)
    ax.set_xticks([x_iip3])
    ax.set_xticklabels(["$A_{IIP3}$"])
    ax.set_yticks([])
    ax.text(1.0, -0.06, "(log scale)", transform=ax.transAxes,
            ha="right", va="top")
    ax.text(0.0, 1.02, "Output Amplitude", transform=ax.transAxes,
            ha="left", va="bottom")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, loc="upper left")

    fig.suptitle("AM-AM response and Third Intercept Point")
    fig.tight_layout()


def main():
    t = np.arange(N_SAMPLES) / FS
    x = A * (np.cos(2 * np.pi * F1 * t) + np.cos(2 * np.pi * F2 * t))
    y = transfer(x)

    input_lines = line_amplitudes(x, FS, PRODUCT_FREQS)
    output_lines = line_amplitudes(y, FS, PRODUCT_FREQS)

    print(f"alpha = {ALPHA}, A = {A}, f1 = {F1}, f2 = {F2}")
    print(f"{'product':>10}  {'analytic':>9}  {'from FFT':>9}  {'dBc':>7}")
    for label, expected, measured, level in zip(
            PRODUCT_LABELS, analytic_products(), output_lines, to_dbc(output_lines)):
        plain = label.replace("$", "").replace("\\omega", "w")
        print(f"{plain:>10}  {expected:9.4f}  {measured:9.4f}  {level:7.1f}")

    fig, (ax_in, ax_out) = plt.subplots(1, 2, figsize=(7.5, 4.5), sharey=True)
    fig.canvas.manager.set_window_title("Two-tone intermodulation")

    plot_spectrum(ax_in, to_dbc(input_lines), C_INPUT, "Two-tone input")
    plot_spectrum(ax_out, to_dbc(output_lines), C_OUTPUT, "Nonlinear output")
    ax_out.set_ylabel("")

    fig.suptitle("Two-tone intermodulation products up to third order  "
                 f"($\\alpha_2 = {ALPHA[1]}$, $\\alpha_3 = {ALPHA[2]}$)", fontsize=11)
    fig.tight_layout()

    plot_ip3()
    plt.show()


if __name__ == "__main__":
    main()
