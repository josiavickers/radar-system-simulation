import os
from datetime import datetime
import numpy as np

CASES = ["Ideal", "Nonlinear", "Predistorted"]

def spectrum_kpis(f, power_dbm, band_low, band_high):
    '''
    KPIs of a power spectrum, with the mainlobe defined as the chirp band
    [band_low, band_high] and everything else in the spectrum as sidelobes.

    peak_dbm - highest bin inside the band (dBm)
    psl_db   - highest bin outside the band relative to the mainlobe peak (dB)
    isl_db   - out-of-band power relative to in-band power (dB)
    '''
    in_band = (f >= band_low) & (f <= band_high)
    power_w = 10**(power_dbm / 10) # linear power per bin

    peak_dbm = np.max(power_dbm[in_band])
    psl_db = np.max(power_dbm[~in_band]) - peak_dbm
    isl_db = 10 * np.log10(np.sum(power_w[~in_band]) / np.sum(power_w[in_band]))

    return {"peak_dbm": peak_dbm, "psl_db": psl_db, "isl_db": isl_db}

def compression_kpis(y):
    '''
    KPIs of a pulse compression output y, with the mainlobe running from the
    peak out to the first null (local minimum) on each side.

    peak_dbm - mainlobe peak power (dBm)
    psl_db   - highest sample outside the mainlobe relative to the peak (dB)
    isl_db   - sidelobe energy relative to mainlobe energy (dB)
    '''
    power = np.abs(y)**2
    k = np.argmax(power)

    # Walk outwards from the peak to the first null on each side
    left = k
    while left > 0 and power[left - 1] < power[left]:
        left -= 1
    right = k
    while right < len(power) - 1 and power[right + 1] < power[right]:
        right += 1

    mainlobe = np.zeros(len(power), dtype=bool)
    mainlobe[left:right + 1] = True

    peak_dbm = 10 * np.log10(power[k]) + 30
    psl_db = 10 * np.log10(np.max(power[~mainlobe]) / power[k])
    isl_db = 10 * np.log10(np.sum(power[~mainlobe]) / np.sum(power[mainlobe]))

    return {"peak_dbm": peak_dbm, "psl_db": psl_db, "isl_db": isl_db}

def phase_deviation_kpis(x, y):
    '''
    Total phase deviation of an AM-PM curve: the peak-to-peak spread of the
    phase of the output y relative to the input x, as drawn in the AM-PM plot.
    A constant phase offset does not distort the pulse and is not counted.

    pp_deg - max(phase) - min(phase) (deg)
    '''
    phase_deg = np.degrees(np.angle(y * np.conj(x)))

    return {"pp_deg": np.max(phase_deg) - np.min(phase_deg)}

SIDELOBE_ROWS =[("Mainlobe peak (dBm)", "peak_dbm"), ("PSL (dB)", "psl_db"), ("ISL (dB)", "isl_db")]
PHASE_ROWS = [("Total phase dev. (deg)", "pp_deg")]

def _kpi_table(title, results, rows):
    '''
    Formats one KPI table: one row per KPI, columns for the three cases and
    their differences.

    rows - list of (row label, KPI key in the results dicts)
    '''
    header = f"{'KPI':<22}{'Ideal':>10}{'Nonlinear':>12}{'Predistorted':>14}{'NL - Ideal':>12}{'PD - Ideal':>12}{'PD - NL':>10}"

    lines = [title, header, "-" * len(header)]
    for label, key in rows:
        ideal = results["Ideal"][key]
        nonlinear = results["Nonlinear"][key]
        predistorted = results["Predistorted"][key]
        lines.append(f"{label:<22}{ideal:>10.2f}{nonlinear:>12.2f}{predistorted:>14.2f}"
                     f"{nonlinear - ideal:>12.2f}{predistorted - ideal:>12.2f}{predistorted - nonlinear:>10.2f}")
    return lines

def write_results_log(path, header_lines, spectrum_results, compression_results, p1db_results, phase_results):
    '''
    Prints the KPI results of the three cases and saves them to a text file.

    header_lines        - list of strings describing the run (pulse, PA model, ...)
    spectrum_results    - dict {case: spectrum_kpis(...)} of the PA output spectra
    compression_results - dict {case: compression_kpis(...)} of the pulse compression outputs
    p1db_results        - dict {case: (input dBm, output dBm) or None} of the AM-AM 1 dB compression points
    phase_results       - dict {case: phase_deviation_kpis(...)} of the AM-PM curves
    '''
    lines = ["RESULTS LOG", f"Date: {datetime.now():%Y-%m-%d %H:%M:%S}"] + header_lines + [""]

    lines += _kpi_table("PA output spectrum (mainlobe = chirp band)", spectrum_results, SIDELOBE_ROWS) + [""]
    lines += _kpi_table("Pulse compression output (mainlobe = peak to first nulls)", compression_results, SIDELOBE_ROWS) + [""]

    lines.append("AM-AM 1 dB compression point (input / output)")
    for name, p1db in p1db_results.items():
        if p1db is None:
            lines.append(f"  {name:<14}not reached")
        else:
            lines.append(f"  {name:<14}{p1db[0]:.2f} dBm / {p1db[1]:.2f} dBm")

    lines.append("")
    lines += _kpi_table("AM-PM total phase deviation (relative to the original pulse)", phase_results, PHASE_ROWS)

    text = "\n".join(lines)
    print(text)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(text + "\n")
