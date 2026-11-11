import copy
from load_config import *
from signal_class import *
from signal_proc import *
from plotting import *
from plotting import _compression_point_dbm # not included in * (leading underscore)
from filter import *
from power_amp import *
from predistorter import *
from results_log import *
from scipy import signal

LNA_GAIN = 30 # dB
RX_ATTENUATION = -80 # received signal attenuation dB
SIM_FS_FACTOR = 200 # simulation rate relative to tx_sample_freq, high enough for complex RF samples
SPECTRUM_SPAN = 100e6 # spectrum plot span around each stage's nominal carrier (Hz)
LO_LEAKAGE_DBC = -22 # LO leakage relative to the pulse spectral peak (dBc), None = off

def main():
    config = load_config("config.yaml")
    print("App name:", config["app"]["name"])

    """
    Initialise parameters from config.yaml
    """
    rx_sample_freq = config["params"]["rx_sample_freq"]
    tx_sample_freq = config["params"]["tx_sample_freq"]
    sim_fs = SIM_FS_FACTOR*tx_sample_freq

    # Short Pulse S1
    s1_duration = config["pulse_shape"]["S1DurationTime"]
    s1_bandwidth = config["pulse_shape"]["S1Bandwidth"]
    s1_delay_samples = config["pulse_shape"]["S1Delay"]
    s1_amplitude = config["pulse_shape"]["S1Amplitude"]
    s1_kaiser_beta = config["pulse_shape"]["S1KaiserBeta"]

    # Medium Pulse M1
    m1_duration = config["pulse_shape"]["M1DurationTime"]
    m1_bandwidth = config["pulse_shape"]["M1Bandwidth"]
    m1_delay_samples = config["pulse_shape"]["M1Delay"]
    m1_amplitude = config["pulse_shape"]["M1Amplitude"]
    m1_kaiser_beta = config["pulse_shape"]["M1KaiserBeta"]

    # Long Pulse L1
    l1_duration = config["pulse_shape"]["L1DurationTime"]
    l1_bandwidth = config["pulse_shape"]["L1Bandwidth"]
    l1_delay_samples = config["pulse_shape"]["L1Delay"]
    l1_amplitude = config["pulse_shape"]["L1Amplitude"]
    l1_kaiser_beta = config["pulse_shape"]["L1KaiserBeta"]

    # IF params
    if_freq_s1 = config["xband"]["if_conversion"]["if_freq_short_pulse"]
    if_freq_m1 = config["xband"]["if_conversion"]["if_freq_medium_pulse"]
    if_freq_l1 = config["xband"]["if_conversion"]["if_freq_long_pulse"]

    # RF params
    rf_freq_0 = config["xband"]["rf_conversion"]["rf_freq_channel_0"]

    '''
    S1 Short Pulse
    '''
    # # S1 BB signal
    # s1 = Pulse(tx_sample_freq,0,s1_duration,s1_amplitude,s1_bandwidth,"S1")
    # s1_t_samples, s1_t = s1.get_time_samples()

    # plot_time_signal(s1_t_samples, s1_t,"S1")

    '''
    Pulse selection
    '''
    pulse_name = "L1" 
    if pulse_name == "M1":
        duration = m1_duration
        bandwidth = m1_bandwidth
        delay_samples = m1_delay_samples
        amplitude = m1_amplitude
        kaiser_beta = m1_kaiser_beta
        if_freq = if_freq_m1
    elif pulse_name == "L1":
        duration = l1_duration
        bandwidth = l1_bandwidth
        delay_samples = l1_delay_samples
        amplitude = l1_amplitude
        kaiser_beta = l1_kaiser_beta
        if_freq = if_freq_l1

    '''
    Power amplifier model selection
    '''
    g = 1.0

    pa_model = 1
    if pa_model == 1:
        model_name = "Rapp"
    elif pa_model == 2:
        model_name = "Modified Saleh"

    def power_amplifier(x):
        if pa_model == 1:
            return rapp_model(x, g, A_sat=6.0, p=3)
        elif pa_model == 2:
            return modified_saleh_model(x, g, alpha_a=1.0, beta_a=1/36, nu_a=0.5, alpha_phi=0.02, beta_phi=0.04)

    def ideal_amplifier(x):
        return g * x # ideal linear amplifier

    '''
    Selected pulse
    '''
    tx_spectrum_groups = []

    # BB signal
    tx_pulse = Pulse(sim_fs,0,duration,amplitude,bandwidth,pulse_name)
    t_samples, t = tx_pulse.get_time_samples()
    f_samples, f = tx_pulse.get_freq_samples(SPECTRUM_SPAN)

    #plot_time_signal(t_samples, t, pulse_name)
    tx_spectrum_groups.append([(f, f_samples, pulse_name)])

    # Windowing
    tx_pulse.update_samples(apply_window(t_samples, kaiser_beta))
    t_samples, t = tx_pulse.get_time_samples()
    tx_pulse_compression_samples = t_samples.copy() # save for pulse compression
    f_samples, f = tx_pulse.get_freq_samples(SPECTRUM_SPAN)
    #plot_time_signal(t_samples, t, f"Windowed {pulse_name}")
    tx_spectrum_groups.append([(f, f_samples, f"Windowed {pulse_name}")])

    # One copy of the windowed pulse per case: ideal, nonlinear and predistorted
    cases = {
        "Ideal": copy.deepcopy(tx_pulse),
        "Nonlinear": copy.deepcopy(tx_pulse),
        "Predistorted": copy.deepcopy(tx_pulse),
    }

    # Predistortion (ILC), only for the predistorted case
    ilc_iterations = 500
    ilc_peak_fraction = 0.95 # target peak output as a fraction of the PA's maximum output
    u, G0 = get_predistorted_pulse(t_samples, power_amplifier, g, K=ilc_iterations, peak_fraction=ilc_peak_fraction)
    cases["Predistorted"].update_samples(u)

    # Linear gain of each case (predistorted: target gain G0 of predistorter + PA)
    case_gains = {"Ideal": g, "Nonlinear": g, "Predistorted": G0}

    # IF upconversion
    group = []
    for name, pulse in cases.items():
        pulse.upconversion(if_freq)
        f_samples, f = pulse.get_freq_samples(SPECTRUM_SPAN)

        if name != "Nonlinear":
            group.append((f, f_samples, f"IF {pulse_name} {name}"))
    tx_spectrum_groups.append(group)

    # RF upconversion
    group = []
    for name, pulse in cases.items():
        pulse.iq_modulator(rf_freq_0, LO_LEAKAGE_DBC)
        f_samples, f = pulse.get_freq_samples(SPECTRUM_SPAN)

        if name != "Nonlinear":
            group.append((f, f_samples, f"RF {pulse_name} {name} (pre-PA)"))
    tx_spectrum_groups.append(group)

#################################################################################################################
    # POWER AMPLIFIER MODELLING
    pa_inputs = {}
    pa_outputs = {}
    pa_spectra = {} # post-PA spectra, for the results log

    group = []
    for name, pulse in cases.items():
        pa_inputs[name] = signal.hilbert(pulse.samples) # complex envelope of the real RF signal (envelope PA models)
        amplifier = ideal_amplifier if name == "Ideal" else power_amplifier
        pa_outputs[name] = amplifier(pa_inputs[name])
        pulse.update_samples(np.real(pa_outputs[name])) # real RF signal again

        f_samples, f = pulse.get_freq_samples(SPECTRUM_SPAN)
        pa_spectra[name] = (f, f_samples)
        group.append((f, f_samples, f"PA {pulse_name} {name} (post-PA)"))
    tx_spectrum_groups.append(group)

    # Chirp band at RF (mainlobe of the spectrum KPIs)
    band_low = cases["Ideal"].fc
    band_high = cases["Ideal"].fc + bandwidth

    plot_power_spectrum_grid(tx_spectrum_groups, f"{pulse_name} TX Path Spectra ({model_name})")
    
    # Plot magnitude of transmitted signal (PA output envelope of each case)
    plot_mag_time(pa_outputs, cases["Ideal"].t, f"{pulse_name} PA Output ({model_name})")

    # AM/AM and AM/PM against the original pulse (ideal case PA input), so the
    # predistorted curve shows the predistorter + PA together
    plot_am_am_curve(pa_inputs["Ideal"], pa_outputs, case_gains, f"{model_name} AM/AM")
    plot_am_pm_curve(pa_inputs["Ideal"], pa_outputs, f"{model_name} AM/PM")
#################################################################################################################

    rx_spectrum_groups = []

    # Received signal
    group = []
    for name, pulse in cases.items():
        pulse.update_samples(apply_channel(pulse.samples,RX_ATTENUATION,delay_samples*SIM_FS_FACTOR))
        f_samples, f = pulse.get_freq_samples(SPECTRUM_SPAN)
        group.append((f, f_samples, f"Rx {pulse_name} {name}"))
    rx_spectrum_groups.append(group)

    # LNA
    group = []
    for name, pulse in cases.items():
        pulse.update_samples(linear_gain(pulse.samples,LNA_GAIN))
        f_samples, f = pulse.get_freq_samples(SPECTRUM_SPAN)
        group.append((f, f_samples, f"LNA {pulse_name} {name}"))
    rx_spectrum_groups.append(group)

    # Downconversion to IF
    group = []
    for name, pulse in cases.items():
        pulse.iq_demodulator(rf_freq_0)
        f_samples, f = pulse.get_freq_samples(SPECTRUM_SPAN)
        group.append((f, f_samples, f"IF {pulse_name} {name} before filtering"))
    rx_spectrum_groups.append(group)

    # IF Filter
    group = []
    for name, pulse in cases.items():
        pulse.update_samples(signal.sosfilt(get_if_filter_coeff(sim_fs), pulse.samples))
        f_samples, f = pulse.get_freq_samples(SPECTRUM_SPAN)
        group.append((f, f_samples, f"IF {pulse_name} {name} after filtering"))
    rx_spectrum_groups.append(group)

    # Downconversion to BB
    group = []
    for name, pulse in cases.items():
        pulse.downconversion(if_freq)
        f_samples, f = pulse.get_freq_samples(SPECTRUM_SPAN)
        group.append((f, f_samples, f"BB {pulse_name} {name}"))
    rx_spectrum_groups.append(group)

    plot_power_spectrum_grid(rx_spectrum_groups, f"{pulse_name} RX Path Spectra ({model_name})")

    # Pulse compression (matched to the original windowed pulse for every case)
    compression_outputs = {}
    for name, pulse in cases.items():
        compression_outputs[name] = pulse_compression(tx_pulse_compression_samples, pulse.samples, sim_fs, pulse_name, plot=False)
    plot_pulse_compression(compression_outputs, sim_fs, f"{pulse_name} ({model_name})")

    '''
    Results log
    '''
    spectrum_results = {}
    for name, (f, power_dbm) in pa_spectra.items():
        spectrum_results[name] = spectrum_kpis(f, power_dbm, band_low, band_high)

    compression_results = {}
    for name, y in compression_outputs.items():
        compression_results[name] = compression_kpis(y)

    p1db_results = {}
    for name in ["Nonlinear", "Predistorted"]:
        p1db_results[name] = _compression_point_dbm(np.abs(pa_inputs["Ideal"]), np.abs(pa_outputs[name]), case_gains[name], 1.0)

    phase_results = {}
    for name, output in pa_outputs.items():
        phase_results[name] = phase_deviation_kpis(pa_inputs["Ideal"], output)

    header_lines = [
        f"Pulse: {pulse_name} ({duration*1e6:.1f} us, {bandwidth/1e6:.1f} MHz, amplitude {amplitude})",
        f"PA model: {model_name}",
        f"ILC: K = {ilc_iterations}, target gain = {G0:.3f}, " +
        (f"fully linear (peak = {ilc_peak_fraction*100:.0f} % of PA max output)" if G0 < g else "clipped at PA saturation (drive limit 2x pulse peak)"),
        f"Spectrum: {SPECTRUM_SPAN/1e6:.0f} MHz span, chirp band {band_low/1e9:.4f} - {band_high/1e9:.4f} GHz",
        f"LO leakage: {LO_LEAKAGE_DBC} dBc",
    ]
    write_results_log(f"results/{pulse_name}_{model_name}_results_log.txt", header_lines,
                      spectrum_results, compression_results, p1db_results, phase_results)

if __name__ == "__main__":
    main()
