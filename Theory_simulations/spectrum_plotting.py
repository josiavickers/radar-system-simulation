import glob
import os
import numpy as np
import matplotlib.pyplot as plt

# Folder with the measured spectrum traces (CSV: frequency_hz, level_dbm)
TRACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spectrum_trace")

# IEC 62388 (Annex B) spectrum mask
NECESSARY_BW = 5e6          # necessary bandwidth (Hz), centred on the measured pulse
PULSE_CENTRE_THRESHOLD_DB = -20 # bins within this level of the peak define the pulse centre
SKIRT_START_DBC = -40       # mask level at the start of the skirt (dBc)
SLOPE_DB_PER_DECADE = 30    # skirt roll-off per decade of offset from the carrier
SPURIOUS_FLOOR_DBC = -60    # spurious emission limit (dBc)

def load_trace(path):
    '''
    Reads a spectrum trace CSV and returns frequency (Hz) and level (dBm).
    '''
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    return data[:, 0], data[:, 1]

def pulse_centre(f, level_dbm):
    '''
    Centre frequency (Hz) of the measured pulse: power-weighted centre of the
    bins within PULSE_CENTRE_THRESHOLD_DB of the trace peak.
    '''
    main_lobe = level_dbm >= np.max(level_dbm) + PULSE_CENTRE_THRESHOLD_DB
    power_w = 10**(level_dbm[main_lobe] / 10)

    return np.sum(f[main_lobe] * power_w) / np.sum(power_w)

def spectrum_mask(f, peak_dbm, f0):
    '''
    IEC 62388 spectrum mask (dBm) at the frequencies f (Hz), relative to the
    trace peak. The necessary bandwidth is centred on the carrier f0 (Hz).
    Inside it the mask is at the carrier level (0 dBc, no limit). Outside, the
    skirt starts at -40 dBc at the band edges and falls at 30 dB per decade of
    offset from the carrier down to the -60 dBc spurious floor.
    '''
    delta0 = NECESSARY_BW / 2                # offset of the skirt start from the carrier
    delta = np.abs(f - f0)

    skirt_dbc = SKIRT_START_DBC - SLOPE_DB_PER_DECADE * np.log10(np.maximum(delta, delta0) / delta0)
    mask_dbc = np.where(delta <= delta0, 0.0, np.maximum(skirt_dbc, SPURIOUS_FLOOR_DBC))

    return peak_dbm + mask_dbc

def plot_trace(f, level_dbm, name):
    peak = np.argmax(level_dbm)
    peak_dbm = level_dbm[peak]
    f0 = pulse_centre(f, level_dbm)
    band_low, band_high = f0 - NECESSARY_BW / 2, f0 + NECESSARY_BW / 2

    plt.figure(figsize=(10, 5))
    plt.plot(f/1e9, level_dbm, label=name)
    plt.plot(f[peak]/1e9, peak_dbm, 'o', color='red',
             label=f"Peak {peak_dbm:.1f} dBm at {f[peak]/1e9:.4f} GHz")

    # Spectrum mask on a fine grid, so the steps at the band edges are vertical
    f_mask = np.linspace(f[0], f[-1], 200001)
    plt.plot(f_mask/1e9, spectrum_mask(f_mask, peak_dbm, f0), '--', color='red', label="IEC 62388 mask")

    # Necessary bandwidth centred on the pulse, and the -40 / -60 dBc reference levels
    plt.axvspan(band_low/1e9, band_high/1e9, color='green', alpha=0.15,
                label=f"Necessary bandwidth ({NECESSARY_BW/1e6:.0f} MHz, {band_low/1e9:.4f} - {band_high/1e9:.4f} GHz)")
    plt.axvline(f0/1e9, color='green', linewidth=1, label=f"Pulse centre {f0/1e9:.4f} GHz")
    plt.axhline(peak_dbm + SKIRT_START_DBC, linestyle=':', color='gray', linewidth=1,
                label=f"{SKIRT_START_DBC} dBc ({peak_dbm + SKIRT_START_DBC:.1f} dBm)")
    plt.axhline(peak_dbm + SPURIOUS_FLOOR_DBC, linestyle=':', color='black', linewidth=1,
                label=f"{SPURIOUS_FLOOR_DBC} dBc ({peak_dbm + SPURIOUS_FLOOR_DBC:.1f} dBm)")

    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Level (dBm)")
    plt.title(f"Measured Spectrum: {name}")
    plt.grid(True)
    plt.legend()
    plt.show()

for path in sorted(glob.glob(os.path.join(TRACE_DIR, "*.csv"))):
    f, level_dbm = load_trace(path)
    plot_trace(f, level_dbm, os.path.splitext(os.path.basename(path))[0])
